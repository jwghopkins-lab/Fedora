-- Fedora hunt backend v7 — run in the Supabase SQL editor of the dedicated
-- project. It CREATES objects rather than replacing them, so over an existing
-- install run app/sql/reset.sql first (destructive — read its header). To move
-- a LIVE database up a version without losing play, generate a migration
-- instead: it alters in place and keeps every team and submission.
--
-- Each clue has a TYPE (number/text), a KIND (wits/dig/ground, kept for our own
-- analysis and never shown) and an ACCEPTED SET. An empty accepted set means
-- COLLECT MODE for that clue: any answer is accepted and logged, which is how we
-- harvest field values we do not yet know. A populated set is COMPETE MODE.
--
-- Player-facing API is six functions and nothing else: join, submit, hint
-- (a SEQUENCE, released one at a time on per-hint delays and logged against the
-- team), skip, signup and leaderboard. The client no longer offers skip — the
-- hint ladder is the way past a wall — but the function stays so that runs which
-- already recorded one still render.
--
-- Security: clients hold no answers and no locked clue text; every table is
-- deny-all (RLS on, no policies, zero anon grants); per-(team,clue) advisory
-- lock plus a 15s cooldown; strike budget decides who can still win.

create table public.hunts (
  id           text primary key check (id ~ '^[a-z0-9-]{3,40}$'),
  title        text not null,
  intro        text,                             -- shown once joined, before part 1
  starts_at    timestamptz,                      -- null = open immediately
  active       boolean not null default true,
  -- total wrong guesses a team may make and still WIN; beyond it they keep
  -- playing but are marked out of the running. null = no limit.
  strike_limit int check (strike_limit > 0),
  -- how long a clue must have been open before its hint is released. Lives here
  -- rather than in the function so the client can count down to the SAME moment
  -- the server will honour; a hard-coded UI wait silently drifts from the gate.
  hint_wait_s  int not null default 300 check (hint_wait_s >= 0)
);

create table public.clues (
  hunt_id        text not null references public.hunts(id) on delete cascade,
  idx            int  not null check (idx between 1 and 99),
  qtype          text not null default 'text' check (qtype in ('text', 'number')),
  -- what the clue demands of the player; drives the UI badge
  --   wits   = think, no phone, no walking
  --   dig    = the answer is in the public record (research is expected)
  --   ground = only obtainable on site (the product's whole point)
  kind           text not null default 'ground' check (kind in ('wits', 'dig', 'ground')),
  -- accepted answers, pre-normalized (A-Z0-9). Empty + qtype='number' means
  -- ANY whole number is accepted (collect mode). Empty + 'text' = misconfig.
  answers        text[] not null default '{}',
  -- 'exact'    : the normalized guess must equal one of the accepted answers
  -- 'contains' : an accepted answer need only appear INSIDE the guess, so
  --              "the fighting temeraire" matches TEMERAIRE. Used where we care
  --              that they know the word, not that they typed it alone.
  match_mode     text not null default 'exact' check (match_mode in ('exact', 'contains')),
  clue_text      text not null check (char_length(clue_text) between 10 and 2000),
  -- Hints are an ordered list, each with its own delay in seconds measured from
  -- the moment the clue opened. They are handed out ONE AT A TIME and in order:
  -- hint 2 cannot be taken before hint 1, however long you wait. A single text
  -- column used to hold all of them at once, which meant asking for a nudge
  -- dumped the entire solution in your lap.
  hints          text[] not null default '{}',
  hint_waits     int[]  not null default '{}',
  -- shown once the clue is answered: the congratulation, the walk to the next
  -- place, and the history the clue was hanging on. A team that got here by
  -- machine still learns why the answer is the answer.
  after_text     text,
  -- null = unlimited. Set on clues where a confident wrong guess from a machine
  -- should cost something; the client warns before spending one. Each hint the
  -- team takes on that clue adds one guess back, so the ladder of hints is
  -- always a way out: with no skip button, a bare limit would be a dead end.
  guess_limit    int check (guess_limit is null or guess_limit > 0),
  unlocked_by    int[] not null default '{}',
  unlock_mode    text not null default 'any' check (unlock_mode in ('any', 'all')),
  available_from timestamptz,
  primary key (hunt_id, idx)
);

create table public.teams (
  id         uuid primary key default gen_random_uuid(),
  hunt_id    text not null references public.hunts(id) on delete cascade,
  name       text not null check (char_length(name) between 1 and 30),
  code       text not null unique check (char_length(code) between 6 and 40),
  created_at timestamptz not null default now()
);

create table public.submissions (
  id         bigint generated always as identity primary key,
  team_id    uuid not null references public.teams(id) on delete cascade,
  hunt_id    text not null,
  clue_idx   int  not null,
  guess      text not null check (char_length(guess) <= 40),
  correct    boolean not null,
  -- a skip satisfies the unlock graph without counting as solved: without it a
  -- single unanswerable clue permanently ends a team's run
  skipped    boolean not null default false,
  created_at timestamptz not null default now()
);
create index submissions_team_clue on public.submissions (team_id, clue_idx, created_at desc);

-- landing-page registrations, taken before team codes are issued
create table public.signups (
  id         bigint generated always as identity primary key,
  email      text not null check (char_length(email) between 5 and 200),
  created_at timestamptz not null default now()
);

-- a taken hint: logged and counted against the team, one row per hint. The key
-- carries hint_no because a clue hands out several, in order, and the count of
-- rows here is what tells fedora_hint which one comes next.
create table public.hints (
  team_id    uuid not null references public.teams(id) on delete cascade,
  hunt_id    text not null,
  clue_idx   int  not null,
  hint_no    int  not null check (hint_no >= 1),
  created_at timestamptz not null default now(),
  primary key (team_id, clue_idx, hint_no)
);

alter table public.hints       enable row level security;
alter table public.signups     enable row level security;
alter table public.hunts       enable row level security;
alter table public.clues       enable row level security;
alter table public.teams       enable row level security;
alter table public.submissions enable row level security;
revoke all on table public.hunts, public.clues, public.teams, public.submissions,
  public.hints, public.signups from anon, authenticated;

-- ---------------------------------------------------------------------------
-- internal helpers (not granted to anon)

create or replace function public.fedora_is_unlocked(p_team uuid, p_clue public.clues)
returns boolean language sql stable security definer set search_path = '' as $$
  select (p_clue.available_from is null or now() >= p_clue.available_from)
     and (cardinality(p_clue.unlocked_by) = 0
          or case p_clue.unlock_mode
               when 'all' then not exists (
                 select 1 from unnest(p_clue.unlocked_by) need(idx)
                 where not exists (
                   select 1 from public.submissions s
                   where s.team_id = p_team and s.clue_idx = need.idx
                     and (s.correct or s.skipped)))
               else exists (
                 select 1 from public.submissions s
                 where s.team_id = p_team and (s.correct or s.skipped)
                   and s.clue_idx = any (p_clue.unlocked_by))
             end)
$$;

-- A clue becomes available when its last-satisfied prerequisite was answered
-- (or, with no prerequisites, when the team was created). The hint timer runs
-- from that moment, so a player who never guesses still earns a hint.
create or replace function public.fedora_available_since(p_team uuid, p_clue public.clues)
returns timestamptz language sql stable security definer set search_path = '' as $$
  select coalesce(
    (select max(s.created_at) from public.submissions s
     where s.team_id = p_team and (s.correct or s.skipped)
       and s.clue_idx = any (p_clue.unlocked_by)),
    (select t.created_at from public.teams t where t.id = p_team))
$$;

create or replace function public.fedora_strikes(p_team uuid)
returns int language sql stable security definer set search_path = '' as $$
  select count(*)::int from public.submissions s
  where s.team_id = p_team and not s.correct
$$;

-- solved answers are what the TEAM submitted (in collect mode there is no
-- canonical answer — the submission IS the data being collected)
create or replace function public.fedora_state(p_team uuid, p_hunt text)
returns jsonb language sql stable security definer set search_path = '' as $$
  select jsonb_build_object(
    -- the LATEST accepted guess is shown, so a fat-fingered answer can be
    -- corrected; every attempt remains in the table as collected data
    'solved', coalesce((
       select jsonb_agg(jsonb_build_object('idx', fs.clue_idx, 'answer', fs.ans,
                                           'skipped', fs.was_skipped,
                                           -- the explainer comes back with every
                                           -- reload and on every teammate's phone,
                                           -- not just in the reply that earned it
                                           'after_text', c.after_text,
                                           'solved_at', fs.first_at)
                        order by fs.clue_idx)
       from (select s.clue_idx, min(s.created_at) as first_at,
                    (array_agg(s.guess order by s.created_at desc))[1] as ans,
                    bool_and(s.skipped) as was_skipped
             from public.submissions s
             where s.team_id = p_team and (s.correct or s.skipped)
             group by s.clue_idx) fs
       join public.clues c on c.hunt_id = p_hunt and c.idx = fs.clue_idx),
      '[]'::jsonb),
    'unlocked', coalesce((
       select jsonb_agg(jsonb_build_object('idx', c.idx, 'qtype', c.qtype,
                          'kind', c.kind, 'clue_text', c.clue_text,
                          'n_hints', cardinality(c.hints),
                          'hints_taken', k.taken,
                          -- the hints already paid for come back with the state,
                          -- so a reload restores them without another call (and
                          -- without fedora_hint's counter advancing a step)
                          'hints_shown', to_jsonb(c.hints[1:k.taken]),
                          -- null once every hint is spent; otherwise the delay
                          -- fedora_hint will actually enforce, so the client
                          -- counts down to the same instant the gate opens
                          'next_hint_wait', case when k.taken >= cardinality(c.hints)
                            then null
                            else coalesce(c.hint_waits[k.taken + 1],
                                          (select hu.hint_wait_s from public.hunts hu
                                           where hu.id = p_hunt)) end,
                          'guess_limit', case when c.guess_limit is null
                            then null else c.guess_limit + k.taken end,
                          'guesses_used', k.used,
                          'since', public.fedora_available_since(p_team, c))
                        order by c.idx)
       from public.clues c
       cross join lateral (select
         (select count(*)::int from public.hints x
          where x.team_id = p_team and x.clue_idx = c.idx) as taken,
         (select count(*)::int from public.submissions s
          where s.team_id = p_team and s.clue_idx = c.idx) as used) k
       where c.hunt_id = p_hunt
         and public.fedora_is_unlocked(p_team, c)
         and not exists (select 1 from public.submissions s
                         where s.team_id = p_team and s.clue_idx = c.idx
                           and (s.correct or s.skipped))),
      '[]'::jsonb))
$$;

-- ---------------------------------------------------------------------------
-- public API (the only three things the anon key can do)

create or replace function public.fedora_join(p_code text)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare t public.teams; h public.hunts; n int;
begin
  select * into t from public.teams
    where code = upper(regexp_replace(coalesce(p_code, ''), '\s', '', 'g'));
  if not found then return jsonb_build_object('status', 'bad_code'); end if;
  select * into h from public.hunts where id = t.hunt_id;
  if not h.active then return jsonb_build_object('status', 'inactive'); end if;
  select count(*) into n from public.clues c where c.hunt_id = h.id;
  if h.starts_at is not null and now() < h.starts_at then
    return jsonb_build_object('status', 'ok', 'team_name', t.name,
      'hunt_id', h.id, 'title', h.title, 'intro', null, 'n_clues', n,
      'starts_at', h.starts_at, 'started', false,
      'strikes', 0, 'strike_limit', h.strike_limit, 'eligible', true,
      'hint_wait_s', h.hint_wait_s,
      'solved', '[]'::jsonb, 'unlocked', '[]'::jsonb);
  end if;
  return jsonb_build_object('status', 'ok', 'team_name', t.name,
                            'hunt_id', h.id, 'title', h.title,
                            'intro', h.intro, 'n_clues', n,
                            'starts_at', h.starts_at, 'started', true,
                            'strikes', public.fedora_strikes(t.id),
                            'strike_limit', h.strike_limit,
                            'eligible', h.strike_limit is null
                              or public.fedora_strikes(t.id) <= h.strike_limit,
                            'hint_wait_s', h.hint_wait_s)
         || public.fedora_state(t.id, h.id);
end $$;

create or replace function public.fedora_submit(p_code text, p_idx int, p_guess text)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare
  t public.teams; h public.hunts; c public.clues;
  guess text; last_try timestamptz; cooldown constant interval := interval '15 seconds';
  before_unlocked int[]; is_right boolean; used int; budget int;
begin
  select * into t from public.teams
    where code = upper(regexp_replace(coalesce(p_code, ''), '\s', '', 'g'));
  if not found then return jsonb_build_object('status', 'bad_code'); end if;
  select * into h from public.hunts where id = t.hunt_id;
  if not h.active then return jsonb_build_object('status', 'inactive'); end if;
  if h.starts_at is not null and now() < h.starts_at then
    return jsonb_build_object('status', 'not_started', 'starts_at', h.starts_at);
  end if;
  select * into c from public.clues where hunt_id = h.id and idx = p_idx;
  if not found then return jsonb_build_object('status', 'no_such_clue'); end if;
  -- serialize concurrent submits for this (team, clue): cooldown is otherwise
  -- a no-op against parallel requests under READ COMMITTED
  perform pg_advisory_xact_lock(hashtext(t.id::text || ':' || p_idx::text));
  -- Re-answering: allowed while the clue is in COLLECT mode (empty accept-list),
  -- so a fat-fingered field value can be corrected — the old attempt stays in
  -- the table as data. In COMPETE mode a solved clue is final.
  if cardinality(c.answers) > 0
     and exists (select 1 from public.submissions s
                 where s.team_id = t.id and s.clue_idx = p_idx and s.correct) then
    return jsonb_build_object('status', 'already_solved');
  end if;
  if not public.fedora_is_unlocked(t.id, c) then
    return jsonb_build_object('status', 'locked');
  end if;
  -- a per-clue guess budget, enforced here and not merely warned about in the
  -- UI. Every hint taken on this clue is worth one more guess, so a team that
  -- runs out can always earn its way forward instead of hitting a wall.
  if c.guess_limit is not null then
    select count(*) into used from public.submissions s
      where s.team_id = t.id and s.clue_idx = p_idx;
    select c.guess_limit + count(*) into budget from public.hints x
      where x.team_id = t.id and x.clue_idx = p_idx;
    if used >= budget then
      return jsonb_build_object('status', 'no_guesses_left', 'guess_limit', budget,
        'hints_left', cardinality(c.hints) - (select count(*) from public.hints x
                                              where x.team_id = t.id and x.clue_idx = p_idx));
    end if;
  end if;
  select max(created_at) into last_try from public.submissions s
    where s.team_id = t.id and s.clue_idx = p_idx;
  if last_try is not null and now() - last_try < cooldown then
    return jsonb_build_object('status', 'cooldown',
      'retry_in', ceil(extract(epoch from cooldown - (now() - last_try))));
  end if;
  if c.qtype = 'number' then
    -- accept digits out of whatever they typed ("about 24" -> 24), but REFUSE
    -- anything holding two separate numbers. The old code concatenated, so
    -- "20-22" was silently stored as 2022 and "1 or 2" as 12 — corrupting the
    -- very field data collect mode exists to gather.
    if (select count(*) from regexp_matches(coalesce(p_guess, ''), '[0-9]+', 'g')) > 1 then
      return jsonb_build_object('status', 'ambiguous');
    end if;
    guess := regexp_replace(coalesce(p_guess, ''), '[^0-9]', '', 'g');
    if guess = '' then return jsonb_build_object('status', 'empty'); end if;
    guess := ltrim(guess, '0');
    if guess = '' then guess := '0'; end if;   -- "000" means zero
    guess := left(guess, 40);                  -- storable, never a CHECK 500
    if cardinality(c.answers) = 0 then
      is_right := true;    -- collect mode: ANY whole number is data
    elsif char_length(guess) > 4 then
      is_right := false;   -- compete mode: no plausible field count has 5+ digits
    else
      is_right := guess = any (c.answers);
    end if;
  else
    guess := regexp_replace(upper(coalesce(p_guess, '')), '[^A-Z0-9]', '', 'g');
    if guess = '' then return jsonb_build_object('status', 'empty'); end if;
    if char_length(guess) > 40 then guess := left(guess, 40); end if;
    -- empty accept-list = COLLECT mode for text too (an inscription we do not
    -- yet know); otherwise membership of the hidden set
    if cardinality(c.answers) = 0 then
      is_right := true;                       -- collect mode
    elsif c.match_mode = 'contains' then
      is_right := exists (select 1 from unnest(c.answers) x where guess like '%' || x || '%');
    else
      is_right := guess = any (c.answers);
    end if;
  end if;
  select array_agg(k.idx) into before_unlocked from public.clues k
    where k.hunt_id = h.id and public.fedora_is_unlocked(t.id, k);
  insert into public.submissions (team_id, hunt_id, clue_idx, guess, correct)
    values (t.id, h.id, p_idx, guess, is_right);
  if not is_right then
    return jsonb_build_object('status', 'wrong',
      'strikes', public.fedora_strikes(t.id), 'strike_limit', h.strike_limit,
      'guess_limit', budget,
      'guesses_used', (select count(*) from public.submissions s
                       where s.team_id = t.id and s.clue_idx = p_idx),
      'eligible', h.strike_limit is null
        or public.fedora_strikes(t.id) <= h.strike_limit);
  end if;
  return jsonb_build_object('status', 'correct', 'idx', p_idx, 'answer', guess,
    'after_text', c.after_text,
    'newly_unlocked', coalesce((
      select jsonb_agg(jsonb_build_object('idx', k.idx, 'qtype', k.qtype,
                                          'kind', k.kind, 'clue_text', k.clue_text,
                                          'n_hints', cardinality(k.hints),
                                          'hints_taken', 0,
                                          'hints_shown', '[]'::jsonb,
                                          'next_hint_wait', case when cardinality(k.hints) = 0 then null
                                             else coalesce(k.hint_waits[1], h.hint_wait_s) end,
                                          'guess_limit', k.guess_limit,
                                          'guesses_used', 0,
                                          'since', public.fedora_available_since(t.id, k))
                       order by k.idx)
      from public.clues k
      where k.hunt_id = h.id and public.fedora_is_unlocked(t.id, k)
        and k.idx <> p_idx and not k.idx = any (coalesce(before_unlocked, '{}'))),
      '[]'::jsonb));
end $$;

-- Escape hatch. Without this, one unanswerable clue permanently ends a run:
-- the chain is linear and a team standing at the wrong railing in the rain has
-- no way forward. A skip unlocks what follows, is logged and flagged (so the
-- organiser sees exactly which clue defeated people — valuable data), costs no
-- strike, and does not count as solved on the leaderboard.
create or replace function public.fedora_skip(p_code text, p_idx int, p_note text)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare
  t public.teams; h public.hunts; c public.clues; before_unlocked int[]; note text;
begin
  select * into t from public.teams
    where code = upper(regexp_replace(coalesce(p_code, ''), '\s', '', 'g'));
  if not found then return jsonb_build_object('status', 'bad_code'); end if;
  select * into h from public.hunts where id = t.hunt_id;
  if not h.active then return jsonb_build_object('status', 'inactive'); end if;
  if h.starts_at is not null and now() < h.starts_at then
    return jsonb_build_object('status', 'not_started');
  end if;
  select * into c from public.clues where hunt_id = h.id and idx = p_idx;
  if not found then return jsonb_build_object('status', 'no_such_clue'); end if;
  perform pg_advisory_xact_lock(hashtext(t.id::text || ':' || p_idx::text));
  if not public.fedora_is_unlocked(t.id, c) then
    return jsonb_build_object('status', 'locked');
  end if;
  if exists (select 1 from public.submissions s
             where s.team_id = t.id and s.clue_idx = p_idx
               and (s.correct or s.skipped)) then
    return jsonb_build_object('status', 'already_done');
  end if;
  select array_agg(k.idx) into before_unlocked from public.clues k
    where k.hunt_id = h.id and public.fedora_is_unlocked(t.id, k);
  note := left(regexp_replace(upper(coalesce(p_note, 'SKIPPED')), '[^A-Z0-9 ]', '', 'g'), 40);
  if note = '' then note := 'SKIPPED'; end if;
  insert into public.submissions (team_id, hunt_id, clue_idx, guess, correct, skipped)
    values (t.id, h.id, p_idx, note, false, true);
  return jsonb_build_object('status', 'skipped', 'idx', p_idx,
    'newly_unlocked', coalesce((
      select jsonb_agg(jsonb_build_object('idx', k.idx, 'qtype', k.qtype,
                                          'kind', k.kind, 'clue_text', k.clue_text,
                                          'n_hints', cardinality(k.hints),
                                          'hints_taken', 0,
                                          'hints_shown', '[]'::jsonb,
                                          'next_hint_wait', case when cardinality(k.hints) = 0 then null
                                             else coalesce(k.hint_waits[1], h.hint_wait_s) end,
                                          'guess_limit', k.guess_limit,
                                          'guesses_used', 0,
                                          'since', public.fedora_available_since(t.id, k))
                       order by k.idx)
      from public.clues k
      where k.hunt_id = h.id and public.fedora_is_unlocked(t.id, k)
        and k.idx <> p_idx and not k.idx = any (coalesce(before_unlocked, '{}'))),
      '[]'::jsonb));
end $$;

-- Hints: available hunts.hint_wait_s after the clue unlocked. The wait is
-- enforced here, not in the client, and taking one is permanent and counted.
create or replace function public.fedora_hint(p_code text, p_idx int)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare
  t public.teams; h public.hunts; c public.clues;
  since timestamptz; wait interval; n int;
begin
  select * into t from public.teams
    where code = upper(regexp_replace(coalesce(p_code, ''), '\s', '', 'g'));
  if not found then return jsonb_build_object('status', 'bad_code'); end if;
  select * into h from public.hunts where id = t.hunt_id;
  if not h.active then return jsonb_build_object('status', 'inactive'); end if;
  select * into c from public.clues where hunt_id = h.id and idx = p_idx;
  if not found then return jsonb_build_object('status', 'no_such_clue'); end if;
  if not public.fedora_is_unlocked(t.id, c) then
    return jsonb_build_object('status', 'locked');
  end if;
  if cardinality(c.hints) = 0 then return jsonb_build_object('status', 'no_hint'); end if;
  -- the next one in sequence, never a later one first
  select count(*) + 1 into n from public.hints x
    where x.team_id = t.id and x.clue_idx = p_idx;
  if n > cardinality(c.hints) then
    return jsonb_build_object('status', 'exhausted',
      'hints', to_jsonb(c.hints[1:cardinality(c.hints)]));
  end if;
  wait := make_interval(secs => coalesce(c.hint_waits[n], h.hint_wait_s));
  since := public.fedora_available_since(t.id, c);
  if since is not null and now() - since < wait then
    return jsonb_build_object('status', 'too_soon',
      'wait_s', ceil(extract(epoch from wait - (now() - since))));
  end if;
  insert into public.hints (team_id, hunt_id, clue_idx, hint_no)
    values (t.id, h.id, p_idx, n) on conflict do nothing;
  -- return every hint taken so far, so a reload never loses one
  return jsonb_build_object('status', 'ok', 'idx', p_idx,
    'hints', to_jsonb(c.hints[1:n]), 'n_taken', n,
    'n_hints', cardinality(c.hints),
    -- the wait on the NEXT one, so the client can restart its countdown without
    -- a second round trip
    'next_hint_wait', case when n < cardinality(c.hints)
                      then coalesce(c.hint_waits[n + 1], h.hint_wait_s) else null end,
    'more', n < cardinality(c.hints));
end $$;

-- Write-only: an address goes in, nothing comes back out. Anon can register
-- but can never enumerate who else did.
create or replace function public.fedora_signup(p_email text)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare e text;
begin
  e := lower(btrim(coalesce(p_email, '')));
  if e !~ '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$' or char_length(e) > 200 then
    return jsonb_build_object('status', 'bad_email');
  end if;
  insert into public.signups (email) values (e);
  return jsonb_build_object('status', 'ok');
end $$;

create or replace function public.fedora_leaderboard(p_hunt text)
returns jsonb language sql stable security definer set search_path = '' as $$
  select coalesce(jsonb_agg(row order by row->'eligible' desc,
                            row->'solved' desc, row->>'last_solve' asc nulls last),
                  '[]'::jsonb)
  from (
    select jsonb_build_object('team_name', t.name,
             'solved', count(distinct s.clue_idx) filter (where s.correct),
             'skipped', count(distinct s.clue_idx) filter (where s.skipped),
             'guesses', count(s.id),
             'hints', (select count(*) from public.hints x where x.team_id = t.id),
             'eligible', h.strike_limit is null
               or count(*) filter (where not s.correct) <= h.strike_limit,
             'last_solve', max(s.created_at) filter (where s.correct)) as row
    from public.teams t
    join public.hunts h on h.id = t.hunt_id
    left join public.submissions s on s.team_id = t.id
    where t.hunt_id = p_hunt
    group by t.id, t.name, h.strike_limit) rows
$$;

revoke execute on function public.fedora_available_since(uuid, public.clues) from public, anon, authenticated;
revoke execute on function public.fedora_is_unlocked(uuid, public.clues) from public, anon, authenticated;
revoke execute on function public.fedora_state(uuid, text) from public, anon, authenticated;
revoke execute on function public.fedora_strikes(uuid) from public, anon, authenticated;
-- tighten: the RPCs are granted to anon only, never to PUBLIC
revoke execute on function public.fedora_join(text) from public;
revoke execute on function public.fedora_submit(text, int, text) from public;
revoke execute on function public.fedora_skip(text, int, text) from public;
revoke execute on function public.fedora_hint(text, int) from public;
revoke execute on function public.fedora_leaderboard(text) from public;
grant execute on function public.fedora_join(text) to anon;
grant execute on function public.fedora_submit(text, int, text) to anon;
grant execute on function public.fedora_skip(text, int, text) to anon;
grant execute on function public.fedora_hint(text, int) to anon;
grant execute on function public.fedora_leaderboard(text) to anon;
revoke execute on function public.fedora_signup(text) from public;
grant  execute on function public.fedora_signup(text) to anon;

-- Fedora hunt backend v3 — run in the Supabase SQL editor of the dedicated
-- project. v3 generalises answers: each clue has a TYPE (number/text) and an
-- ACCEPTED SET, which enables "collect mode" (accept any whole number, log
-- what players found) and "compete mode" (exact sets) with the same engine.
--
-- Security model unchanged: clients hold NO locked clue text; all access via
-- three RPCs; tables deny-all (RLS on, no policies, zero anon grants);
-- per-(team,clue) advisory lock + 15s cooldown; strike budget for the win.

create table public.hunts (
  id           text primary key check (id ~ '^[a-z0-9-]{3,40}$'),
  title        text not null,
  intro        text,                             -- shown once joined, before part 1
  starts_at    timestamptz,                      -- null = open immediately
  active       boolean not null default true,
  -- total wrong guesses a team may make and still WIN; beyond it they keep
  -- playing but are marked out of the running. null = no limit.
  strike_limit int check (strike_limit > 0)
);

create table public.clues (
  hunt_id        text not null references public.hunts(id) on delete cascade,
  idx            int  not null check (idx between 1 and 99),
  qtype          text not null default 'text' check (qtype in ('text', 'number')),
  -- accepted answers, pre-normalized (A-Z0-9). Empty + qtype='number' means
  -- ANY whole number is accepted (collect mode). Empty + 'text' = misconfig.
  answers        text[] not null default '{}',
  clue_text      text not null check (char_length(clue_text) between 10 and 2000),
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
  created_at timestamptz not null default now()
);
create index submissions_team_clue on public.submissions (team_id, clue_idx, created_at desc);

alter table public.hunts       enable row level security;
alter table public.clues       enable row level security;
alter table public.teams       enable row level security;
alter table public.submissions enable row level security;
revoke all on table public.hunts, public.clues, public.teams, public.submissions
  from anon, authenticated;

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
                   where s.team_id = p_team and s.clue_idx = need.idx and s.correct))
               else exists (
                 select 1 from public.submissions s
                 where s.team_id = p_team and s.correct
                   and s.clue_idx = any (p_clue.unlocked_by))
             end)
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
    'solved', coalesce((
       select jsonb_agg(jsonb_build_object('idx', fs.clue_idx, 'answer', fs.ans,
                                           'solved_at', fs.first_at)
                        order by fs.clue_idx)
       from (select s.clue_idx, min(s.created_at) as first_at,
                    (array_agg(s.guess order by s.created_at))[1] as ans
             from public.submissions s
             where s.team_id = p_team and s.correct group by s.clue_idx) fs
       where exists (select 1 from public.clues c
                     where c.hunt_id = p_hunt and c.idx = fs.clue_idx)),
      '[]'::jsonb),
    'unlocked', coalesce((
       select jsonb_agg(jsonb_build_object('idx', c.idx, 'qtype', c.qtype,
                                           'clue_text', c.clue_text)
                        order by c.idx)
       from public.clues c
       where c.hunt_id = p_hunt
         and public.fedora_is_unlocked(p_team, c)
         and not exists (select 1 from public.submissions s
                         where s.team_id = p_team and s.clue_idx = c.idx and s.correct)),
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
      'solved', '[]'::jsonb, 'unlocked', '[]'::jsonb);
  end if;
  return jsonb_build_object('status', 'ok', 'team_name', t.name,
                            'hunt_id', h.id, 'title', h.title,
                            'intro', h.intro, 'n_clues', n,
                            'starts_at', h.starts_at, 'started', true,
                            'strikes', public.fedora_strikes(t.id),
                            'strike_limit', h.strike_limit,
                            'eligible', h.strike_limit is null
                              or public.fedora_strikes(t.id) <= h.strike_limit)
         || public.fedora_state(t.id, h.id);
end $$;

create or replace function public.fedora_submit(p_code text, p_idx int, p_guess text)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare
  t public.teams; h public.hunts; c public.clues;
  guess text; last_try timestamptz; cooldown constant interval := interval '15 seconds';
  before_unlocked int[]; is_right boolean;
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
  if exists (select 1 from public.submissions s
             where s.team_id = t.id and s.clue_idx = p_idx and s.correct) then
    return jsonb_build_object('status', 'already_solved');
  end if;
  if not public.fedora_is_unlocked(t.id, c) then
    return jsonb_build_object('status', 'locked');
  end if;
  select max(created_at) into last_try from public.submissions s
    where s.team_id = t.id and s.clue_idx = p_idx;
  if last_try is not null and now() - last_try < cooldown then
    return jsonb_build_object('status', 'cooldown',
      'retry_in', ceil(extract(epoch from cooldown - (now() - last_try))));
  end if;
  if c.qtype = 'number' then
    -- accept digits out of whatever they typed ("about 24" -> 24)
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
    if char_length(guess) > 40 then guess := left(guess, 40); is_right := false;
    else is_right := guess = any (c.answers);
    end if;
  end if;
  select array_agg(k.idx) into before_unlocked from public.clues k
    where k.hunt_id = h.id and public.fedora_is_unlocked(t.id, k);
  insert into public.submissions (team_id, hunt_id, clue_idx, guess, correct)
    values (t.id, h.id, p_idx, guess, is_right);
  if not is_right then
    return jsonb_build_object('status', 'wrong',
      'strikes', public.fedora_strikes(t.id), 'strike_limit', h.strike_limit,
      'eligible', h.strike_limit is null
        or public.fedora_strikes(t.id) <= h.strike_limit);
  end if;
  return jsonb_build_object('status', 'correct', 'idx', p_idx, 'answer', guess,
    'newly_unlocked', coalesce((
      select jsonb_agg(jsonb_build_object('idx', k.idx, 'qtype', k.qtype,
                                          'clue_text', k.clue_text)
                       order by k.idx)
      from public.clues k
      where k.hunt_id = h.id and public.fedora_is_unlocked(t.id, k)
        and k.idx <> p_idx and not k.idx = any (coalesce(before_unlocked, '{}'))),
      '[]'::jsonb));
end $$;

create or replace function public.fedora_leaderboard(p_hunt text)
returns jsonb language sql stable security definer set search_path = '' as $$
  select coalesce(jsonb_agg(row order by row->'eligible' desc,
                            row->'solved' desc, row->>'last_solve' asc nulls last),
                  '[]'::jsonb)
  from (
    select jsonb_build_object('team_name', t.name,
             'solved', count(distinct s.clue_idx) filter (where s.correct),
             'guesses', count(s.id),
             'eligible', h.strike_limit is null
               or count(*) filter (where not s.correct) <= h.strike_limit,
             'last_solve', max(s.created_at) filter (where s.correct)) as row
    from public.teams t
    join public.hunts h on h.id = t.hunt_id
    left join public.submissions s on s.team_id = t.id
    where t.hunt_id = p_hunt
    group by t.id, t.name, h.strike_limit) rows
$$;

revoke execute on function public.fedora_is_unlocked(uuid, public.clues) from public, anon, authenticated;
revoke execute on function public.fedora_state(uuid, text) from public, anon, authenticated;
revoke execute on function public.fedora_strikes(uuid) from public, anon, authenticated;
grant execute on function public.fedora_join(text) to anon;
grant execute on function public.fedora_submit(text, int, text) to anon;
grant execute on function public.fedora_leaderboard(text) to anon;

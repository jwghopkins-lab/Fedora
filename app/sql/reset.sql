-- Fedora RESET — DESTRUCTIVE. Run this ONLY before a launch, never during one.
--
-- It removes every Fedora table and function, and with them every team, every
-- submission and every hint that has ever been recorded. There is no undo and
-- Supabase keeps no copy you can reach from the SQL editor.
--
-- Its purpose is a clean relaunch: schema.sql creates objects rather than
-- replacing them, so running it over an existing install fails on the first
-- "relation already exists". Run reset.sql, then schema.sql, then your private
-- seed_<hunt>.sql, in that order, in one paste.
--
-- To change a live hunt WITHOUT losing play data, do not come here: the private
-- seed re-inserts the hunt on its own (it deletes and recreates just that hunt),
-- and small text fixes are a manual UPDATE on public.clues.

-- Functions first. Those taking public.clues as a parameter depend on the
-- table's row type and would be dropped by the table cascade anyway; naming
-- them keeps this file honest about what exists.
drop function if exists public.fedora_leaderboard(text)                cascade;
drop function if exists public.fedora_hint(text, int)                  cascade;
drop function if exists public.fedora_skip(text, int, text)            cascade;
drop function if exists public.fedora_submit(text, int, text)          cascade;
drop function if exists public.fedora_join(text)                       cascade;
drop function if exists public.fedora_state(uuid, text)                cascade;
drop function if exists public.fedora_strikes(uuid)                    cascade;
drop function if exists public.fedora_available_since(uuid, public.clues) cascade;
drop function if exists public.fedora_is_unlocked(uuid, public.clues)  cascade;

-- Then tables, children before parents (cascade covers it either way).
drop table if exists public.hints       cascade;
drop table if exists public.submissions cascade;
drop table if exists public.teams       cascade;
drop table if exists public.clues       cascade;
drop table if exists public.hunts       cascade;

create extension if not exists pgcrypto;

create table if not exists public.channels (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  slug text not null,
  name text not null,
  config jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique(owner_id, slug)
);

create table if not exists public.topics (
  id uuid primary key default gen_random_uuid(),
  channel_id uuid not null references public.channels(id) on delete cascade,
  title text not null,
  status text not null default 'idea',
  research jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.scripts (
  id uuid primary key default gen_random_uuid(),
  topic_id uuid not null references public.topics(id) on delete cascade,
  version integer not null default 1,
  body text not null default '',
  storyboard jsonb not null default '[]'::jsonb,
  status text not null default 'draft',
  created_at timestamptz not null default now()
);

create table if not exists public.videos (
  id uuid primary key default gen_random_uuid(),
  channel_id uuid not null references public.channels(id) on delete cascade,
  script_id uuid references public.scripts(id) on delete set null,
  title text not null default '',
  asset_url text,
  status text not null default 'planned',
  scheduled_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists public.publishing_jobs (
  id uuid primary key default gen_random_uuid(),
  video_id uuid not null references public.videos(id) on delete cascade,
  platform text not null default 'youtube',
  status text not null default 'pending_approval',
  external_id text,
  created_at timestamptz not null default now()
);

alter table public.channels enable row level security;
alter table public.topics enable row level security;
alter table public.scripts enable row level security;
alter table public.videos enable row level security;
alter table public.publishing_jobs enable row level security;

create policy "owners manage channels" on public.channels for all using (owner_id = auth.uid()) with check (owner_id = auth.uid());
create policy "owners manage topics" on public.topics for all using (exists (select 1 from public.channels c where c.id = channel_id and c.owner_id = auth.uid())) with check (exists (select 1 from public.channels c where c.id = channel_id and c.owner_id = auth.uid()));
create policy "owners manage scripts" on public.scripts for all using (exists (select 1 from public.topics t join public.channels c on c.id = t.channel_id where t.id = topic_id and c.owner_id = auth.uid())) with check (exists (select 1 from public.topics t join public.channels c on c.id = t.channel_id where t.id = topic_id and c.owner_id = auth.uid()));
create policy "owners manage videos" on public.videos for all using (exists (select 1 from public.channels c where c.id = channel_id and c.owner_id = auth.uid())) with check (exists (select 1 from public.channels c where c.id = channel_id and c.owner_id = auth.uid()));
create policy "owners manage publishing jobs" on public.publishing_jobs for all using (exists (select 1 from public.videos v join public.channels c on c.id = v.channel_id where v.id = video_id and c.owner_id = auth.uid())) with check (exists (select 1 from public.videos v join public.channels c on c.id = v.channel_id where v.id = video_id and c.owner_id = auth.uid()));

grant usage on schema public to authenticated;
grant select, insert, update, delete on public.channels, public.topics, public.scripts, public.videos, public.publishing_jobs to authenticated;

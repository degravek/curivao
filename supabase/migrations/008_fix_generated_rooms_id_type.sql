-- generated_rooms was created with Supabase's default bigint id instead of uuid.
-- No data exists yet, so drop and recreate.

drop table if exists generated_rooms;

create table generated_rooms (
  id               uuid primary key default gen_random_uuid(),
  design_intent    text not null,
  dominant_style   text,
  color_palette    text[],
  selected_pieces  jsonb not null,
  image_gen_prompt text,
  image_url        text,
  published        boolean not null default false,
  created_at       timestamptz not null default now()
);

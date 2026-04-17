-- Recreate products table with correct column order.
-- Postgres does not support ALTER TABLE ... REORDER COLUMN, so this requires a
-- full table recreation. Re-ingestion is required regardless (new styles vocabulary),
-- so no data migration is needed — just drop and recreate.

drop table if exists products;

create table products (
  id               uuid primary key default gen_random_uuid(),
  created_at       timestamptz default now(),
  updated_at       timestamptz default now(),
  retailer         text not null,
  brand            text,
  name             text not null,
  sku              text,
  price            numeric,
  currency         text default 'USD',
  in_stock         boolean,
  product_url      text not null unique,
  image_url        text,
  category         text not null,
  sub_category     text,
  description      text,
  width_in         numeric,
  length_in        numeric,
  height_in        numeric,
  styles           text[],
  spatial_role     text,
  size_class       text,
  price_tier       text,
  materials        text[],
  mood             text[],
  primary_colors   text[],
  color_family     text[],
  text_embedding   vector(1536),
  image_embedding  vector(1536)
);

create index on products using ivfflat (text_embedding vector_cosine_ops)
  with (lists = 100);

create index products_styles_gin on products using gin (styles);

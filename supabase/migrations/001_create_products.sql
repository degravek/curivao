create extension if not exists vector;

create table products (
  id               uuid primary key default gen_random_uuid(),
  name             text not null,
  category         text not null,
  sub_category     text,
  retailer         text not null,
  product_url      text not null unique,
  image_url        text,
  price            numeric,
  currency         text default 'USD',
  in_stock         boolean,
  sku              text,
  style            text,
  spatial_role     text,
  size_class       text,
  price_tier       text,
  materials        text[],
  primary_colors   text[],
  mood             text[],
  color_family     text[],
  description      text,
  width_in         numeric,
  length_in        numeric,
  height_in        numeric,
  text_embedding   vector(1536),   -- text-embedding-3-small
  image_embedding  vector(1536),   -- nullable; reserved for future image embeddings
  created_at       timestamptz default now(),
  updated_at       timestamptz default now()
);

-- Approximate nearest-neighbor index for vector similarity search
create index on products using ivfflat (text_embedding vector_cosine_ops)
  with (lists = 100);

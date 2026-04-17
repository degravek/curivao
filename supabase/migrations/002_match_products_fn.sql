create or replace function match_products_by_text(
  query_embedding  vector(1536),
  filter_category  text,
  match_count      int default 10
)
returns table (
  id             bigint,
  name           text,
  category       text,
  sub_category   text,
  retailer       text,
  product_url    text,
  image_url      text,
  price          numeric,
  style          text,
  spatial_role   text,
  size_class     text,
  price_tier     text,
  materials      text[],
  primary_colors text[],
  mood           text[],
  color_family   text[],
  description    text,
  similarity     float
)
language sql stable
as $$
  select
    id, product_name as name, category, sub_category, retailer, product_url, image_url, price,
    style, spatial_role, size_class, price_tier, materials, primary_colors,
    mood, color_family, description,
    1 - (text_embedding <=> query_embedding) as similarity
  from products
  where category = filter_category
    and text_embedding is not null
  order by text_embedding <=> query_embedding
  limit match_count;
$$;

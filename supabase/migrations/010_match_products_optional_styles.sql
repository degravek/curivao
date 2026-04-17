-- Make the styles filter optional: when filter_styles is empty, skip the array overlap
-- check so callers can fall back to a pure category + vector search.

drop function if exists match_products_by_text(vector, text, text[], integer);

create or replace function match_products_by_text(
  query_embedding  vector(1536),
  filter_category  text,
  filter_styles    text[],
  match_count      int default 10
)
returns table (
  id             uuid,
  name           text,
  category       text,
  sub_category   text,
  styles         text[],
  spatial_role   text,
  size_class     text,
  price_tier     text,
  materials      text[],
  primary_colors text[],
  mood           text[],
  color_family   text[],
  description    text,
  image_url      text,
  product_url    text,
  price          numeric,
  similarity     float
)
language sql stable
as $$
  select
    id,
    name,
    category,
    sub_category,
    styles,
    spatial_role,
    size_class,
    price_tier,
    materials,
    primary_colors,
    mood,
    color_family,
    description,
    image_url,
    product_url,
    price,
    1 - (text_embedding <=> query_embedding) as similarity
  from products
  where category = filter_category
    and (filter_styles = '{}' or styles && filter_styles)
    and text_embedding is not null
  order by text_embedding <=> query_embedding
  limit match_count;
$$;

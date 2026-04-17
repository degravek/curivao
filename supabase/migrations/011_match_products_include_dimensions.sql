-- Include physical dimensions in the search results so the selection agent can
-- pass them through to the image generator. Gemini needs real-world scale to
-- avoid rendering small accents at furniture scale and vice versa.

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
  width_in       numeric,
  length_in      numeric,
  height_in      numeric,
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
    width_in,
    length_in,
    height_in,
    1 - (text_embedding <=> query_embedding) as similarity
  from products
  where category = filter_category
    and (filter_styles = '{}' or styles && filter_styles)
    and text_embedding is not null
  order by text_embedding <=> query_embedding
  limit match_count;
$$;

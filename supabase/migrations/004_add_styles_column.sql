-- Add styles text[] column to replace the deprecated style text column.
-- The old style column (6-value vocabulary) is left in place for backfill reference
-- and can be dropped after the catalog is re-ingested against the new 10-style vocabulary.

alter table products add column styles text[];

create index products_styles_gin on products using gin (styles);

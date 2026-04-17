import os
from supabase import AsyncClient, acreate_client


async def get_client() -> AsyncClient:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    return await acreate_client(url, key)


async def upsert_product(product_data: dict, table: str = "products") -> dict:
    """Insert or update a product record. Conflicts on product_url are updated in place."""
    client = await get_client()
    response = (
        await client.table(table)
        .upsert(product_data, on_conflict="product_url")
        .execute()
    )
    return response.data[0]


async def get_existing_product_urls(table: str = "products") -> set[str]:
    """Return the set of product_urls already in the given table."""
    client = await get_client()
    response = await client.table(table).select("product_url").execute()
    return {row["product_url"] for row in response.data}


async def insert_room(room_data: dict) -> dict:
    """Insert a new generated room record."""
    client = await get_client()
    response = await client.table("generated_rooms").insert(room_data).execute()
    return response.data[0]


async def list_published_rooms(limit: int = 10, offset: int = 0) -> list[dict]:
    """Return published rooms ordered newest-first, with summary fields only."""
    client = await get_client()
    response = (
        await client.table("generated_rooms")
        .select("id, design_intent, dominant_style, color_palette, image_url, created_at")
        .eq("published", True)
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response.data


async def count_published_rooms() -> int:
    """Return total count of published rooms."""
    client = await get_client()
    response = (
        await client.table("generated_rooms")
        .select("id", count="exact")
        .eq("published", True)
        .execute()
    )
    return response.count or 0


async def upload_room_image(image_bytes: bytes, filename: str) -> str:
    """Upload PNG bytes to the room-images bucket and return the public URL."""
    client = await get_client()
    bucket = "room-images"
    await client.storage.from_(bucket).upload(
        path=filename,
        file=image_bytes,
        file_options={"content-type": "image/png", "upsert": "true"},
    )
    return await client.storage.from_(bucket).get_public_url(filename)


async def update_room_image_url(room_id: str, image_url: str) -> None:
    """Update image_url for an existing room record."""
    client = await get_client()
    await (
        client.table("generated_rooms")
        .update({"image_url": image_url})
        .eq("id", room_id)
        .execute()
    )


async def get_room_by_id(room_id: str) -> dict | None:
    """Return a single room by ID, or None if not found."""
    client = await get_client()
    response = (
        await client.table("generated_rooms")
        .select("*")
        .eq("id", room_id)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else None


async def get_products_by_ids(product_ids: list[str]) -> dict[str, dict]:
    """Fetch product rows by ID and return a dict keyed by product id."""
    if not product_ids:
        return {}
    client = await get_client()
    response = (
        await client.table("products")
        .select("id, name, brand, retailer, product_url, price, currency")
        .in_("id", product_ids)
        .execute()
    )
    return {row["id"]: row for row in response.data}


async def search_products_by_text(
    embedding: list[float],
    category: str,
    styles: list[str],
    limit: int = 10,
) -> list[dict]:
    """Return the closest products in a given category and style set by cosine similarity.

    Products are hard-filtered to those whose styles array overlaps with the given styles
    list before vector similarity ranking is applied. If fewer than 3 results are returned,
    falls back to an unfiltered category search so thin-inventory styles can still fill a room.
    """
    client = await get_client()
    response = await client.rpc(
        "match_products_by_text",
        {
            "query_embedding": embedding,
            "filter_category": category,
            "filter_styles": styles,
            "match_count": limit,
        },
    ).execute()

    if len(response.data) >= 3:
        return response.data

    # Fallback: style inventory too thin — broaden to full category.
    fallback = await client.rpc(
        "match_products_by_text",
        {
            "query_embedding": embedding,
            "filter_category": category,
            "filter_styles": [],
            "match_count": limit,
        },
    ).execute()
    return fallback.data

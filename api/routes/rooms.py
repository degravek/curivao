from fastapi import APIRouter, HTTPException, Query
from services.supabase import count_published_rooms, get_products_by_ids, get_room_by_id, list_published_rooms

router = APIRouter(prefix="/api/rooms", tags=["rooms"])

VALID_LIMITS = {10, 20, 50}


@router.get("")
async def get_rooms(
    limit: int = Query(default=10, description="Items per page (10, 20, or 50)"),
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
) -> dict:
    if limit not in VALID_LIMITS:
        limit = 10
    offset = (page - 1) * limit
    rooms, total = await _fetch_rooms_and_count(limit, offset)
    return {"rooms": rooms, "total": total, "page": page, "limit": limit}


@router.get("/{room_id}")
async def get_room(room_id: str) -> dict:
    room = await get_room_by_id(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    pieces = room.get("selected_pieces") or []
    # Pieces stored by the image gen agent use "catalog_id"; selection agent uses "product_id"
    product_ids = [
        p.get("catalog_id") or p.get("product_id")
        for p in pieces
        if p.get("catalog_id") or p.get("product_id")
    ]
    product_map = await get_products_by_ids(product_ids)

    enriched_pieces = []
    for piece in pieces:
        pid = piece.get("catalog_id") or piece.get("product_id")
        product = product_map.get(pid, {})
        enriched_pieces.append({
            **piece,
            # Normalize field names so the frontend always sees product_id / product_name
            "product_id": pid,
            "product_name": piece.get("product_name") or piece.get("name"),
            "placement_note": piece.get("placement_note") or piece.get("placement"),
            "price": product.get("price"),
            "currency": product.get("currency", "USD"),
            "retailer": product.get("retailer"),
            "product_url": product.get("product_url"),
        })

    return {**room, "selected_pieces": enriched_pieces}


async def _fetch_rooms_and_count(limit: int, offset: int) -> tuple[list[dict], int]:
    import asyncio

    rooms, total = await asyncio.gather(
        list_published_rooms(limit, offset),
        count_published_rooms(),
    )
    return rooms, total

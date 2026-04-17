#!/usr/bin/env python3
"""Backfill local image paths → Supabase Storage URLs in generated_rooms.

Usage:
    uv run python scripts/backfill_images.py
"""
import asyncio
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from services.supabase import get_client, update_room_image_url, upload_room_image  # noqa: E402


async def backfill() -> None:
    client = await get_client()
    rows = (await client.table("generated_rooms").select("id, image_url").execute()).data
    local_rows = [r for r in rows if r["image_url"] and r["image_url"].startswith("/")]
    print(f"Found {len(local_rows)} row(s) with local paths")
    for row in local_rows:
        path = Path(row["image_url"])
        if not path.exists():
            print(f"  SKIP (file missing): {path}")
            continue
        filename = f"{row['id']}.png"
        print(f"  Uploading {path.name} → {filename} ...", end=" ", flush=True)
        public_url = await upload_room_image(path.read_bytes(), filename)
        await update_room_image_url(row["id"], public_url)
        print(f"done\n  {public_url}")
    print("Backfill complete.")


asyncio.run(backfill())

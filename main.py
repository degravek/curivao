from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import urlparse, urlunparse
import asyncio
import re
import shutil
import sys

from data.scrape import scrape_product_page
from agents.product_ingestion_agent import furniture_agent
from agents.embeddings import get_text_embedding
from services.supabase import upsert_product, get_existing_product_urls

TARGET_TABLE = "products"

load_dotenv(override=True)

_RETAILER_MAP = {
    "target.com": "Target",
    "crateandbarrel.com": "Crate & Barrel",
}


def _base_url(url: str) -> str:
    """Strip query string and fragment for deduplication comparison."""
    p = urlparse(url)
    return urlunparse((p.scheme, p.netloc, p.path, "", "", ""))


def _retailer_from_url(url: str) -> str:
    host = urlparse(url).hostname or ""
    for domain, name in _RETAILER_MAP.items():
        if domain in host:
            return name
    return host


def _build_product_record(extraction, product_url: str, text_embedding: list[float]) -> dict:
    """Map the FurnitureExtraction output + embedding into a flat Supabase row."""
    src = extraction.source
    dims = extraction.dimensions
    return {
        "name": src.product_name,
        "brand": src.brand,
        "retailer": _retailer_from_url(product_url),
        "category": extraction.category,
        "sub_category": extraction.sub_category,
        "product_url": src.product_url,
        "image_url": src.image_url,
        "price": src.price,
        "currency": src.currency,
        "in_stock": src.in_stock,
        "sku": src.sku,
        "styles": extraction.styles,
        "spatial_role": extraction.spatial_role,
        "size_class": extraction.size_class,
        "price_tier": extraction.price_tier,
        "materials": extraction.materials,
        "primary_colors": extraction.primary_colors,
        "mood": extraction.mood,
        "color_family": extraction.color_family,
        "description": extraction.description,
        "width_in": dims.width,
        "length_in": dims.length,
        "height_in": dims.height,
        "text_embedding": text_embedding,
    }


async def ingest(product_url: str) -> None:
    print(f"Scraping: {product_url}", flush=True)
    scraped = await scrape_product_page(product_url)

    print("Extracting structured data...", flush=True)
    for attempt in range(3):
        try:
            result = await furniture_agent(scraped)
            break
        except Exception as e:
            if "429" in str(e) and attempt < 2:
                wait = 60 * (attempt + 1)
                print(f"Rate limited — waiting {wait}s...", flush=True)
                await asyncio.sleep(wait)
            else:
                raise
    extraction = result.output

    print("Embedding description...", flush=True)
    text_embedding = await get_text_embedding(extraction.description)

    print("Upserting to Supabase...", flush=True)
    record = _build_product_record(extraction, product_url, text_embedding)
    saved = await upsert_product(record, table=TARGET_TABLE)
    print(f"Saved: {saved['id']} — {saved['name']}", flush=True)


async def main() -> None:
    urls_file = Path(__file__).parent / "data" / "product_urls.txt"
    product_urls = [
        line.strip()
        for line in urls_file.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]
    existing_urls = {_base_url(u) for u in await get_existing_product_urls(table=TARGET_TABLE)}
    print(f"Found {len(existing_urls)} already-ingested URLs — skipping.", flush=True)
    for url in product_urls:
        if _base_url(url) in existing_urls:
            print(f"Skipping (exists): {url}", flush=True)
            continue
        try:
            await ingest(url)
        except Exception as e:
            print(f"ERROR on {url}: {e}", flush=True)
        await asyncio.sleep(10)


async def test_generation(design_intent: str) -> None:
    from agents.product_selection_agent import run_selection
    from agents.image_planning_agent import run_room_generation

    print(f"Running selection for: {design_intent!r}", flush=True)
    room_selection = await run_selection(design_intent)
    print(f"\nSelected {len(room_selection.selected_pieces)} pieces:", flush=True)
    for p in room_selection.selected_pieces:
        print(f"  [{p.spatial_role}] {p.product_name}", flush=True)
    print(f"\nStyle: {room_selection.dominant_style}", flush=True)
    print(f"Palette: {room_selection.color_palette}", flush=True)

    print("\nRunning room generation...", flush=True)
    room, _ = await run_room_generation(room_selection)
    print(f"\nRoom saved: {room['id']}", flush=True)
    print(f"Image: {room['image_url']}", flush=True)


def _slugify(text: str, max_len: int = 60) -> str:
    slug = text.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug[:max_len]


async def select_and_save(design_intent: str) -> Path:
    from agents.product_selection_agent import run_selection

    print(f"Running selection for: {design_intent!r}", flush=True)
    room_selection = await run_selection(design_intent)
    print(f"\nSelected {len(room_selection.selected_pieces)} pieces:", flush=True)
    for p in room_selection.selected_pieces:
        print(f"  [{p.spatial_role}] {p.product_name}", flush=True)
    print(f"\nStyle: {room_selection.dominant_style}", flush=True)
    print(f"Palette: {room_selection.color_palette}", flush=True)

    selections_dir = Path(__file__).parent / "output" / "selections"
    selections_dir.mkdir(parents=True, exist_ok=True)
    out_path = selections_dir / f"{_slugify(design_intent)}.json"
    out_path.write_text(room_selection.model_dump_json(indent=2))
    print(f"\nSelection saved: {out_path}", flush=True)
    return out_path


async def gen_from_file(selection_path: Path) -> None:
    from agents.schemas.product_selection_agent_schema import RoomSelection
    from agents.image_planning_agent import run_room_generation

    room_selection = RoomSelection.model_validate_json(selection_path.read_text())
    print(f"Loaded selection: {room_selection.design_intent!r}", flush=True)
    print(f"  {len(room_selection.selected_pieces)} pieces, style: {room_selection.dominant_style}", flush=True)

    print("\nRunning room generation...", flush=True)
    room, debug_dir = await run_room_generation(room_selection)
    print(f"\nRoom saved: {room['id']}", flush=True)
    print(f"Image: {room['image_url']}", flush=True)

    frozen_dir = Path("frozen") / selection_path.stem
    frozen_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(debug_dir / "1_room_selection.json", frozen_dir / "1_room_selection.json")
    shutil.copy(debug_dir / "3_image_gen_plan_output.json", frozen_dir / "3_image_gen_plan_output.json")
    print(f"Frozen artifacts saved: {frozen_dir}", flush=True)


async def publish_frozen(source_dir: Path) -> None:
    """Upload a frozen image to storage and insert a generated_rooms row (published=False)."""
    import json
    from uuid import uuid4
    from agents.schemas.product_selection_agent_schema import RoomSelection
    from services.supabase import upload_room_image, insert_room

    room_selection = RoomSelection.model_validate_json(
        (source_dir / "1_room_selection.json").read_text()
    )
    # Parse as plain dict to avoid schema drift with older frozen files
    plan = json.loads((source_dir / "3_image_gen_plan_output.json").read_text())
    image_bytes = (source_dir / "5_output.png").read_bytes()

    print(f"Uploading image for: {room_selection.design_intent!r}", flush=True)
    public_url = await upload_room_image(image_bytes, f"{uuid4()}.png")

    room_data = {
        "design_intent": plan["design_intent"],
        "dominant_style": room_selection.dominant_style,
        "color_palette": room_selection.color_palette,
        "selected_pieces": plan["placements"],
        "image_gen_prompt": plan["scene_description"],
        "image_url": public_url,
        "published": False,
    }
    room = await insert_room(room_data)
    print(f"Room inserted: {room['id']} (published=False)", flush=True)
    print(f"Image URL: {public_url}", flush=True)


async def render_from_frozen(source_dir: Path, prompt_template: Path | None = None) -> None:
    """Re-run only the Gemini step using frozen artifacts from a previous run."""
    from uuid import uuid4
    from agents.schemas.product_selection_agent_schema import RoomSelection
    from agents.schemas.image_planning_agent_schema import ImageGenPlan
    from agents.image_planning_agent import run_gemini_step
    from services.image_fetch import fetch_images

    room_selection = RoomSelection.model_validate_json(
        (source_dir / "1_room_selection.json").read_text()
    )
    plan = ImageGenPlan.model_validate_json(
        (source_dir / "3_image_gen_plan_output.json").read_text()
    )
    print(f"Loaded frozen selection: {room_selection.design_intent!r}", flush=True)
    print(f"  {len(room_selection.selected_pieces)} pieces, style: {room_selection.dominant_style}", flush=True)

    run_id = uuid4()
    debug_dir = Path("output") / str(run_id)
    debug_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy(source_dir / "1_room_selection.json", debug_dir / "1_room_selection.json")
    shutil.copy(source_dir / "3_image_gen_plan_output.json", debug_dir / "3_image_gen_plan_output.json")

    pieces_with_images = [p for p in room_selection.selected_pieces if p.image_url]
    fetched = await fetch_images([p.image_url for p in pieces_with_images])  # type: ignore[arg-type]
    image_map: dict[str, tuple[bytes, str]] = {
        p.product_id: img
        for p, img in zip(pieces_with_images, fetched)
        if img is not None
    }
    prompt_override = prompt_template.read_text() if prompt_template else None
    print("\nRunning Gemini step...", flush=True)
    room_data = await run_gemini_step(room_selection, plan, debug_dir, image_map, prompt_override=prompt_override)
    print(f"Image: {room_data['image_url']}", flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else None
    if cmd == "test":
        intent = " ".join(sys.argv[2:]) or "A cozy Scandinavian living room with warm oak tones and soft neutrals"
        asyncio.run(test_generation(intent))
    elif cmd == "select":
        intent = " ".join(sys.argv[2:])
        if not intent:
            print("Usage: main.py select \"<design intent>\"")
            sys.exit(1)
        asyncio.run(select_and_save(intent))
    elif cmd == "gen":
        if len(sys.argv) < 3:
            print("Usage: main.py gen <path/to/selection.json>")
            sys.exit(1)
        asyncio.run(gen_from_file(Path(sys.argv[2])))
    elif cmd == "publish":
        if len(sys.argv) < 3:
            print("Usage: main.py publish <path/to/frozen/slug/>")
            sys.exit(1)
        asyncio.run(publish_frozen(Path(sys.argv[2])))
    elif cmd == "render":
        if len(sys.argv) < 3:
            print("Usage: main.py render <path/to/run_dir/> [<system_prompt.txt>]")
            sys.exit(1)
        template = Path(sys.argv[3]) if len(sys.argv) > 3 else None
        asyncio.run(render_from_frozen(Path(sys.argv[2]), template))
    else:
        asyncio.run(main())

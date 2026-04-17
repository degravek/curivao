import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv(override=True)

from agents.product_selection_agent import run_selection
from agents.image_planning_agent import run_room_generation

DESIGN_INTENT = "moody industrial loft with dark metals, exposed brick, and leather"


async def main() -> None:
    print(f"Selecting products for: {DESIGN_INTENT!r}")
    room_selection = await run_selection(DESIGN_INTENT)
    print(f"Selected {len(room_selection.selected_pieces)} pieces:")
    for p in room_selection.selected_pieces:
        print(f"  [{p.spatial_role}] {p.product_name} — {p.category}")

    print("\nGenerating room image...")
    room = await run_room_generation(room_selection)
    print("\nDone!")
    print(f"  Supabase row id: {room['id']}")
    print(f"  Image saved:     {room['image_url']}")


asyncio.run(main())

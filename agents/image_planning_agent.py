from pathlib import Path
from uuid import uuid4

from openai import AsyncOpenAI

from .schemas.image_planning_agent_schema import ImageGenPlan
from .schemas.product_selection_agent_schema import RoomSelection, SelectedProduct
from agents.image_generation_agent import GeminiImageGen, _PREAMBLE as _GEMINI_PREAMBLE
from services.image_fetch import fetch_images
from services.supabase import insert_room, upload_room_image

_SYSTEM_PROMPT = (
    Path(__file__).parent / "prompts" / "image_planning_agent_system_prompt.md"
).read_text()

_client = AsyncOpenAI()


async def run_image_gen_plan(
    room_selection: RoomSelection,
    debug_dir: Path | None = None,
) -> ImageGenPlan:
    content: list[dict] = [{"type": "text", "text": room_selection.model_dump_json()}]

    if debug_dir is not None:
        lines: list[str] = [f"=== SYSTEM PROMPT ===\n{_SYSTEM_PROMPT}\n\n=== USER CONTENT ===\n"]
        lines.append(room_selection.model_dump_json(indent=2))
        (debug_dir / "2_image_gen_plan_request.txt").write_text("\n".join(lines))

    response = await _client.beta.chat.completions.parse(
        model="gpt-5.4-mini",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ],
        response_format=ImageGenPlan,
        reasoning_effort="high",
    )
    plan = response.choices[0].message.parsed
    if plan is None:
        raise ValueError("Failed to parse ImageGenPlan from model response")

    if debug_dir is not None:
        (debug_dir / "3_image_gen_plan_output.json").write_text(plan.model_dump_json(indent=2))

    return plan


async def run_gemini_step(
    room_selection: RoomSelection,
    plan: ImageGenPlan,
    debug_dir: Path,
    image_map: dict[str, tuple[bytes, str]],
    prompt_override: str | None = None,
) -> dict:
    """Build prompt and pieces, call Gemini, save artifacts 4+5. Returns room_data dict."""
    scene_description = prompt_override if prompt_override is not None else plan.scene_description

    # Build pieces from plan JSON, using room_selection as ground truth for image bytes.
    # Match plan pieces to selection pieces by product_id — NOT by position, since the
    # planning agent is free to reorder pieces in its output.
    plan_by_id = {p.product_id: p for p in plan.placements}
    sel_pieces_with_images = [p for p in room_selection.selected_pieces if p.product_id in image_map]
    pieces: list[dict] = []
    for sel_piece in sel_pieces_with_images:
        img_bytes, _ = image_map[sel_piece.product_id]
        plan_piece = plan_by_id.get(sel_piece.product_id)
        label = plan_piece.generic_name if plan_piece else sel_piece.product_id
        placement = plan_piece.placement if plan_piece else sel_piece.placement_note
        pieces.append({
            "label": label,
            "dimensions": sel_piece.dimensions,
            "image_bytes": img_bytes,
            "placement": placement,
        })

    # Artifact 4: full prompt sent to Gemini, matching GeminiImageGen.generate() exactly
    piece_lines: list[str] = []
    for p in pieces:
        dims = f" | {p['dimensions']}" if p.get("dimensions") else ""
        piece_lines.append(f"\n[{p['label']}{dims}] — {p['placement']}:")
        piece_lines.append("(image)")
    gemini_debug = "\n".join([
        _GEMINI_PREAMBLE.format(scene_description=scene_description),
        *piece_lines,
    ])
    (debug_dir / "4_gemini_input.txt").write_text(gemini_debug)

    image_bytes = await GeminiImageGen().generate(scene_description, pieces)

    (debug_dir / "5_output.png").write_bytes(image_bytes)

    image_filename = f"{uuid4()}.png"
    public_url = await upload_room_image(image_bytes, image_filename)
    print(f"\n[debug] Artifacts saved to: {debug_dir}")
    print(f"[debug] Uploaded to Supabase Storage: {public_url}")

    return {
        "design_intent": plan.design_intent,
        "dominant_style": room_selection.dominant_style,
        "color_palette": room_selection.color_palette,
        "selected_pieces": [p.model_dump() for p in plan.placements],
        "image_gen_prompt": plan.scene_description,
        "image_url": public_url,
        "published": False,
    }


async def run_room_generation(room_selection: RoomSelection) -> tuple[dict, Path]:
    """Full pipeline: fetch reference images → plan environment → generate image → persist.

    Returns (room_row, debug_dir) so callers can copy artifacts from debug_dir.
    """
    run_id = uuid4()
    debug_dir = Path("output") / str(run_id)
    debug_dir.mkdir(parents=True, exist_ok=True)

    # Artifact 1: what the selection agent passed in
    (debug_dir / "1_room_selection.json").write_text(
        room_selection.model_dump_json(indent=2)
    )

    pieces_with_images = [p for p in room_selection.selected_pieces if p.image_url]
    fetched = await fetch_images([p.image_url for p in pieces_with_images])  # type: ignore[arg-type]
    image_map: dict[str, tuple[bytes, str]] = {
        p.product_id: img
        for p, img in zip(pieces_with_images, fetched)
        if img is not None
    }

    plan = await run_image_gen_plan(room_selection, debug_dir=debug_dir)

    room_data = await run_gemini_step(room_selection, plan, debug_dir, image_map)
    return await insert_room(room_data), debug_dir

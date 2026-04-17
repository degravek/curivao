# CLAUDE.md

**Curivao** — "buy this look" interior design app. An AI pipeline selects real retail products and generates a photorealistic room image. Users browse a curated feed and buy pieces directly from retailers.

**Core flow:** browse feed → click room → product list with retailer links  
**Generation flow (admin-only):** ingest product URLs → embed → Supabase → selection agent → image planning agent → Gemini image gen → publish

---

## Architecture

```
frontend/          Next.js 16 App Router — feed + room detail (Vercel)
api/               FastAPI — GET /api/rooms, GET /api/rooms/{id}
agents/            Pydantic AI pipeline agents + schemas/
services/          supabase.py (async client), image_fetch.py
data/              scrape.py (Playwright, Target-specific)
selections/        Frozen room selection JSONs (one per aesthetic)
frozen/            Persistent render inputs — 1_room_selection.json + 3_image_gen_plan_output.json per scene (not gitignored)
output/            Per-run debug artifacts (gitignored)
```

**Supabase:** `products` (metadata + pgvector embeddings) + `generated_rooms` (published feed rows)  
Frontend queries only `published = true` rows. No user-facing generation trigger.

---

## Dev Commands

```bash
uv run python main.py select "intent string"        # run selection → saves to selections/<slug>.json
uv run python main.py gen selections/<slug>.json    # full pipeline: plan + gen; saves frozen/ artifacts
uv run python main.py render frozen/<slug>/         # re-run Gemini only (skips planning agent); use for prompt testing

uv run uvicorn api.main:app --reload --port 8000  # FastAPI
cd frontend && npm run dev                         # Next.js (port 3000)
uv add <package>                                   # add Python dep
uv run playwright install chromium                 # first-time scraper setup
```

---

## Key Files

| File | Purpose |
|---|---|
| [main.py](main.py) | CLI entry point: `select`, `gen`, `render` commands |
| [agents/product_ingestion_agent.py](agents/product_ingestion_agent.py) | Extracts structured furniture data from scraped HTML |
| [agents/product_selection_agent.py](agents/product_selection_agent.py) | Vector-searches products, selects cohesive room set |
| [agents/image_planning_agent.py](agents/image_planning_agent.py) | Plans environment + layout → `ImageGenPlan`; also runs Gemini step |
| [agents/image_generation_agent.py](agents/image_generation_agent.py) | `GeminiImageGen` — calls Gemini with scene + reference images → PNG bytes |
| [agents/prompts/](agents/prompts/) | System prompts as `.md` files (never inline in Python) |
| [agents/schemas/](agents/schemas/) | Pydantic output types for each agent |
| [services/supabase.py](services/supabase.py) | Upsert products, vector search, insert/list rooms, upload images |
| [api/routes/rooms.py](api/routes/rooms.py) | `GET /api/rooms` (paginated) + `GET /api/rooms/{id}` |
| [frontend/lib/api.ts](frontend/lib/api.ts) | All frontend → backend fetches |
| [design/website_template.png](design/website_template.png) | Visual design reference |

---

## Schema Design

`FurnitureExtraction` ([agents/schemas/product_ingestion_agent_schema.py](agents/schemas/product_ingestion_agent_schema.py)) — discriminated union over 7 category models (`Seating`, `Table`, `Storage`, `Bed`, `Lighting`, `Textile`, `Accessory`), all inheriting `BaseFurniture`.

`BaseFurniture` key fields: `source: ProductSource` (brand, price, URLs, SKU), `description` (embedding-optimized), `dimensions`, `style` (one of 6 Literals), `spatial_role` (anchor/secondary/accent), `size_class`, `price_tier`, `materials`, `primary_colors`, `mood`, `color_family`.

`ImageGenPlan` ([agents/schemas/image_planning_agent_schema.py](agents/schemas/image_planning_agent_schema.py)) — `Environment` (includes `background_space`), `focal_point`, `ColorPalette` (typed `ColorRole` objects for 60/30/10 split), `list[PlacedPiece]` (spatial placement only — no appearance), `material_thread`, `scene_description`. Output schema enforced via `response_format=ImageGenPlan`; no JSON spec in the system prompt. `PlacedPiece` uses `product_id` as the join key to match against `SelectedProduct.product_id` in `run_gemini_step()`.

---

## Supabase Schema

```sql
-- products
id uuid pk, name text, category text, retailer text, product_url text unique,
image_url text, price numeric, style_tags text[], colors text[],
primary_material text, description text,
text_embedding vector(1536), image_embedding vector(512)

-- generated_rooms
id uuid pk, design_intent text, environment jsonb, selected_pieces jsonb,
color_palette jsonb, image_url text, image_gen_prompt text,
published boolean default false, created_at timestamptz
```

Vector search: `ORDER BY text_embedding <=> $2::vector LIMIT 10` (with optional style hard-filter + unfiltered fallback if < 3 results).

---

## Environment Variables

```bash
# .env
OPENAI_API_KEY=
GOOGLE_API_KEY=
EMBEDDING_MODEL=text-embedding-3-small
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=

# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Code Conventions

**Python:** Python 3.13, type hints everywhere. Pydantic models for all inter-layer data. Pydantic AI for ingestion + selection agents. Image generation uses `GeminiImageGen` (`gemini-3-pro-image-preview`) in `agents/image_generation_agent.py` — not Pydantic AI. All I/O async. No business logic in `main.py`. System prompts in `agents/prompts/` as `.md` files. Typed exceptions; no bare `except Exception`.

**TypeScript:** Next.js 16 App Router, strict TypeScript (no `any`). Tailwind CSS v4 via `@theme` in `globals.css` (no `tailwind.config.ts`). All fetches through `frontend/lib/api.ts`. No CSS modules or inline styles. `params` in dynamic routes is `Promise<{...}>` — always `await params`.

**Design:** Brand "Curivao", accent gold `#B88E2F`, hero card `#FFF3E3`, Poppins font. Feed: 2-column grid, pagination 10/20/50. Hero background = most-recently-published room image.

**API:** `GET /api/rooms?limit=10&page=1` · `GET /api/rooms/{id}`

---

## Image Generation Harness

Frozen selections live in `selections/`. Re-running `gen` against the same file produces a new image from the same product set — reliable for A/B prompt comparison.

**6 frozen aesthetics:**
1. Nordic Minimalist — pale oak, oat linen, soft whites
2. Modern Farmhouse — shiplap, natural wood, black accents
3. Eclectic Bohemian — layered textiles, jewel tones, global patterns
4. Classic American Transitional — warm greige, mixed wood tones (one product image has a stale 403 URL)
5. Refined Industrial — exposed concrete, warm leather, matte black
6. Moody Refined Industrial — dark metals, exposed brick, worn leather

**Debug artifacts** saved to `output/<run_id>/` (gitignored, ephemeral):
- `1_room_selection.json` — input `RoomSelection`
- `2_image_gen_plan_request.txt` — system prompt + user content sent to GPT
- `3_image_gen_plan_output.json` — `ImageGenPlan` from GPT
- `4_gemini_input.txt` — scene description + piece placements sent to Gemini
- `5_output.png` — generated image

**Persistent render inputs** saved to `frozen/<slug>/` (not gitignored) by `gen`:
- `1_room_selection.json` and `3_image_gen_plan_output.json` copied here after each `gen` run
- Allows `render` to re-run the Gemini step after `output/` is cleared
- To test image gen prompt changes: edit `agents/prompts/image_generation_agent_system_prompt.md`, then `render frozen/<slug>/`

`test/test_*` branches vary only image gen strategy against the same frozen JSONs — visual differences across branches are intentional.

---

## Open Design Questions

**Style-filtered product search:** Current approach hard-filters by `dominant_style`, falling back to unfiltered if < 3 results. Alternative: remove upfront style commitment; agent searches a broad candidate pool and assigns `dominant_style` post-hoc. Requires changes to `selection_schema.py` and the selection agent system prompt.

---

## Key Design Decisions — Do Not Revisit Without Discussion

- **Curated feed only** — no user-facing generation UI, no prompt inputs or style selectors
- **Pydantic AI for agents** — no LangChain, LlamaIndex, or other frameworks
- **Supabase for everything** — no separate vector DB
- **No auth** — anonymous users only
- **System prompts as `.md` files** — never inline in Python

from dataclasses import dataclass
from pathlib import Path

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModelSettings

from .schemas.product_selection_agent_schema import RoomSelection
from agents.embeddings import get_text_embedding
from services.supabase import search_products_by_text

_SYSTEM_PROMPT = (
    Path(__file__).parent / "prompts" / "selection_agent_system_prompt.md"
).read_text()


@dataclass
class SelectionDeps:
    design_embedding: list[float]


selection_agent = Agent(
    "openai:gpt-5.4-mini",
    deps_type=SelectionDeps,
    output_type=RoomSelection,
    instructions=_SYSTEM_PROMPT,
    model_settings=OpenAIModelSettings(reasoning_effort="high"),
)


@selection_agent.tool
async def search_by_category(
    ctx: RunContext[SelectionDeps], category: str, styles: list[str], limit: int = 10
) -> list[dict]:
    """Search for products in a given category filtered by style, then ranked by vector similarity.

    You MUST pass the styles argument with at least dominant_style in the list. The tool
    hard-filters to products tagged with at least one of the given styles before applying
    vector similarity — this is what prevents style drift. Do not call this tool without styles.
    """
    return await search_products_by_text(ctx.deps.design_embedding, category, styles, limit)


async def run_selection(design_intent: str) -> RoomSelection:
    embedding = await get_text_embedding(design_intent)
    result = await selection_agent.run(
        design_intent,
        deps=SelectionDeps(design_embedding=embedding),
    )
    return result.output

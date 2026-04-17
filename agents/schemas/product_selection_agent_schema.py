from __future__ import annotations
from typing import Literal, Annotated
from pydantic import BaseModel, Field


# Must match product_ingestion_agent_schema.DesignStyle exactly. Duplicated here to avoid a
# cross-module dependency at the agent boundary; keep them in sync.
DesignStyle = Literal[
    "Warm Japandi",
    "Classic American Transitional",
    "Coastal Hamptons",
    "Moody Maximalist",
    "Mediterranean Tuscan",
    "Modern Farmhouse",
    "Refined Industrial",
    "Eclectic Bohemian",
    "Nordic Minimalist",
    "Art Deco Revival",
]

RoomType = Literal[
    "living room",
    "bedroom",
    "dining room",
    "home office",
    "reading nook",
    "kitchen open-plan",
]

Setting = Literal[
    "urban loft",
    "city apartment",
    "suburban home",
    "country cottage",
    "coastal house",
    "mediterranean villa",
    "townhouse",
    "modern new-build",
]

LightQuality = Literal[
    "golden hour warm afternoon",
    "bright midday south light",
    "cool north light",
    "evening with artificial light",
    "overcast soft light",
]


class SelectedProduct(BaseModel):
    product_id: str
    product_name: str
    category: str
    spatial_role: Literal["anchor", "secondary", "accent"]
    placement_note: str = Field(
        description="Where and how this piece sits in the scene. Be specific."
    )
    image_url: str | None = None
    dimensions: str | None = Field(
        default=None,
        description=(
            'Physical dimensions as a compact string, e.g. \'32"W × 18"D × 16"H\'. '
            "Copied directly from the product search results (width_in, length_in, height_in). "
            "Leave null only if all three are missing."
        ),
    )


class RoomSelection(BaseModel):
    # COMMITTED FIRST — before any product retrieval. These constrain everything downstream.
    dominant_style: DesignStyle = Field(
        description=(
            "The single governing style for this room. Committed BEFORE retrieving any products. "
            "All selected pieces must include this style in their styles list."
        )
    )
    secondary_style: DesignStyle | None = Field(
        default=None,
        description=(
            "Optional second compatible style. Use only when the room intentionally blends two "
            "compatible aesthetics (e.g. Warm Japandi + Nordic Minimalist). Leave null for a pure single-style room. "
            "Never pair incompatible styles."
        )
    )
    forbidden_styles: list[DesignStyle] = Field(
        default_factory=list,
        description=(
            "Styles that are explicitly disqualifying for this room. The image gen agent must not "
            "drift toward any of these. Populate with any style that would clash with dominant_style."
        )
    )

    design_intent: str = Field(
        description="One-sentence governing concept for the room. Committed BEFORE retrieving products."
    )

    room_type: RoomType
    setting: Setting = Field(
        description="The kind of building/space this room exists in. Constrains the image gen agent's environment choices."
    )
    light_quality_hint: LightQuality = Field(
        description="The intended light quality. The image gen agent must honor this rather than re-deciding."
    )

    color_palette: list[str] = Field(
        description="3-5 specific colors anchoring the room (e.g. 'warm oak', 'oat linen', 'matte black')."
    )

    selected_pieces: Annotated[
        list[SelectedProduct],
        Field(min_length=5, max_length=8),
    ]

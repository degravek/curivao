from __future__ import annotations
from typing import Literal, Union, Annotated, Optional
from pydantic import BaseModel, Field


class ProductSource(BaseModel):
    brand: str = Field(
        description="Brand name as it appears on the product page (e.g. 'Crate & Barrel', 'Target')."
    )
    product_name: str = Field(
        description="Exact product name as listed on the page."
    )
    sku: Optional[str] = Field(
        default=None,
        description="Product ID or SKU if present on the page. Leave null if not found."
    )
    price: Optional[float] = Field(
        default=None,
        description="Exact listed price as a number (e.g. 299.99). Leave null if not found."
    )
    currency: str = Field(
        default="USD",
        description="ISO 4217 currency code (e.g. 'USD', 'CAD'). Default to 'USD' if not specified."
    )
    product_url: str = Field(
        description="Full URL of the product page this item was extracted from."
    )
    image_url: Optional[str] = Field(
        default=None,
        description="URL of the primary product image. Leave null if not available."
    )
    in_stock: Optional[bool] = Field(
        default=None,
        description="True if the page indicates the item is in stock, False if out of stock, null if availability is not stated."
    )


class Dimensions(BaseModel):
    width: float = Field(
        description="Width in inches. Extract from the product page if possible, otherwise estimate from visual inspection."
    )
    length: float = Field(
        description="Length/depth in inches. Extract from the product page if possible, otherwise estimate from visual inspection."
    )
    height: float = Field(
        description="Height in inches. Extract from the product page if possible, otherwise estimate from visual inspection."
    )


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


class BaseFurniture(BaseModel):
    source: ProductSource = Field(
        description="Commercial data extracted directly from the product page. Do not infer or estimate these values."
    )

    description: str = Field(
        description=(
            "A 2-3 sentence description optimized for semantic search and retrieval. "
            "Sentence 1: lead with the design style(s) and mood (e.g. 'A Refined Industrial leather sectional with a moody, sophisticated feel'). "
            "Sentence 2: describe the primary materials, construction details (tufting, nailheads, leg type, frame), and colors. "
            "Sentence 3: state the spatial role and size class (e.g. 'An anchor piece, oversized, suited for loft living rooms'). "
            "Be specific about silhouette and construction — these are the cues that distinguish, e.g., a Chesterfield from a track-arm sofa within the same color and material. "
            "Do not mention warranty, assembly, maintenance, or shipping. "
            "Do not use promotional language."
        )
    )

    dimensions: Dimensions = Field(
        description="Extract or estimate the dimensions of the piece."
    )

    # MULTIPLE SELECTION (max 2) — a piece may legitimately span at most two compatible styles.
    # Do NOT add a style speculatively. If only one style clearly applies, return only one.
    # Do NOT pair styles that are aesthetically incompatible (e.g. Refined Industrial + Coastal Hamptons).
    styles: Annotated[
        list[DesignStyle],
        Field(
            min_length=1,
            max_length=2,
            description=(
                "The design style(s) this piece belongs to. Return one style for unambiguous pieces, "
                "two only when the piece genuinely reads in both worlds (e.g. a clean oak sideboard "
                "that works in both Nordic Minimalist and Warm Japandi). Never pair incompatible styles. "
                "A Chesterfield sofa is 'Classic American Transitional', not 'Refined Industrial', "
                "even if it is brown leather. Style is determined by silhouette and construction, not material alone."
            ),
        ),
    ]

    spatial_role: Literal["anchor", "secondary", "accent"] = Field(
        description=(
            "The role this piece plays in a room composition. "
            "'anchor' = dominant, room-defining piece (e.g. sofa, dining table). "
            "'secondary' = supporting piece that complements the anchor (e.g. accent chair, coffee table). "
            "'accent' = small detail piece (e.g. pillow, vase, lamp)."
        )
    )

    size_class: Literal["small", "medium", "large", "oversized"] = Field(
        description=(
            "Normalized size of the piece relative to its category. "
            "Used for layout slot matching — prefer this over raw dimensions for retrieval."
        )
    )

    price_tier: Literal["budget", "mid", "premium"] = Field(
        description=(
            "Relative price positioning of this piece within its category. "
            "Derive from source.price if available; otherwise infer from visual cues and brand positioning."
        )
    )

    materials: list[
        Literal[
            "Solid Wood",
            "Engineered Wood",
            "Metal",
            "Glass",
            "Marble",
            "Plastic",
            "Leather",
            "Velvet",
            "Linen",
            "Ceramic",
            "Fabric",
        ]
    ] = Field(description="Select all primary materials used in this piece.")

    primary_colors: list[
        Literal[
            "Black",
            "White",
            "Grey",
            "Beige",
            "Brown",
            "Red",
            "Blue",
            "Green",
            "Yellow",
            "Natural/Wood",
            "Metallic",
        ]
    ] = Field(description="Select all dominant colors present in this piece.")

    mood: Annotated[
        list[Literal["cozy", "airy", "sophisticated", "playful", "serene", "moody", "formal"]],
        Field(
            max_length=3,
            description=(
                "Up to 3 visual moods that clearly apply. Do not select speculatively."
            ),
        ),
    ]

    color_family: list[
        Literal["neutral", "warm", "cool", "earthy", "bold"]
    ] = Field(description="Select all applicable broader color families.")


class Seating(BaseFurniture):
    category: Literal["seating"]
    sub_category: Literal[
        "sofa", "arm chair", "love seat", "recliner", "sectional", "bench", "other"
    ]


class Table(BaseFurniture):
    category: Literal["table"]
    sub_category: Literal[
        "coffee table",
        "side table",
        "console table",
        "dining table",
        "accent table",
        "nightstand",
        "other",
    ]


class Storage(BaseFurniture):
    category: Literal["storage"]
    sub_category: Literal[
        "cabinet", "bookshelf", "wardrobe", "dresser", "media console", "other"
    ]


class Bed(BaseFurniture):
    category: Literal["bed"]
    sub_category: Literal["platform", "canopy", "bunk", "day", "other"]


class Lighting(BaseFurniture):
    category: Literal["lighting"]
    sub_category: Literal[
        "floor lamp", "table lamp", "pendant", "chandelier", "sconce", "other"
    ]


class Textile(BaseFurniture):
    category: Literal["textile"]
    sub_category: Literal[
        "rug", "runner", "blanket", "pillow", "curtain", "other"
    ]


class Accessory(BaseFurniture):
    category: Literal["accessory"]
    sub_category: Literal[
        "mirror", "wall art", "sculpture", "planter", "vase", "other"
    ]


FurnitureExtraction = Annotated[
    Union[Seating, Table, Storage, Bed, Lighting, Textile, Accessory],
    Field(discriminator="category"),
]

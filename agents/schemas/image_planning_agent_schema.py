from pydantic import BaseModel, Field


class Environment(BaseModel):
    wall_treatment: str = Field(description="Wall finish type (e.g. flat painted, limewash, shiplap, exposed brick).")
    wall_color: str = Field(description="Exact wall color including tone and temperature.")
    flooring: str = Field(description="Flooring material, species, and tone (e.g. wide-plank walnut hardwood, warm medium brown).")
    architectural_features: list[str] = Field(description="Architectural details present in the scene (e.g. crown moulding, exposed beams, built-in shelving, fireplace).")
    background_space: str = Field(description="What is visible beyond the primary scene (e.g. fully enclosed, open-plan kitchen through archway, exterior view through glazing).")
    light_quality: str = Field(description="Light source, direction and quality. Must match the light_quality_hint from the input.")


class ColorRole(BaseModel):
    color: str = Field(description="The specific color, including hue, tone, and temperature.")
    applied_to: str = Field(description="The surfaces or elements that carry this color.")


class ColorPalette(BaseModel):
    dominant_60: ColorRole = Field(description="The 60% dominant color — walls, large upholstery, rug.")
    secondary_30: ColorRole = Field(description="The 30% secondary color — curtains, accent chairs, secondary surfaces.")
    accent_10: ColorRole = Field(description="The 10% accent color — cushions, vases, hardware, art.")


class PlacedPiece(BaseModel):
    product_id: str = Field(description="The product_id from the input RoomSelection JSON for this piece. MUST match exactly.")
    generic_name: str = Field(description="Short generic furniture label (e.g. 'sofa', 'accent chair', 'coffee table', 'area rug'). No brand, color, or material — appearance-free.")
    product_name: str = Field(description="Human-readable product name (copied from the input RoomSelection).")
    placement: str = Field(description="Purely spatial and relational — where the piece sits, what it faces, what it rests on, its orientation, clearances, and which other selected pieces it relates to. NO appearance description.")


class ImageGenPlan(BaseModel):
    design_intent: str = Field(description="One-sentence governing concept. Use exactly as provided in the input.")
    environment: Environment = Field(description="Full environment specification for the scene.")
    focal_point: str = Field(description="The dominant anchor of the composition — what it is and which wall it sits on.")
    color_palette: ColorPalette = Field(description="60/30/10 color distribution for the scene.")
    material_thread: str = Field(description="2–3 dominant materials echoed across furniture and environment.")
    placements: list[PlacedPiece] = Field(description="Every piece from the input RoomSelection, each with refined spatial placement.")
    scene_description: str = Field(description="Single dense prose paragraph (150–250 words) covering render style, camera, environment, light, mood, and environmental styling. Must NOT describe any selected piece's appearance or placement.")

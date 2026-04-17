import io
import uuid
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image


class ImageGenError(Exception):
    pass


_PREAMBLE = (
    Path(__file__).parent / "prompts" / "image_generation_agent_system_prompt.md"
).read_text()


class GeminiImageGen:
    def __init__(self) -> None:
        self._client = genai.Client()

    async def generate(
        self,
        scene_description: str,
        pieces: list[dict],
    ) -> bytes:
        """Generate a photorealistic room image.

        scene_description: full environment/scene context sent as the first content block.
        pieces: list of dicts with keys:
            - label (str): generic descriptor shown to Gemini (e.g. "sofa", "vase").
              Deliberately appearance-free — the reference image owns visual fidelity.
            - dimensions (str | None): real-world size, e.g. '32"W × 18"D × 16"H',
              so Gemini renders the piece at correct physical scale.
            - image_bytes (bytes): raw image data.
            - placement (str): where and how to place this piece in the scene.
        Returns PNG bytes.
        """
        contents: list = [_PREAMBLE.format(scene_description=scene_description)]

        for piece in pieces:
            dims = f" | {piece['dimensions']}" if piece.get("dimensions") else ""
            contents.append(f"\n[{piece['label']}{dims}] — {piece['placement']}:")
            contents.append(Image.open(io.BytesIO(piece["image_bytes"])))

        response = await self._client.aio.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(aspect_ratio="16:9", image_size="1K"),
            ),
        )

        for part in response.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                return part.inline_data.data

        raise ImageGenError("No image was generated")


# -- Testing helper (local save for quick visual inspection) ------------------
_OUTPUT_DIR = Path(__file__).parent.parent / "output"


def save_locally(image_bytes: bytes, filename: str | None = None) -> Path:
    """Save image bytes to output/ for development testing only."""
    _OUTPUT_DIR.mkdir(exist_ok=True)
    name = filename or f"{uuid.uuid4()}.png"
    path = _OUTPUT_DIR / name
    path.write_bytes(image_bytes)
    return path

from .schemas.product_ingestion_agent_schema import FurnitureExtraction
from pydantic_ai.messages import ImageUrl
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModelSettings


async def furniture_agent(scraped):

    USER_PROMPT = (
        f"Product URL:\n{scraped['product_url']}\n\n"
        f"Product image URL:\n{scraped['product_image_url']}\n\n"
        f"Product webpage text:\n{scraped['product_description']}"
    )

    INSTRUCTION_PROMPT = (
        "You are an expert interior design data extractor. "
        "Review the provided product details and image. "
        "Extract information about the item exactly matching the schema."
    )

    agent = Agent(
        'openai:gpt-5.4-mini',
        instructions=INSTRUCTION_PROMPT,
        output_type=FurnitureExtraction
    )

    messages = [USER_PROMPT]
    if scraped.get('product_image_url'):
        messages.append(ImageUrl(url=scraped['product_image_url']))
    result = await agent.run(messages, model_settings=OpenAIModelSettings(reasoning_effort='high'))

    return result

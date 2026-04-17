from openai import AsyncOpenAI


async def get_text_embedding(text: str) -> list[float]:
    client = AsyncOpenAI()
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding

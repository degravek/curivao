import httpx


async def fetch_images(urls: list[str]) -> list[tuple[bytes, str] | None]:
    """Fetch image URLs into memory. Returns (bytes, media_type) per URL, or None on failure.

    Failures (4xx, 5xx, network errors) are logged and returned as None so the
    caller can skip unavailable reference images without aborting the pipeline.
    No files written to disk.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    async with httpx.AsyncClient(timeout=30, headers=headers) as client:
        results: list[tuple[bytes, str] | None] = []
        for url in urls:
            try:
                r = await client.get(url, follow_redirects=True)
                r.raise_for_status()
                media_type = r.headers.get("content-type", "image/jpeg").split(";")[0].strip()
                results.append((r.content, media_type))
            except httpx.HTTPError as e:
                print(f"Warning: could not fetch reference image {url}: {e}", flush=True)
                results.append(None)
        return results

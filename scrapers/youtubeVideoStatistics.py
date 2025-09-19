"""
Async Youtube v3 API video data scraper, requires API keys.
1 clear API key will be enough for approx. 500,000 videos.
"""
import aiohttp
import asyncio
import itertools
from typing import List, Dict, Any
import logging

class YouTubeScraper:
    BASE_URL = "https://www.googleapis.com/youtube/v3/videos"

    def __init__(self, api_keys: List[str], quota_retry_wait: int = 60, max_concurrent_batches: int = 10):
        if (not api_keys):
            raise ValueError("At least one API key is required")
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        
        self.api_keys = itertools.cycle(api_keys)
        self.current_key = next(self.api_keys)
        self.quota_retry_wait = quota_retry_wait
        self.max_concurrent_batches = max_concurrent_batches

    async def _fetch_chunk(self, session: aiohttp.ClientSession, video_ids: List[str], part: str) -> List[Dict[str, Any]]:
        params = {
            "part": part,
            "id": ",".join(video_ids),
            "key": self.current_key,
        }

        while True:
            async with session.get(self.BASE_URL, params=params) as resp:
                if (resp.status == 200):
                    data = await resp.json()
                    return data.get("items", [])
                elif (resp.status in (403, 429)):
                    self.logger.info(f"Quota exhausted for key {self.current_key}, switching...")
                    self.current_key = next(self.api_keys)
                    params["key"] = self.current_key
                    await asyncio.sleep(self.quota_retry_wait)
                elif (resp.status == 404):
                    return []
                else:
                    text = await resp.text()
                    raise RuntimeError(f"Unexpected status {resp.status}: {text}")

    async def fetch_videos_stats(
        self,
        video_ids: List[str],
        batch_size: int = 50,
        part: str = "statistics"
    ) -> List[Dict[str, Any]]:
        if (batch_size > 50):
            raise ValueError("YouTube API only allows up to 50 IDs per request")

        chunks = [video_ids[i:i + batch_size] for i in range(0, len(video_ids), batch_size)]
        results: List[Dict[str, Any]] = []

        semaphore = asyncio.Semaphore(self.max_concurrent_batches)

        async with aiohttp.ClientSession() as session:

            async def sem_fetch(chunk):
                async with semaphore:
                    return await self._fetch_chunk(session, chunk, part)

            tasks = [sem_fetch(chunk) for chunk in chunks]
            all_results = await asyncio.gather(*tasks)

        for batch in all_results:
            results.extend(batch)

        return results

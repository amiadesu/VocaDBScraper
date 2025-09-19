import asyncio
import aiohttp
import math
import logging

from tqdm import tqdm

from db.db import SongRepository

class VocaDBScraper:

    def __init__(self, db_url: str, max_concurrent_batches: int = 10):
        self.sem = asyncio.Semaphore(max_concurrent_batches)
        self.db = SongRepository(db_url=db_url, echo=False)

    def gen_url(self, start: int = 0, size: int = 100):
        url = f"https://vocadb.net/api/songs?childTags=false&unifyTypesAndTags=false&childVoicebanks=false&includeMembers=true&onlyWithPvs=false&start={start}&maxResults={size}&getTotalCount=true&sort=None&preferAccurateMatches=false&fields=AdditionalNames,PVs,Artists,Bpm,Tags"
        return url

    async def gen_urls(self, start: int = 0, size: int = 100):
        first_url = self.gen_url(start, size)

        logging.debug("Getting total count...")
        async with aiohttp.ClientSession() as session:
            total_count = (await self.fetch_url(session, first_url))['totalCount']
        logging.debug(f"Total count: {total_count}")

        total_pages = math.ceil((total_count - start + 1) / size)
        urls = [self.gen_url(i * 100, 100) for i in range(total_pages + 1)]
        return urls

    async def fetch_url(self, session: aiohttp.ClientSession, url: str):
        try:
            async with session.get(url, timeout=30) as res:
                res.raise_for_status()
                return await res.json()
        except Exception as e:
            logging.error(f"[ERROR] Failed fetching {url}: {e}")
            return {"items": []}  # safe fallback

    async def process_url(self, session: aiohttp.ClientSession, url: str, pbar: tqdm = None):
        async with self.sem:
            try:
                res = (await self.fetch_url(session, url)).get("items", [])
                if (res):
                    await self.db.insert_songs(res)
                    song_urls_total = []
                    for item in res:
                        song_urls = [{
                            "pv_id": pv["id"],
                            "song_id": item["id"],
                            "url": pv["url"],
                            "service": pv["service"],
                            "published_at": pv.get("publishDate", None)
                        } for pv in item["pvs"]]
                        if (song_urls):
                            song_urls_total.extend(song_urls)
                    if (song_urls_total):
                        await self.db.insert_song_urls(song_urls_total)
            except Exception as e:
                logging.error(f"[ERROR] Processing {url} failed: {e}")
            finally:
                if (pbar is not None):
                    pbar.update(1)  # always advance progress bar

    async def run(self, pbar: tqdm = None):
        urls = await self.gen_urls(0, 100)

        if (pbar is not None):
            pbar.total = len(urls)

        await self.db.init_models()

        logging.debug("Starting fetching songs...")
        async with aiohttp.ClientSession() as session:
            tasks = [
                asyncio.create_task(self.process_url(session, url, pbar))
                for url in urls
            ]
            await asyncio.gather(*tasks)

        logging.debug("Fetching completed!")
"""
Use this ONLY if you do not have API keys for corresponding resources!
These approaches can be really easily blocked and are just not reliable.
"""
import aiohttp

# --- Async HTTP helpers ---
async def fetch_text(url: str, session: aiohttp.ClientSession, **kwargs) -> str:        
    async with session.get(url, **kwargs) as resp:
        return await resp.text()

async def fetch_json(url: str, session: aiohttp.ClientSession, **kwargs) -> dict:    
    async with session.get(url, **kwargs) as resp:
        return await resp.json()



async def get_yt_views(session: aiohttp.ClientSession, vid: str) -> int:
    url = 'https://www.youtube.com/watch?v=' + vid
    html = await fetch_text(url, session)
    if 'viewCount":"' in html:
        parts = html.split('viewCount":"')
        if len(parts) > 1:
            view_count = parts[1].split('"')[0]
            try:
                return int(view_count)
            except ValueError:
                return 0
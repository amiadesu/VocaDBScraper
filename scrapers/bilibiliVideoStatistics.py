import xml.etree.ElementTree as ET
import aiohttp
import asyncio
from typing import Tuple, List, Optional
import logging

from utils.bvid import get_bv

from constants.states import ResponseState

class BilibiliScraper():
    BASE_URL = "https://api.bilibili.com/x/web-interface/view?bvid="

    def __init__(self, user_agent: Optional[dict] = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)

        self.user_agent = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/135.0.0.0 Safari/537.36"
            )
        }

        if (user_agent and not user_agent["User-Agent"]):
            self.logger.info("Improper User-Agent was passed. Falling back to default UA.")
        elif (user_agent):
            self.user_agent = user_agent

    def _get_video_url(self, vid: str):
        return self.BASE_URL + get_bv(vid)
    
    def _parse_json(self, json: dict) -> Tuple[ResponseState, dict]:
        code = json.get("code", None)

        if (code is None):
            return (ResponseState.UNKNOWN, {})
        elif (code == 0):
            data = json.get("data", {})
            stats = data.get("stat", {})
            return (
                ResponseState.SUCCESS,
                {
                    "views" : stats.get("view", 0),
                    "likes" : stats.get("like", 0),
                    "dislikes" : stats.get("dislike", 0),
                    "favorites" : stats.get("favorite", 0)
                }
            )
        elif (code in [-400, -404]):
            return (ResponseState.NOT_FOUND, {})
        elif (code in [62002, 62012, -403]):
            return (ResponseState.DELETED, {
                "views" : 0,
                "likes" : 0,
                "dislikes" : 0,
                "favorites" : 0
            })

        self.logger.debug(json)          

        return (ResponseState.UNKNOWN, {})
    
    async def _get_single_video_data(self, session: aiohttp.ClientSession, vid: str) -> Tuple[str, ResponseState, dict]:
        try:
            async with session.get(self._get_video_url(vid), headers=self.user_agent) as res:
                json = await res.json()
                res_state, data = self._parse_json(json)
                return (vid, res_state, data)
        except Exception as e:
            self.logger.debug(e)
            return (vid, ResponseState.UNKNOWN, {})

    async def get_videos_data(self, ids: List[str]) -> List[Tuple[str, ResponseState, dict]]:
        """
        Each video id inside ids should be an aid, not bvid.
        """
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._get_single_video_data(session, vid)
                for vid in ids
            ]

            results = await asyncio.gather(*tasks)

            return results

    
import xml.etree.ElementTree as ET
import aiohttp
import asyncio
from typing import Tuple, List
import logging

from constants.states import ResponseState

class NicoNicoScraper():
    BASE_URL = "https://ext.nicovideo.jp/api/getthumbinfo/"

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)

    def test_logging(self):
        self.logger.debug("Debug")
        self.logger.info("Info")
        self.logger.warning("Warning")
        self.logger.error("Error")
        self.logger.critical("Critical")

    def _get_video_url(self, vid: str):
        return self.BASE_URL + vid
    
    def _parse_xml_tree(self, xml: str) -> Tuple[ResponseState, dict]:
        try:
            root = ET.fromstring(xml)
            status = root.attrib.get("status", "unknown")

            if (status == "ok"):
                view_counter = root.findtext("thumb/view_counter", default="0")
                try:
                    view_counter = int(view_counter)
                except Exception:
                    view_counter = 0
                    
                return (ResponseState.SUCCESS, {
                    "views" : view_counter
                })
            elif (status == "fail"):
                error_code = root.findtext("error/code", default="unknown")
                if (error_code == "DELETED"):
                    return (ResponseState.DELETED, {
                        "views" : 0
                    })
                elif (error_code == "NOT_FOUND"):
                    return (ResponseState.NOT_FOUND, {})  

            self.logger.debug(xml)          

            return (ResponseState.UNKNOWN, {})
        except ET.ParseError:
            self.logger.debug(f"Parse error: {xml}")
            return (ResponseState.UNKNOWN, {})
    
    async def _get_single_video_data(self, session: aiohttp.ClientSession, vid: str) -> Tuple[str, ResponseState, dict]:
        try:
            async with session.get(self._get_video_url(vid)) as res:
                xml = await res.text()
                res_state, data = self._parse_xml_tree(xml)
                return (vid, res_state, data)
        except Exception as e:
            self.logger.debug(e)
            return (vid, ResponseState.UNKNOWN, {})

    async def get_videos_data(self, ids: List[str]) -> List[Tuple[str, ResponseState, dict]]:
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._get_single_video_data(session, vid)
                for vid in ids
            ]

            results = await asyncio.gather(*tasks)

            return results

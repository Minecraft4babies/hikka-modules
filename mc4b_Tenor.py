# ©️ Minecraft4babies
# 🌐 https://github.com/Minecraft4babies/hikka-modules/

import re
import typing
import requests

from .. import loader, utils
from ..inline.types import InlineQuery

@loader.tds
class Tenor(loader.Module):
    """Regain access to Tenor GIFs in Hikka Userbot. By @Minecraft4babies_Modules"""

    strings = {
        "name": "Tenor",
        "_ihandle_doc_tenor": "Send Tenor GIFs (search by tags).",
        "api_url": "https://tenor.com/",
        "thumb_url": "https://tenor.com/assets/img/favicon/favicon-32x32.png",
        "result_title": "Tenor GIF #{i}",
        "result_description": "",
        "result_caption": "",
    }

    strings_ru = {
        "_ihandle_doc_tenor": "Отправить GIF'ки из Tenor (поиск по тегам).",
        "api_url": "https://tenor.com/ru/",
    }

    strings_ua = {
        "_ihandle_doc_tenor": "Відправити GIF'ки з Tenor (пошук за тегами).",
        "api_url": "https://tenor.com/uk/",
    }

    @loader.inline_handler(
        thumb_url=strings["thumb_url"]
    )
    async def tenor(self, query: InlineQuery):

        gifs = await self._get_gif_list(query.args)

        return [
            {
                "title": self.strings("result_title").format(i=i + 1),
                "description": self.strings("result_description"),
                "caption": self.strings("result_caption"),
                "gif": url
            }
            for i, url in enumerate(gifs)
        ]

    async def _get_gif_list(self, args: str) -> typing.List[str]:
        """Get the Tenor GIF list based on parsed inline arguments."""

        if not args:
            return await self._get_default_gifs()

        keywords = [token.lower() for token in args.split() if token.strip()]

        return await self._get_gifs(keywords)

    async def _get_default_gifs(self) -> typing.List[str]:
        """Return a default list of Tenor GIFs."""

        try:
            response = await utils.run_sync(
                requests.get,
                self.strings("api_url"),
                timeout=5,
            )
            html_content = response.text
        except Exception:
            return []

        return self._parse_gifs(html_content)

    async def _get_gifs(self, keywords: typing.List[str]) -> typing.List[str]:
        """Return a list of Tenor GIFs based on keywords."""
        
        try:
            response = await utils.run_sync(
                requests.get,
                self.strings("api_url") + "search/" + "-".join(keywords),
                timeout=5,
            )
            html_content = response.text
        except Exception:
            return []

        return self._parse_gifs(html_content)

    def _parse_gifs(self, html_content: str) -> typing.List[str]:
        """Parse the HTML content and extract `.mp4` GIF URLs."""

        gifs = []
        
        if not html_content:
            return gifs

        # Match MP4 URLs in <source> tags like
        # <source media="..." type="video/mp4" srcset="...mp4 186w">
        pattern = re.compile(
            r'<source[^>]*\btype=["\']video/mp4["\'][^>]*\bsrcset=["\']([^"\']+?\.mp4)(?:\s+\d+w)?["\']',
            re.IGNORECASE,
        )

        for match in pattern.finditer(html_content):
            gifs.append(match.group(1))

        if not gifs:
            gifs = re.findall(r'https?://[^"\s<>]+?\.mp4', html_content)

        gifs = [url for url in gifs if url.startswith("http://") or url.startswith("https://")]
        
        return list(dict.fromkeys(gifs))

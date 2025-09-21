from aiohttp import ClientSession
from langdetect import detect, DetectorFactory

import re
from typing import Literal

from config import TRANSLATER_API_KEY


DetectorFactory.seed = 0


def heuristic_detection(text) -> Literal["EN", "ZH-HANT"]:
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    chinese_ratio = len(chinese_chars) / max(len(text), 1)

    english_chars = re.findall(r'[a-zA-Z]', text)
    english_ratio = len(english_chars) / max(len(text), 1)

    if chinese_ratio > 0.3:
        return "EN"

    elif english_ratio > 0.6:
        return "ZH-HANT"

    return "EN" if chinese_ratio > english_ratio else "ZH-HANT"


async def translate_text(
    text: str,
) -> str:
    if not text.strip():
        return ""

    target_language = "EN"
    # try:
    #     lang = detect(text=text)

    #     if lang.startswith("zh"):
    #         target_language = "EN"
    #     else:
    #         target_language = "ZH-HANT"
    # except:
    target_language = heuristic_detection(text)

    print(target_language)
    async with ClientSession() as session:
        response = await session.post(
            "https://api-free.deepl.com/v2/translate",
            data={
                "auth_key": TRANSLATER_API_KEY,
                "text": text,
                "target_lang": target_language
            }
        )

        if response.status != 200:
            print(await response.json())
            return ""

        data = await response.json()
        return data["translations"][0]["text"]

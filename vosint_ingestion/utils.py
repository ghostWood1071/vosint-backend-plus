import uuid
from datetime import datetime

import pytz
import unidecode
import requests
from core.config import settings


def get_time_now_string(
    tz: str = "Asia/Ho_Chi_Minh", fmt: str = "%Y/%m/%d %H:%M:%S"
) -> str:
    return datetime.now(pytz.timezone(tz)).strftime(fmt)


def get_time_now_string_y_m_d(
    tz: str = "Asia/Ho_Chi_Minh", fmt: str = "%Y/%m/%d"
) -> str:
    return datetime.now(pytz.timezone(tz)).strftime(fmt)


def get_time_now_string_y_m_now(
    tz: str = "Asia/Ho_Chi_Minh", fmt: str = "%Y/%m/%d"
) -> str:
    return datetime.strptime(str(get_time_now_string_y_m_d()), "%Y/%m/%d")


def gen_id(length: int = 12) -> str:
    return str(uuid.uuid4().hex[-length:])


def norm_text(text: str) -> str:
    text_lower = text.lower()
    text_removed_accent = unidecode.unidecode(text_lower)
    return text_removed_accent


def crawl_ttxvn_func():
    try:
        requests.post(f"{settings.PIPELINE_API}/Job/api/crawling_ttxvn_news")
    except Exception as e:
        print(e)

import requests
from core.config import settings
import json


def summarize(lang: str = "", title: str = "", paras: str = "", k: float = 0.4):
    try:
        request = requests.post(
            settings.SUMMARIZE_API,
            data=json.dumps(
                {
                    "lang": lang,
                    "title": title,
                    "paras": paras,
                    "k": k,
                    "description": "",
                }
            ),
        )
        if request.status_code != 200:
            raise Exception("Summarize failed")
        data = request.json()
        return data
    except:
        raise Exception("summarize failed")

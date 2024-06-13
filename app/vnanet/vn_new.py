from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Path
from playwright.sync_api import sync_playwright
from pymongo import MongoClient

from app.vnanet.service import count, get_all
from core.config import settings
from db.init_db import get_collection_client

router = APIRouter()
client = get_collection_client("News_vnanet")


@router.get("/get-craw-vnnew/{check_crawl}")
async def get_craw(
    text_search: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    check_crawl: Optional[str] = Path(
        None, title="check crawl", enum=["all", "crawled", "not_crawl"]
    ),
    skip=1,
    limit=10,
):
    list_craw = await get_all(
        text_search, start_date, end_date, check_crawl, int(skip), int(limit)
    )
    count_craw = await count(
        text_search, start_date, end_date, check_crawl, int(skip), int(limit)
    )
    return {"data": list_craw, "total": count_craw}


visited_data_ids = set()


@router.get("/fetch-news-in-country")
def fetch_new_in_country():
    list_new = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context()
        page = context.new_page()

        page.goto(
            "https://news.vnanet.vn/?created=7%20day&servicecateid=1&scode=1&qcode=17"
        )

        links = page.query_selector_all("a.spATitle")

        for link in links:
            href = link.get_attribute("href")

            data_id = link.get_attribute("data-id")

            if data_id in visited_data_ids:
                continue

            visited_data_ids.add(data_id)

            title = link.inner_text().strip()

            if not title:
                continue

            # Retrieve data-service
            data_service = link.get_attribute("data-service")

            # Retrieve timestamp
            timestamp = page.query_selector("span.spADate").inner_text()

            datetime_obj = datetime.strptime(timestamp, "%d/%m/%Y %H:%M")

            data = {
                "title": title,
                "href": href,
                "data_id": data_id,
                "data_service": data_service,
                "date": datetime_obj,
                "is_crawled": False,
            }
            list_new.append(data)

        insert_into_mongodb(list_new)

    return {"data": list_new}


@router.get("/fetch-news-in-world")
def fetch_new_in_world():
    list_new = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context()
        page = context.new_page()

        page.goto(
            "https://news.vnanet.vn/?created=7%20day&servicecateid=3&scode=1&qcode=17"
        )
        page.wait_for_load_state("networkidle")

        links = page.query_selector_all("a.spATitle")

        for link in links:
            href = link.get_attribute("href")

            data_id = link.get_attribute("data-id")

            if data_id in visited_data_ids:
                continue

            visited_data_ids.add(data_id)

            title = link.inner_text().strip()

            if not title:
                continue

            # Retrieve data-service
            data_service = link.get_attribute("data-service")

            # Retrieve timestamp
            timestamp = page.query_selector("span.spADate").inner_text()

            datetime_obj = datetime.strptime(timestamp, "%d/%m/%Y %H:%M")

            data = {
                "title": title,
                "href": href,
                "data_id": data_id,
                "data_service": data_service,
                "date": datetime_obj,
                "is_crawled": False,
            }
            list_new.append(data)

        insert_into_mongodb_2(list_new)

    return {"data": list_new}


@router.get("/fetch-economics-news-in-country")
def fetch_new_economics_news_in_country():
    list_new = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context()
        page = context.new_page()

        page.goto(
            "https://news.vnanet.vn/?created=7%20day&servicecateid=10&scode=1&qcode=17"
        )
        page.wait_for_load_state("networkidle")

        links = page.query_selector_all("a.spATitle")

        for link in links:
            href = link.get_attribute("href")

            data_id = link.get_attribute("data-id")

            if data_id in visited_data_ids:
                continue

            visited_data_ids.add(data_id)

            title = link.inner_text().strip()

            if not title:
                continue

            # Retrieve data-service
            data_service = link.get_attribute("data-service")

            # Retrieve timestamp
            timestamp = page.query_selector("span.spADate").inner_text()

            datetime_obj = datetime.strptime(timestamp, "%d/%m/%Y %H:%M")

            data = {
                "title": title,
                "href": href,
                "data_id": data_id,
                "data_service": data_service,
                "date": datetime_obj,
                "is_crawled": False,
            }
            list_new.append(data)

        insert_into_mongodb_3(list_new)

    return {"data": list_new}


@router.get("/fetch-economics-news-in-world")
def fetch_newe_conomics_news_in_world():
    list_new = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context()
        page = context.new_page()

        page.goto(
            "https://news.vnanet.vn/?created=7%20day&servicecateid=1000&scode=1&qcode=17"
        )
        page.wait_for_load_state("networkidle")

        links = page.query_selector_all("a.spATitle")

        for link in links:
            href = link.get_attribute("href")

            data_id = link.get_attribute("data-id")

            if data_id in visited_data_ids:
                continue

            visited_data_ids.add(data_id)

            title = link.inner_text().strip()

            if not title:
                continue

            # Retrieve data-service
            data_service = link.get_attribute("data-service")

            # Retrieve timestamp
            timestamp = page.query_selector("span.spADate").inner_text()

            datetime_obj = datetime.strptime(timestamp, "%d/%m/%Y %H:%M")

            data = {
                "title": title,
                "href": href,
                "data_id": data_id,
                "data_service": data_service,
                "date": datetime_obj,
                "is_crawled": False,
            }
            list_new.append(data)

        insert_into_mongodb_4(list_new)

    return {"data": list_new}


@router.get("/fetch-fast-news")
def fetch_fast_new():
    list_new = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context()
        page = context.new_page()

        page.goto(
            "https://news.vnanet.vn/?created=7%20day&servicecateid=1097&scode=1&qcode=17"
        )
        page.wait_for_load_state("networkidle")

        links = page.query_selector_all("a.spATitle")

        for link in links:
            href = link.get_attribute("href")

            data_id = link.get_attribute("data-id")

            if data_id in visited_data_ids:
                continue

            visited_data_ids.add(data_id)

            title = link.inner_text().strip()

            if not title:
                continue

            # Retrieve data-service
            data_service = link.get_attribute("data-service")

            # Retrieve timestamp
            timestamp = page.query_selector("span.spADate").inner_text()

            datetime_obj = datetime.strptime(timestamp, "%d/%m/%Y %H:%M")

            data = {
                "title": title,
                "href": href,
                "data_id": data_id,
                "data_service": data_service,
                "date": datetime_obj,
                "is_crawled": False,
            }
            list_new.append(data)

        insert_into_mongodb_5(list_new)

    return {"data": list_new}


def insert_into_mongodb(data):
    client = MongoClient(settings.MONGO_DETAILS)
    database = client.vosint_db
    collection = database.News_vnanet
    collection.insert_many(data)


def insert_into_mongodb_2(data):
    client = MongoClient(settings.MONGO_DETAILS)
    database = client.vosint_db
    collection = database.News_vnanet
    collection.insert_many(data)


def insert_into_mongodb_3(data):
    client = MongoClient(settings.MONGO_DETAILS)
    database = client.vosint_db
    collection = database.News_vnanet
    collection.insert_many(data)


def insert_into_mongodb_4(data):
    client = MongoClient(settings.MONGO_DETAILS)
    database = client.vosint_db
    collection = database.News_vnanet
    collection.insert_many(data)


def insert_into_mongodb_5(data):
    client = MongoClient(settings.MONGO_DETAILS)
    database = client.vosint_db
    collection = database.News_vnanet
    collection.insert_many(data)

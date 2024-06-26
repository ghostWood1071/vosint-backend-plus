from fastapi import APIRouter, HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi.params import Depends

from .service import (
    count_news_country_today,
    count_news_hours,
    news_country_today,
    news_hours_today,
    news_seven_nearest,
    top_news_by_topic,
    top_user_read,
    total_users,
    hot_events_today,
    status_source_news,
    source_news_lowest_hightest,
    users_online,
    top_country_by_entities,
    total_news_by_time,
    news_read_by_user,
    status_error_source_news,
    status_completed_source_news,
    status_unknown_source_news,
)

from .plus_service import * 
from .plus_model import *

router = APIRouter()


@router.get("/hot-events-today")
async def get_hot_events_today(authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    return await hot_events_today(user_id)


@router.get("/news-country-today")
async def get_news_country_today(start_day: int):
    return await news_country_today(start_day)


@router.get("/news-hours-today")
async def get_news_hours_today():
    return await news_hours_today()


@router.post("/count-news-country-today")
async def get_count_news_country_today():
    return await count_news_country_today()


@router.post("/count-news-hours")
async def get_count_news_hours():
    return await count_news_hours()


# New
# ------- Start leader --------
@router.get("/get-news-seven-nearest")
async def get_news_seven_nearest_r(day_space: int = 7):
    return await news_seven_nearest(day_space)


@router.get("/get-top-news-by-topic")
async def get_top_news_by_topic():
    return await top_news_by_topic()


@router.get("/get-top-news-by-country")
async def get_top_news_by_country(
    day_space: int = 7, top: int = 5, start_date: str = None, end_date: str = None
):
    return await top_country_by_entities(day_space, top, start_date, end_date)


@router.get("/get-total-users")
async def get_total_users():
    return await total_users()


@router.get("/get-total-users-online")
async def get_total_users_online(authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    return await users_online(user_id)


@router.get("/get-top-user-read")
async def get_top_user_read(page_index: int = 1, page_size:int = 5, status:bool=None):
    return await top_user_read(page_index, page_size, status)


# ------- End leader --------


# ------- Start expert --------
@router.get("/get-source-news-lowest-hightest")
async def get_source_news_lowest_hightest(days=1):
    return await source_news_lowest_hightest(days)


@router.get("/get-total-news-by-time")
async def get_total_news_by_time(days=1):
    return await total_news_by_time(days)


@router.get("/get-news-read-by-user")
async def get_news_read_by_user(days: int = 7, authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()  # Dont need ObjectId
    return await news_read_by_user(days, user_id)


# ------- End expert --------


# ------- Start admin --------
@router.get("/get-status-source-news")
async def get_status_source_news(day_space: int = 3):
    return await status_source_news(day_space)


@router.get("/get-pipeline-error")
async def get_pipeline_error(
    day_space: int = 7, start_date=None, end_date=None, page_index=1, page_size=10
):
    return await status_error_source_news(
        day_space, start_date, end_date, int(page_index), int(page_size)
    )


@router.get("/get-pipeline-completed")
async def get_pipeline_completed(
    day_space: int = 7, start_date=None, end_date=None, page_index=1, page_size=10
):
    return await status_completed_source_news(
        day_space, start_date, end_date, int(page_index), int(page_size)
    )


@router.get("/get-pipeline-unknown")
async def get_pipeline_unknown(
    day_space: int = 7, start_date=None, end_date=None, page_index=1, page_size=10
):
    return await status_unknown_source_news(
        day_space, start_date, end_date, int(page_index), int(page_size)
    )


# ------- End admin --------

@router.post("/get-source-by-source-group-id")
def get_source_by_source_group_id_route(params:GetSourceListParams):
    try:
        data = get_source_from_source_group(**params.dict())
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))
    
@router.post("/statistic_source_by_time")
def get_statistic_source_by_time(source_host_name: str):
    try:
        data = statisitic_source_by_time(source_host_name)
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))
    
@router.post("/update_crawl_times")
def update_crawl_times_route(source_id:str, crawl_times:List[str]=[]):
    try:
        data = save_suggest_crawl_times(source_id, crawl_times)
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))
from app.dashboard.service import count_news_country_today, count_news_hours
from vosint_ingestion.async_scheduler import AsyncScheduler


async def start_all_jobs():
    # Cron every day at 00:00
    AsyncScheduler.instance().add_job(
        id="countries_today",
        func=count_news_country_today,
        cron_expr="0 0 * * *",
    )

    # cron every hour
    AsyncScheduler.instance().add_job(
        id="countries_hours",
        func=count_news_hours,
        cron_expr="0 * * * *",
    )


async def stop_all_jobs():
    jobs = AsyncScheduler.instance().get_jobs()
    for job in jobs:
        AsyncScheduler.instance().remove_job(job)


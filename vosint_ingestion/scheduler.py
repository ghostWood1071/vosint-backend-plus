from typing import Callable

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from common.internalerror import *
from core.config import settings
from apscheduler.jobstores.mongodb import MongoDBJobStore
import utils
import statistic_schedule
from datetime import datetime
import pytz
from threading import Lock


class Scheduler:
    __instance = None
    __lock = Lock()

    def __init__(self):
        if Scheduler.__instance is not None:
            raise InternalError(
                ERROR_SINGLETON_CLASS,
                params={
                    "code": [self.__class__.__name__.upper()],
                    "msg": [self.__class__.__name__],
                },
            )
        mongo_config = {
            "host": settings.MONGO_DETAILS,
            "database": settings.DATABASE_NAME,
            "collection": "jobstore",
        }
        jobstore = {"default": MongoDBJobStore(**mongo_config)}
        self.__bg_scheduler = BackgroundScheduler(jobstores=jobstore)
        self.__bg_scheduler.start()
        self.timezone = "Asia/Ho_Chi_Minh"
        Scheduler.__instance = self

    @staticmethod
    def instance():
        """Static access method."""
        if Scheduler.__instance is None:
            with Scheduler.__lock:
                if Scheduler.__instance is None:
                    Scheduler()
        return Scheduler.__instance

    def add_job(self, id: str, func: Callable, cron_expr: str, args: list = []):
        # print('args..............',args)
        trigger = CronTrigger().from_crontab(cron_expr)
        aware_time = datetime.now(pytz.timezone(self.timezone))
        trigger.timezone = aware_time.tzinfo
        self.__bg_scheduler.add_job(id=id, func=func, args=args, trigger=trigger)

    def remove_job(self, id: str):
        self.__bg_scheduler.remove_job(id)

    def get_jobs(self) -> list:
        jobs = [job.id for job in self.__bg_scheduler.get_jobs()]
        return jobs

    def add_job_interval(
        self,
        id: str,
        func: Callable,
        interval: int,
        args: list = [],
        next_run_time=None,
    ):
        self.__bg_scheduler.add_job(
            id=id,
            func=func,
            args=args,
            trigger="interval",
            seconds=interval,
            next_run_time=next_run_time,
        )

    def add_job_crawl_ttxvn(self):
        try:
            self.__bg_scheduler.add_job(
                id="crawttxvnnews",
                func=utils.crawl_ttxvn_func,
                trigger=CronTrigger.from_crontab("0 * * * *"),
            )
        except Exception as e:
            print("crawl ttxvn existed, no need to crete new one")

    def add_job_update_error_source(self):
        try:
            self.__bg_scheduler.add_job(
                id="top_news",
                func=statistic_schedule.top_news_by_topic,
                trigger=CronTrigger.from_crontab("0,15,30,45 * * * *"),
            )
        except Exception as e:
            print("dashboard_error_source existed, no need to crete new one")

    def add_job_clear_activity(self):
        try:
            self.__bg_scheduler.add_job(
                id="clear_slave_activity",
                func=statistic_schedule.clear_slave_activity,
                trigger=CronTrigger.from_crontab("0 * * * *"),
            )
        except Exception as e:
            print("clear_slave_activity existed, no need to create one")

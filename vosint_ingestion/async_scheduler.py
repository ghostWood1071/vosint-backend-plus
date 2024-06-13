from typing import Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from common.internalerror import *


class AsyncScheduler:
    __instance = None

    def __init__(self):
        if AsyncScheduler.__instance is not None:
            raise InternalError(
                ERROR_SINGLETON_CLASS,
                params={
                    "code": [self.__class__.__name__.upper()],
                    "msg": [self.__class__.__name__],
                },
            )

        self.__async_scheduler = AsyncIOScheduler()
        self.__async_scheduler.start()

        AsyncScheduler.__instance = self

    @staticmethod
    def instance():
        """Static access method."""
        if AsyncScheduler.__instance is None:
            AsyncScheduler()
        return AsyncScheduler.__instance

    def add_job(self, id: str, func: Callable, cron_expr: str, args: list = []):
        self.__async_scheduler.add_job(
            id=id, func=func, args=args, trigger=CronTrigger.from_crontab(cron_expr)
        )

    def remove_job(self, id: str):
        self.__async_scheduler.remove_job(id)

    def get_jobs(self) -> list:
        jobs = [job.id for job in self.__async_scheduler.get_jobs()]
        return jobs

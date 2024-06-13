import logging
from logging.handlers import TimedRotatingFileHandler

from common.internalerror import *
from configs import GlobalConfigs


class Logger(object):
    __instance = None

    def __init__(self):
        if Logger.__instance is not None:
            raise InternalError(
                ERROR_SINGLETON_CLASS,
                params={
                    "code": [self.__class__.__name__.upper()],
                    "msg": [self.__class__.__name__],
                },
            )

        log_dir = GlobalConfigs.instance().LOG["log_dir"]
        file_name = GlobalConfigs.instance().LOG["file_name"]
        when = GlobalConfigs.instance().LOG["when"]
        interval = GlobalConfigs.instance().LOG["interval"]
        backup_count = GlobalConfigs.instance().LOG["backup_count"]

        # Split log at 0h everyday
        handler = TimedRotatingFileHandler(
            f"./{log_dir}/{file_name}",
            when=when,
            interval=interval,
            backupCount=backup_count,
        )
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        self.__logger = logging.getLogger("RotatingFileHandler")
        self.__logger.setLevel(logging.DEBUG)
        self.__logger.addHandler(handler)
        Logger.__instance = self

    @staticmethod
    def instance():
        """Static access method."""
        if Logger.__instance is None:
            Logger()
        return Logger.__instance

    def debug(self, content: str):
        self.__logger.debug(content)

    def info(self, content: str):
        self.__logger.info(content)

    def warning(self, content: str):
        self.__logger.warning(content)

    def error(self, content: str):
        self.__logger.error(content)

    def critical(self, content: str):
        self.__logger.critical(content)

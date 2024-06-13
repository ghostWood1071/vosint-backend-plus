import yaml
from common.internalerror import *


class GlobalConfigs:
    __instance = None

    def __init__(self):
        if GlobalConfigs.__instance is not None:
            raise InternalError(
                ERROR_SINGLETON_CLASS,
                params={
                    "code": [self.__class__.__name__.upper()],
                    "msg": [self.__class__.__name__],
                },
            )

        # Get the configuarion information from yaml file
        cfg = self.__loadConfig("configs/configs.yaml")

        # Validate configuration data
        if cfg is None or cfg.get("api") is None or cfg.get("log") is None:
            raise InternalError(
                ERROR_MISSING_CONFIG, params={"msg": ["API server or Log information"]}
            )

        self.API = cfg["api"]
        self.LOG = cfg["log"]

        # Validate details data
        if (
            self.API.get("port") is None
            or self.API.get("url") is None
            or self.API.get("public_dir") is None
        ):
            raise InternalError(
                ERROR_MISSING_CONFIG, params={"msg": ["API server information"]}
            )
        if (
            self.LOG.get("log_dir") is None
            or self.LOG.get("file_name") is None
            or self.LOG.get("when") is None
            or self.LOG.get("interval") is None
            or self.LOG.get("backup_count") is None
        ):
            raise InternalError(
                ERROR_MISSING_CONFIG, params={"msg": ["log information"]}
            )

        # Cast string to correct data type
        self.API["port"] = int(self.API["port"])
        self.LOG["interval"] = int(self.LOG["interval"])
        self.LOG["backup_count"] = int(self.LOG["backup_count"])
        GlobalConfigs.__instance = self

    @staticmethod
    def instance():
        """Static access method."""
        if GlobalConfigs.__instance is None:
            GlobalConfigs()
        return GlobalConfigs.__instance

    def __loadConfig(self, path: str):
        """
        Get the configuration information from yaml file

        Parameters
        ----------
        path : str
            Configuration file path (*.yaml)

        Returns
        -------
        : dict
            The configuration information
        """
        with open(path, "r") as f:
            cfg = yaml.load(f, Loader=yaml.SafeLoader)
        return cfg

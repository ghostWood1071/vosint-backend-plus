class InternalError(Exception):
    def __init__(self, error: dict = {}, params: dict = {}):
        if not error:
            raise Exception("Error is required.")

        if not params:
            raise Exception("Parameters is required.")

        self.__error = error
        self.__params = params
        if "code" not in self.__params or not self.__params["code"]:
            self.__params["code"] = []
        if "msg" not in self.__params or not self.__params["msg"]:
            self.__params["msg"] = []

    def to_dict(self) -> dict:
        return {
            "code": self.__error["code"].format(*self.__params["code"]),
            "msg": self.__error["msg"].format(*self.__params["msg"]),
        }

    def __str__(self) -> str:
        return "InternalError: {} - {}".format(
            self.__error["code"].format(*self.__params["code"]),
            self.__error["msg"].format(*self.__params["msg"]),
        )


ERROR_SINGLETON_CLASS = {
    "code": "ERROR_{}_SINGLETON_CLASS",
    "msg": "{} class is a singleton.",
}

ERROR_REQUIRED = {"code": "ERROR_{}_REQUIRED", "msg": "{} is required."}

ERROR_NOT_FOUND = {"code": "ERROR_{}_NOT_FOUND", "msg": "Could not found {}."}

ERROR_MISSING_CONFIG = {
    "code": "ERROR_MISSING_CONFIG",
    "msg": "Configuration data is missing {}.",
}

ERROR_NOT_INTEGER = {"code": "ERROR_{}_NOT_INTEGER", "msg": "{} must be integer type."}

ERROR_NOT_LESS_THAN_0 = {
    "code": "ERROR_{}_NOT_LESS_THAN_0",
    "msg": "{} must not be less than zero.",
}

ERROR_NOT_ALLOW_SPECIFY = {
    "code": "ERROR_{}_NOT_ALLOW_SPECIFY",
    "msg": "Not allowed to specify {}.",
}

ERROR_DISABLED = {"code": "ERROR_{}_DISABLED", "msg": "{} is disabled."}

ERROR_NOT_IN = {"code": "ERROR_{}_NOT_IN", "msg": "{} must be in {}."}

ERROR_NOT_INPUT = {"code": "ERROR_{}_NOT_INPUT", "msg": "{} must be input type."}

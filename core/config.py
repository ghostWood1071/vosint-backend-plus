from typing import List

from pydantic import AnyHttpUrl, BaseSettings
import os
import json
from decouple import Config, RepositoryEnv
import sys


script_path = os.path.abspath(sys.argv[0])
script_directory = os.path.dirname(script_path)


# class Settings(BaseSettings):
class Settings:
    APP_TITLE: str = "V-OSINT API"
    APP_ORIGINS: List[str] = []

    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 6082
    APP_STATIC_DIR: str = ""

    PRIVATE_KEY: str = ""
    PUBLIC_KEY: str = ""

    # MONGO_DETAILS: str = (
    #     "mongodb://vosint:vosint_2022@118.70.52.237:27017/?authMechanism=DEFAULT"
    # )
    MONGO_DETAILS: str = ""  # = "mongodb://localhost:27017"
    DATABASE_NAME: str = ""  # = "vosint_db"

    mong_host: str = ""  # = "localhost"  # "118.70.52.237"
    mongo_port: int = 6100  # = 27017
    mongo_username: str = ""  # = "vosint"
    mongo_passwd: str = ""  # = "vosint_2022"
    mongo_db_name: str = ""  # = "vosint_db"

    ELASTIC_CONNECT: str = ""  # = "http://localhost:9200"

    ROOT_PATH: str = ""  # = ""

    SUMMARIZE_API: str = ""  # = "http://sumthesis.aiacademy.edu.vn/ext"

    PIPELINE_API: str = ""

    KEYWORD_EXTRACTION_API: str = ""

    TRANSLATE_API: str = ""

    TOPIC_SENTIMENT_API:str = ""

    def read_secret(self):
        with open(f"{script_directory}/secrets/PUBLIC_KEY", mode="r") as file:
            self.PUBLIC_KEY = file.read()
        with open(f"{script_directory}/secrets/PRIVATE_KEY", mode="r") as file:
            self.PRIVATE_KEY = file.read()

    def dict(self):
        data = {k: self.__getattribute__(k) for k in self.__annotations__.keys()}
        return data

    def __dict__(self):
        data = {k: self.__getattribute__(k) for k in self.__annotations__.keys()}
        return data.items()

    def load_env(self):
        config = Config(RepositoryEnv(f"{script_directory}/.env"))
        self.read_secret()
        for env_name in list(self.__annotations__.keys()):
            if env_name == "PUBLIC_KEY" or env_name == "PRIVATE_KEY":
                continue
            type_obj = self.__annotations__[env_name]
            value = config.get(env_name, None)
            if not value:
                continue
            if type_obj != List[str]:
                env_val = type_obj(value)
            else:
                env_val = str(value)
            self.__setattr__(env_name, env_val)

    def __init__(self):
        # loaded = dotenv.load_dotenv()
        self.load_env()
        setting_dict = self.dict()
        for env_name in list(self.__annotations__.keys()):
            type_obj = self.__annotations__[env_name]
            if type_obj != List[str]:
                env_val = type_obj(os.environ.get(env_name, setting_dict.get(env_name)))
            else:
                env_val = os.environ.get(env_name, str(setting_dict.get(env_name)))
            self.__setattr__(env_name, env_val)


settings = Settings()

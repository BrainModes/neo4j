import os
from functools import lru_cache
from typing import Any
from typing import Dict
from typing import List

from pydantic import BaseSettings
from pydantic import Extra
from dotenv import load_dotenv
from common import VaultClient
from common.config import ConfigClass as vault_config

load_dotenv()
SRV_NAMESPACE = os.environ.get('APP_NAME', 'dataset_neo4j')
CONFIG_CENTER_ENABLED = os.environ.get('CONFIG_CENTER_ENABLED', 'false')
VAULT_URL = os.getenv("VAULT_URL")
VAULT_CRT = os.getenv("VAULT_CRT")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")

def load_vault_settings(settings: BaseSettings) -> Dict[str, Any]:
    if CONFIG_CENTER_ENABLED == "false":
        return {}
    else:
        vc = VaultClient(VAULT_URL, VAULT_CRT, VAULT_TOKEN)
        res = vc.get_from_vault(SRV_NAMESPACE)
        return res

class ConfigInfo(BaseSettings):
    APP_NAME: str = 'service_neo4j'
    PORT: int = 5062
    HOST: str = '0.0.0.0'
    LOGLEVEL: str = 'info'
    WORKERS: int = 4
    THREADS: int = 2
    WORKER_CONNECTIONS: int = 5
    DEBUG: bool = True
    NEO4J_URL: str
    NEO4J_USER: str
    NEO4J_PASS: str
    DATA_OPS_UTIL: str
    API_MODULES: List[str] = ['neo4j_api']
    OPEN_TELEMETRY_ENABLED: bool = False
    OPEN_TELEMETRY_HOST: str = '127.0.0.1'
    OPEN_TELEMETRY_PORT: int = 6831

    def modify_values(self, settings):
        settings.DATAOPS = settings.DATA_OPS_UTIL
        return settings

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.allow

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return load_vault_settings, env_settings, init_settings, file_secret_settings


@lru_cache(1)
def get_settings():
    settings = ConfigInfo()
    settings.modify_values(settings)
    return settings


ConfigClass = get_settings()

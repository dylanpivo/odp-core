from enum import Enum
from typing import Literal

from pydantic import AnyHttpUrl, constr

from odp.config import BaseConfig
from odp.config.mixins import AppConfigMixin, DBConfigMixin


class ServerEnv(str, Enum):
    """Deployment environment."""
    DEVELOPMENT = 'development'
    TESTING = 'testing'
    STAGING = 'staging'
    PRODUCTION = 'production'


class LogLevel(str, Enum):
    """Logging detail level."""
    CRITICAL = 'critical'
    ERROR = 'error'
    WARNING = 'warning'
    INFO = 'info'
    DEBUG = 'debug'


class ODPDBConfig(BaseConfig, DBConfigMixin):
    class Config:
        env_prefix = 'ODP_DB_'


class ODPAPIConfig(BaseConfig):
    class Config:
        env_prefix = 'ODP_API_'

    # URL path prefix at which the API is mounted, e.g. `/api`
    PATH_PREFIX: constr(regex=r'^(/\w+)*$') = ''

    # JSON-encoded list of allowed CORS origins; `["*"]` to allow any origin
    ALLOW_ORIGINS: list[Literal['*'] | AnyHttpUrl] = []


class ODPAdminConfig(BaseConfig, AppConfigMixin):
    class Config:
        env_prefix = 'ODP_ADMIN_'


class ODPWebConfig(BaseConfig, AppConfigMixin):
    class Config:
        env_prefix = 'ODP_WEB_'

class ODPMailConfig(BaseConfig):
    class Config:
        env_prefix = 'ODP_MAIL_'

    HOST: str  # mail server IP / hostname
    PORT: int = 25  # mail server port
    TLS: bool = False  # use TLS
    USERNAME: str = None  # sending account username
    PASSWORD: str = None  # sending account password


class ODPConfig(BaseConfig):
    class Config:
        env_prefix = 'ODP_'

    ENV: ServerEnv  # deployment environment
    LOG: LogLevel = 'info'  # logging detail level
    API_URL: AnyHttpUrl = None  # ODP API URL
    ADMIN_URL: AnyHttpUrl = None  # ODP Admin URL

    _subconfig = {
        'API': ODPAPIConfig,
        'DB': ODPDBConfig,
        'ADMIN': ODPAdminConfig,
        'WEB': ODPWebConfig,
        'MAIL': ODPMailConfig,
    }

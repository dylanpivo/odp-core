from pydantic import AnyHttpUrl
from odp.config.base import BaseConfig


class AuthConfig(BaseConfig):
    class Config:
        env_prefix = 'AUTH_'

    URL: AnyHttpUrl = 'http://localhost:8080/realms/odp'

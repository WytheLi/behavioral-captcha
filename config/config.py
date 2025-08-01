import os

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "local.env"), case_sensitive=False)

    BASE_PATH: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 阿里云DashScope API密钥
    DASHSCOPE_API_KEY: str = 'your_dashscope_api_key'


config = Config()

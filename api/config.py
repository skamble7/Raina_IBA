from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    openai_api_key: str
    mongodb_uri: str
    openai_model: str = "gpt-4o"

    rabbitmq_host: str = "localhost"
    rabbitmq_exchange: str = "mphai.raina.exchange"
    rabbitmq_routing_key: str = "iba.artifacts.ready"
    rabbitmq_exchange_type: str = "topic"
    rabbitmq_routing_key_iba_stream: str = "iba.artifact.generated"
    VBA_API_URL: str = "http://localhost:8011"
    PLANTUML_SERVER_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings():
    return Settings()

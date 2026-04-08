from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    RABBITMQ_URL: str
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str = "reports"
    MINIO_SECURE: bool = False

    REPORT_EXCHANGE: str = "report.exchange"
    REPORT_QUEUE: str = "report.queue"
    REPORT_ROUTING_KEY: str = "report.generate"

    class Config:
        env_file = ".env"


settings = Settings()

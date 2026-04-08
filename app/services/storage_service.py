from io import BytesIO
import uuid

from minio import Minio
from minio.error import S3Error

from app.config import settings


class StorageService:
    _client: Minio | None = None

    @classmethod
    def get_client(cls) -> Minio:
        if cls._client is None:
            cls._client = Minio(
                endpoint=settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE,
            )
        return cls._client

    @classmethod
    def upload(cls, data: bytes, filename: str) -> str:
        client = cls.get_client()
        file_id = str(uuid.uuid4())
        object_name = f"{file_id}/{filename}"
        stream = BytesIO(data)

        if not client.bucket_exists(settings.MINIO_BUCKET):
            client.make_bucket(settings.MINIO_BUCKET)

        try:
            client.put_object(
                bucket_name=settings.MINIO_BUCKET,
                object_name=object_name,
                data=stream,
                length=len(data),
                content_type="application/pdf",
            )
        except S3Error as exc:
            raise RuntimeError(f"failed to upload PDF to MinIO: {exc}") from exc

        return file_id

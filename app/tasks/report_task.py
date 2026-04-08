from celery import Task

from app.celery_app import celery_app
from app.config import settings
from app.database import SessionLocal
import app.models 
from app.services.report_service import ReportService


@celery_app.task(
    bind=True,
    name="tasks.generate_report",
    max_retries=3,
    default_retry_delay=10,
    queue=settings.REPORT_QUEUE,
)
def generate_report(self: Task, report_id: str) -> None:
    db = SessionLocal()
    try:
        ReportService(db).generate_and_upload(report_id)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc)
    finally:
        db.close()

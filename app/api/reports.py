from fastapi import APIRouter

from app.tasks.report_task import generate_report

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/{report_id}/generate")
async def generate_report(report_id: str):
    task = generate_report.delay(report_id)
    return {"task_id": task.id, "status": "queued"}


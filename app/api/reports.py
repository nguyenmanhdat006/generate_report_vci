from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Report, ReportHTMLData
from app.tasks.report_task import generate_report
router = APIRouter(prefix="/reports", tags=["reports"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/{report_id}/generate")
async def generate_report_endpoint(report_id: str):
    task = generate_report.delay(report_id)
    return {"task_id": task.id, "status": "queued"}

@router.post("/test/seed")
async def seed_test_data(db: Session = Depends(get_db)):
    """Generate fake report data for PDF testing"""
    report = Report(
        case_number=2024001,
        type="SECURITY_INCIDENT",
        severity=8,
        report_case="CASE-2024-TEST-001",
        title="Test Report - Báo cáo CTIP Test",
        body="Test body content",
        condition="Khai thác qua chuỗi sự kiện giả lập để kiểm tra hiển thị PDF.",
        subscribe_required=True,
        tags=["test", "ddos", "security"],
    )
    db.add(report)
    db.flush()
    
    report_id = str(report.id)
    
    sections_data = [
        {
            "section": "Thông tin chung",
            "section_num": 1,
            "data": "<h3>Loại sự cố</h3><p>Tấn công DDoS từ nước ngoài</p><p>Thời gian phát hiện: 2024-04-09 10:00 UTC+7</p><p>Mức độ nghiêm trọng: Cao</p>"
        },
        {
            "section": "Chi tiết sự cố",
            "section_num": 2,
            "data": "<h3>Nguồn tấn công</h3><p>Địa chỉ IP: 192.168.1.100</p><p>Lưu lượng: 10Gbps</p><p>Duration: 2 giờ</p><p>Protocol: UDP Flood</p>"
        },
        {
            "section": "Biện pháp xử lý",
            "section_num": 3,
            "data": "<h3>Actions Taken</h3><p>✓ Kích hoạt DDoS mitigation</p><p>✓ Chặn IP nguồn</p><p>✓ Tăng băng thông</p><p>✓ Thông báo ISP</p><p>Status: Resolved</p>"
        }
    ]
    
    for section_data in sections_data:
        html_data = ReportHTMLData(
            report_id=report_id,
            section=section_data["section"],
            section_num=section_data["section_num"],
            data=section_data["data"]
        )
        db.add(html_data)
    
    db.commit()
    
    return {
        "report_id": report_id,
        "case_number": report.case_number,
        "title": report.title,
        "sections_count": len(sections_data),
        "message": "Data seeded successfully!",
    }



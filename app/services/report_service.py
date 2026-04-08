import html  
from pathlib import Path
import re

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup
from sqlalchemy import String, cast
from sqlalchemy.orm import Session

from app.services.pdf_service import PdfService
from app.services.storage_service import StorageService
from app.models import Report, ReportFile, ReportHTMLData

templates_dir = Path(__file__).resolve().parent.parent / "templates"
jinja_env = Environment(
    loader=FileSystemLoader(str(templates_dir)),
    autoescape=select_autoescape(["html", "xml"]),
)

def _force_clean_html(fragment: str) -> str:
    if not fragment:
        return ""
    
    decoded = html.unescape(fragment)
    
    cleaned = re.sub(r"</?(html|head|body|meta|title)[^>]*>", "", decoded, flags=re.IGNORECASE)
    
    cleaned = re.sub(r"<script[^>]*>.*?</script>", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r"<style[^>]*>.*?</style>", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    
    return cleaned.strip()

class ReportService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def generate_and_upload(self, report_id: str) -> None:
        report = self.db.query(Report).filter(Report.id == report_id).first()
        if report is None:
            raise ValueError(f"report {report_id} not found")

        sections_db = (
            self.db.query(ReportHTMLData)
            .filter(cast(ReportHTMLData.report_id, String) == str(report_id))
            .order_by(ReportHTMLData.section_num)
            .all()
        )

        html_sections = [
            {
                "section": section.section or "No section",
                "data": Markup(_force_clean_html(section.data)) if section.data else "",
            }
            for section in sections_db
        ]

        context = {
            "title": report.title or f"CTIP-{report.case_number or 'REPORT'}",
            "severity": report.severity if report.severity is not None else "N/A",
            "report_case": report.report_case or str(report.id),
            "created_at": report.created_at.strftime("%d/%m/%Y %H:%M:%S") if report.created_at else "N/A",
            "overview": "Tổng quan",
            "body": Markup(_force_clean_html(report.body)) if report.body else "No content",
            "condition": Markup(_force_clean_html(report.condition)) if report.condition else "",
            "html_sections": html_sections,
            "report": report,
            "sections": html_sections,
        }

        main_template = jinja_env.get_template("ctip_pdf_v2.html")
        final_html = main_template.render(**context)

        try:
            footer_template = jinja_env.get_template("footer_v2.html")
            footer_raw = footer_template.render(**context)

            f_style = re.search(r"<style>(.*?)</style>", footer_raw, re.DOTALL)
            f_body = re.search(r"<footer>(.*?)</footer>", footer_raw, re.DOTALL)

            if f_style and f_body:
                final_html = final_html.replace("</head>", f"<style>{f_style.group(1)}</style></head>")
                final_html = final_html.replace("</body>", f"<footer>{f_body.group(1)}</footer></body>")
            else:
                final_html = final_html.replace("</body>", f"{footer_raw}</body>")
        except:
            pass

        pdf_bytes = PdfService.to_pdf(final_html)

        filename = f"CTIP-{report.case_number}.pdf"
        file_id = StorageService.upload(pdf_bytes, filename)

        file_tag = ReportFile(report_id=report_id, file_id=file_id, filename=filename, main_file=True)
        self.db.add(file_tag)
        self.db.commit()
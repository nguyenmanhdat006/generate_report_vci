from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session

from app.services.pdf_service import PdfService
from app.services.storage_service import StorageService
# from service.models.report import Report, ReportFile, ReportHTMLData


templates_dir = Path(__file__).resolve().parent.parent / "templates"
jinja_env = Environment(
    loader=FileSystemLoader(str(templates_dir)),
    autoescape=select_autoescape(["html", "xml"]),
)


class ReportService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def generate_and_upload(self, report_id: str) -> None:
        # read report metadata
        report = self.db.query(Report).filter(Report.id == report_id).first()
        if report is None:
            raise ValueError(f"report {report_id} not found")

        # read report sections HTML
        sections = (
            self.db.query(ReportHTMLData)
            .filter(ReportHTMLData.report_id == report_id)
            .order_by(ReportHTMLData.section_num)
            .all()
        )

        # render HTML từ template
        template = jinja_env.get_template("ctip_pdf_v2.html")
        html_string = template.render(report=report, sections=sections)

        # chuyển HTML sang PDF
        pdf_bytes = PdfService.to_pdf(html_string)

        filename = f"CTIP-{report.case_number}.pdf"
        file_id = StorageService.upload(pdf_bytes, filename)

        file_tag = ReportFile(
            report_id=report_id,
            file_id=file_id,
            filename=filename,
            main_file=True,
        )
        self.db.add(file_tag)
        self.db.commit()
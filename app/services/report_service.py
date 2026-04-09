import html
from pathlib import Path
import re

from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup
from sqlalchemy import String, cast
from sqlalchemy.orm import Session

from app.services.pdf_service import PdfService
from app.services.storage_service import StorageService
from app.models import Report, ReportFile, ReportHTMLData


def _force_clean_html(fragment: str) -> str:
    if not fragment:
        return ""
    decoded = html.unescape(fragment)
    cleaned = re.sub(r"</?(html|head|body|meta|title)[^>]*>", "", decoded, flags=re.IGNORECASE)
    cleaned = re.sub(r"<script[^>]*>.*?</script>", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r"<style[^>]*>.*?</style>", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    return cleaned.strip()


def _safe(value: str | None, default: str = "") -> Markup | str:
    return Markup(_force_clean_html(value)) if value else default


class ReportService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(Path(__file__).resolve().parent.parent / "templates")),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def _merge_footer(self, main_html: str, footer_html: str) -> str:
        """Parse và inject <style> + <footer> từ footer_v2.html vào main HTML."""
        main_soup = BeautifulSoup(main_html, "html.parser")
        footer_soup = BeautifulSoup(footer_html, "html.parser")

        footer_style = footer_soup.find("style")
        footer_tag = footer_soup.find("footer")

        if footer_style:
            main_soup.head.append(footer_style)
        if footer_tag:
            main_soup.body.append(footer_tag)

        return str(main_soup)

    def _build_context(self, report: Report, html_sections: list) -> dict:
        return {
            "title": report.title or f"CTIP-{report.case_number or 'REPORT'}",
            "severity": report.severity if report.severity is not None else "N/A",
            "report_case": report.report_case or str(report.id),
            "created_at": report.created_at.strftime("%d/%m/%Y %H:%M:%S") if report.created_at else "N/A",
            "overview": "Tổng quan",
            "body": _safe(report.body, default="No content"),
            "condition": _safe(report.condition),
            "html_sections": html_sections,
            "report": report,
            "sections": html_sections,
        }

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
                "data": _safe(section.data),
            }
            for section in sections_db
        ]

        context = self._build_context(report, html_sections)
        main_html = self.jinja_env.get_template("ctip_pdf_v2.html").render(**context)

        footer_html = self.jinja_env.get_template("footer_v2.html").render(**context)
        final_html = self._merge_footer(main_html, footer_html)


        pdf_bytes = PdfService.to_pdf(final_html)

        filename = f"CTIP-{report.case_number}.pdf"
        file_id = StorageService.upload(pdf_bytes, filename)

        self.db.add(ReportFile(
            report_id=report_id,
            file_id=file_id,
            filename=filename,
            main_file=True,
        ))
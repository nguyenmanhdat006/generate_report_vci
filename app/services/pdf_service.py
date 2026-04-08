from pathlib import Path

from weasyprint import HTML


class PdfService:
    @staticmethod
    def to_pdf(html_string: str) -> bytes:
        templates_dir = Path(__file__).resolve().parent.parent / "templates"
        return HTML(string=html_string, base_url=str(templates_dir)).write_pdf()

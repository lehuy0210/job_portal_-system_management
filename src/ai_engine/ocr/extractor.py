import os
from pypdf import PdfReader

class DocumentExtractor:
    @staticmethod
    def extract_text(file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return DocumentExtractor._extract_from_pdf(file_path)
        elif ext in [".txt", ".md"]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read().strip()
        else:
            try:
                return DocumentExtractor._extract_from_pdf(file_path)
            except Exception:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read().strip()

    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        reader = PdfReader(file_path)
        extracted_pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_pages.append(text)
        return "\n".join(extracted_pages).strip()

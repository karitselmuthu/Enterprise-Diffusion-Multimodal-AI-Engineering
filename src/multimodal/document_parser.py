"""Extract embedded PDF text, plain text, or optional OCR from images."""

from __future__ import annotations

from io import BytesIO


def extract_document(data: bytes, filename: str) -> dict:
    if len(data) > 5_000_000:
        raise ValueError("document exceeds 5 MB limit")
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if suffix == "txt":
        return {"text": data.decode("utf-8"), "method": "utf8", "pages": 1}
    if suffix == "pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("pypdf is required to extract PDF text") from exc
        try:
            reader = PdfReader(BytesIO(data))
            if len(reader.pages) > 100:
                raise ValueError("PDF exceeds 100 page limit")
            texts = [(page.extract_text() or "") for page in reader.pages]
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError("invalid or unreadable PDF") from exc
        return {"text": "\n".join(texts), "method": "embedded_pdf_text", "pages": len(texts), "note": "Scanned pages require OCR; empty text does not imply a blank document." if not any(texts) else ""}
    if suffix in {"png", "jpg", "jpeg", "ppm"}:
        try:
            from PIL import Image
            import pytesseract
        except ImportError:
            return {"text": "", "method": "unavailable", "pages": 1, "note": "Install Pillow, pytesseract and the Tesseract executable for image OCR."}
        try:
            text = pytesseract.image_to_string(Image.open(BytesIO(data)))
        except Exception as exc:
            raise RuntimeError("OCR failed; check Tesseract installation and image format") from exc
        return {"text": text, "method": "tesseract_ocr", "pages": 1}
    raise ValueError("supported documents: .txt, .pdf, .png, .jpg, .jpeg, .ppm")

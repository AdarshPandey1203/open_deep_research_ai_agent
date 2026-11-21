import os
import logging

logger = logging.getLogger(__name__)

def read_pdf(file_path: str) -> str:
    """Extracts text from PDF using pdfminer or pypdf."""
    # Attempt 1: pdfminer (standard in Python environment)
    try:
        from pdfminer.high_level import extract_text
        text = extract_text(file_path)
        if text and text.strip():
            return text.strip()
    except Exception as e:
        logger.debug(f"pdfminer extraction failed: {e}")

    # Attempt 2: pypdf / PyPDF2
    try:
        import pypdf
        reader = pypdf.PdfReader(file_path)
        pages_text = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages_text).strip()
        if text:
            return text
    except Exception:
        pass

    try:
        import PyPDF2
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            pages_text = [page.extract_text() or "" for page in reader.pages]
            text = "\n".join(pages_text).strip()
            if text:
                return text
    except Exception:
        pass

    return ""

def read_docx(file_path: str) -> str:
    """Extracts text from DOCX using docx2txt or docx."""
    try:
        import docx2txt
        text = docx2txt.process(file_path)
        if text and text.strip():
            return text.strip()
    except Exception as e:
        logger.debug(f"docx2txt extraction failed: {e}")

    try:
        import docx
        doc = docx.Document(file_path)
        full_text = [para.text for para in doc.paragraphs if para.text]
        return "\n".join(full_text).strip()
    except Exception:
        pass

    return ""

def read_plain_text(file_path: str) -> str:
    """Reads plain text files with multiple encoding fallbacks."""
    for encoding in ['utf-8', 'latin-1', 'cp1252', 'utf-16']:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read().strip()
        except UnicodeDecodeError:
            continue
        except Exception:
            break
    return ""

def read_document(file_path: str, max_chars: int = 25000) -> str:
    """
    Robust, cross-platform document reader.
    Supports PDF, DOCX, TXT, MD, CSV, JSON, and code files.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return ""

    _, ext = os.path.splitext(file_path.lower())
    extracted_text = ""

    try:
        if ext == '.pdf':
            extracted_text = read_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            extracted_text = read_docx(file_path)
        else:
            extracted_text = read_plain_text(file_path)

        # Fallback to textract if nothing extracted and textract is available
        if not extracted_text:
            try:
                import textract
                extracted_text = textract.process(file_path).decode('utf-8', errors='ignore').strip()
            except Exception:
                pass

        if len(extracted_text) > max_chars:
            extracted_text = extracted_text[:max_chars] + f"\n\n[... Truncated for token safety: {len(extracted_text)} total chars ...]"

        return extracted_text

    except Exception as e:
        logger.error(f"Error reading document {file_path}: {e}")
        return ""

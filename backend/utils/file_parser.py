"""
File Parsing Utilities

Supports parsing of multiple file formats:
- .txt (plain text)
- .docx (Microsoft Word)
- .pdf (PDF documents)
"""

import io
from pathlib import Path
from typing import BinaryIO
from docx import Document


async def parse_txt_file(file_content: bytes) -> str:
    """
    Parse plain text file.
    
    Args:
        file_content: Raw bytes from uploaded file
        
    Returns:
        Plain text content
    """
    try:
        # Try UTF-8 first
        return file_content.decode("utf-8")
    except UnicodeDecodeError:
        # Fallback to latin-1
        return file_content.decode("latin-1", errors="ignore")


async def parse_docx_file(file_content: bytes) -> str:
    """
    Parse Microsoft Word .docx file.
    
    Args:
        file_content: Raw bytes from uploaded file
        
    Returns:
        Extracted plain text content
    """
    file_stream = io.BytesIO(file_content)
    doc = Document(file_stream)
    
    # Extract all paragraphs
    paragraphs = [paragraph.text for paragraph in doc.paragraphs]
    
    # Join with newlines
    full_text = "\n".join(paragraphs)
    
    return full_text


async def parse_pdf_file(file_content: bytes) -> str:
    """
    Parse PDF file.
    
    Args:
        file_content: Raw bytes from uploaded file
        
    Returns:
        Extracted plain text content
        
    Note:
        This is a basic implementation using PyPDF2.
        For better OCR support, consider using libraries like pdfplumber or pytesseract.
    """
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        raise ImportError("PyPDF2 is required for PDF parsing. Install with: pip install PyPDF2")
    
    file_stream = io.BytesIO(file_content)
    reader = PdfReader(file_stream)
    
    # Extract text from all pages
    text_parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_parts.append(text)
    
    return "\n".join(text_parts)


async def parse_file(filename: str, file_content: bytes) -> str:
    """
    Parse file based on extension.
    
    Args:
        filename: Original filename with extension
        file_content: Raw bytes from uploaded file
        
    Returns:
        Extracted plain text content
        
    Raises:
        ValueError: If file extension is not supported
    """
    file_ext = Path(filename).suffix.lower()
    
    if file_ext == ".txt":
        return await parse_txt_file(file_content)
    elif file_ext == ".docx":
        return await parse_docx_file(file_content)
    elif file_ext == ".pdf":
        return await parse_pdf_file(file_content)
    else:
        raise ValueError(
            f"Unsupported file extension: {file_ext}. "
            f"Supported formats: .txt, .docx, .pdf"
        )


def is_supported_file(filename: str) -> bool:
    """
    Check if file extension is supported.
    
    Args:
        filename: Filename to check
        
    Returns:
        True if supported, False otherwise
    """
    supported_extensions = {".txt", ".docx", ".pdf"}
    file_ext = Path(filename).suffix.lower()
    return file_ext in supported_extensions

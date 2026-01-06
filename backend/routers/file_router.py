# backend/routers/file_router.py

from fastapi import APIRouter, File, UploadFile, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.service.file_service import upload_file_service, get_file_by_course_name
from backend.schema.file_schema import UploadFileResponse, FileInfoResponse


router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/upload", response_model=UploadFileResponse)
async def upload_file(
    course_name: str = Form(..., description="Unique course identifier (immutable)"),
    file: UploadFile = File(..., description="File to upload (.pdf, .docx, .txt)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and parse course file.
    
    Process:
    1. Validate course_name uniqueness
    2. Validate file extension (.pdf, .docx, .txt)
    3. Parse file content to plain text
    4. Save to database with course_name
    
    Returns:
        - course_name: The course identifier
        - file_id: UUID of created file record
        
    Raises:
        - 400: Course name already exists or unsupported file format
        - 500: Error parsing or saving file
    """
    return await upload_file_service(course_name, file, db)


@router.get("/{course_name}", response_model=FileInfoResponse)
async def get_file(
    course_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get file information by course_name.
    
    Returns file metadata including extracted text.
    """
    file_obj = await get_file_by_course_name(course_name, db)
    return FileInfoResponse(
        file_id=file_obj.id,
        course_name=file_obj.course_name,
        full_text=file_obj.full_text,
        created_at=str(file_obj.created_at)
    )

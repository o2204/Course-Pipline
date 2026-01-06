# backend/service/file_service.py

from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from backend.repo.file_repo import FileRepository
from backend.utils.file_parser import parse_file, is_supported_file
from backend.schema.file_schema import UploadFileResponse


async def upload_file_service(
    course_name: str,
    file: UploadFile,
    db: AsyncSession
) -> UploadFileResponse:
    """
    Upload and parse file service.
    
    Process:
    1. Validate course_name uniqueness
    2. Validate file extension
    3. Parse file content to plain text
    4. Save to database
    
    Args:
        course_name: Unique course identifier (immutable)
        file: Uploaded file (.pdf, .docx, .txt)
        db: Database session
        
    Returns:
        UploadFileResponse with course_name and file_id
        
    Raises:
        HTTPException: If course_name exists or file format unsupported
    """
    file_repo = FileRepository(db)
    
    # 1. Validate course_name uniqueness
    if await file_repo.exists(course_name):
        raise HTTPException(
            status_code=400,
            detail=f"Course '{course_name}' already exists. Course names must be unique."
        )
    
    # 2. Validate file extension
    if file.filename and not is_supported_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported formats: .txt, .docx, .pdf"
        )
    
    # 3. Parse file content
    try:
        file_content = await file.read()
        full_text = await parse_file(file.filename or "file.txt", file_content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing file: {str(e)}"
        )
    
    # 4. Save to database
    try:
        created_file = await file_repo.create_file(
            course_name=course_name,
            full_text=full_text
        )
        
        return UploadFileResponse(
            course_name=created_file.course_name,
            file_id=created_file.id,
            message="File uploaded and processed successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saving file: {str(e)}"
        )


async def get_file_by_course_name(
    course_name: str,
    db: AsyncSession
):
    """Get file by course_name."""
    file_repo = FileRepository(db)
    file_obj = await file_repo.get_by_course_name(course_name)
    
    if not file_obj:
        raise HTTPException(
            status_code=404,
            detail=f"Course '{course_name}' not found"
        )
    
    return file_obj

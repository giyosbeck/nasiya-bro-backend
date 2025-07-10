from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
import aiofiles
from datetime import datetime
from pathlib import Path
import mimetypes
from PIL import Image
import io

from app.db.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.core.config import settings
from pydantic import BaseModel

router = APIRouter()

class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    file_path: str
    file_size: int
    content_type: str
    uploaded_at: datetime

class MultipleFileUploadResponse(BaseModel):
    files: List[FileUploadResponse]
    total_files: int

# Allowed file types
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/mov", "video/quicktime", "video/avi", "video/x-msvideo", "video/webm"}

# Maximum file sizes (in bytes)
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB

def validate_file_type(file: UploadFile, allowed_types: set) -> bool:
    """Validate file type based on content type"""
    if file.content_type not in allowed_types:
        return False
    return True

def validate_file_size(file: UploadFile, max_size: int) -> bool:
    """Validate file size"""
    # Note: file.size might not be available in all cases
    # We'll do additional validation after reading the file
    return True

async def save_file(file: UploadFile, subdirectory: str) -> FileUploadResponse:
    """Save uploaded file to disk and return file info"""
    # Generate unique filename
    file_extension = Path(file.filename or "").suffix.lower()
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Create directory path
    upload_dir = Path(settings.UPLOAD_FOLDER) / subdirectory
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / unique_filename
    
    # Read and validate file content
    content = await file.read()
    file_size = len(content)
    
    # Validate file size
    max_size = MAX_VIDEO_SIZE if file.content_type in ALLOWED_VIDEO_TYPES else MAX_IMAGE_SIZE
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)"
        )
    
    # Additional validation for images
    if file.content_type in ALLOWED_IMAGE_TYPES:
        try:
            # Validate image and potentially resize
            image = Image.open(io.BytesIO(content))
            
            # Fix image orientation based on EXIF data
            try:
                # Get EXIF data
                exif = image._getexif()
                if exif is not None:
                    orientation = exif.get(274)  # 274 is the EXIF orientation tag
                    if orientation == 3:
                        image = image.rotate(180, expand=True)
                    elif orientation == 6:
                        image = image.rotate(270, expand=True)
                    elif orientation == 8:
                        image = image.rotate(90, expand=True)
            except (AttributeError, KeyError, TypeError):
                # If EXIF data is not available or readable, continue without rotation
                pass
            
            # Convert RGBA to RGB if necessary
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])
                image = background
            
            # Resize if too large (max 1920x1080)
            max_width, max_height = 1920, 1080
            if image.width > max_width or image.height > max_height:
                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                # Save optimized image (without EXIF data to prevent further rotation issues)
                buffer = io.BytesIO()
                image.save(buffer, format='JPEG', quality=85, optimize=True, exif=b'')
                content = buffer.getvalue()
                file_size = len(content)
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image file: {str(e)}"
            )
    
    # Save file to disk
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    return FileUploadResponse(
        file_id=unique_filename.split('.')[0],
        filename=file.filename or unique_filename,
        file_path=str(file_path.relative_to(Path(settings.UPLOAD_FOLDER))),
        file_size=file_size,
        content_type=file.content_type or "application/octet-stream",
        uploaded_at=datetime.now()
    )

@router.post("/upload-passport", response_model=FileUploadResponse)
async def upload_passport_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload passport image for client verification"""
    # Validate file type
    if not validate_file_type(file, ALLOWED_IMAGE_TYPES):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    
    # Save file
    try:
        file_info = await save_file(file, "passports")
        return file_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

@router.post("/upload-agreement", response_model=MultipleFileUploadResponse)
async def upload_agreement_images(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload multiple agreement document images"""
    if len(files) > 10:  # Limit to 10 files
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 files allowed per upload"
        )
    
    uploaded_files = []
    
    for file in files:
        # Validate file type
        if not validate_file_type(file, ALLOWED_IMAGE_TYPES):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type for {file.filename}. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}"
            )
        
        try:
            file_info = await save_file(file, "agreements")
            uploaded_files.append(file_info)
        except Exception as e:
            # Clean up already uploaded files if one fails
            for uploaded_file in uploaded_files:
                try:
                    os.remove(Path(settings.UPLOAD_FOLDER) / uploaded_file.file_path)
                except:
                    pass
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload {file.filename}: {str(e)}"
            )
    
    return MultipleFileUploadResponse(
        files=uploaded_files,
        total_files=len(uploaded_files)
    )

@router.post("/upload-video", response_model=FileUploadResponse)
async def upload_loan_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload video recording for loan agreement"""
    # Validate file type
    if not validate_file_type(file, ALLOWED_VIDEO_TYPES):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_VIDEO_TYPES)}"
        )
    
    # Save file
    try:
        file_info = await save_file(file, "videos")
        return file_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload video: {str(e)}"
        )

@router.get("/serve/{file_path:path}")
async def serve_file(
    file_path: str
):
    """Serve uploaded files (public access for media display)"""
    full_path = Path(settings.UPLOAD_FOLDER) / file_path
    
    if not full_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Basic security check - ensure file is within upload directory
    try:
        full_path.resolve().relative_to(Path(settings.UPLOAD_FOLDER).resolve())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Determine content type
    content_type, _ = mimetypes.guess_type(str(full_path))
    if not content_type:
        content_type = "application/octet-stream"
    
    return FileResponse(
        path=str(full_path),
        media_type=content_type,
        filename=full_path.name
    )

@router.delete("/delete/{file_path:path}")
async def delete_file(
    file_path: str,
    current_user: User = Depends(get_current_user)
):
    """Delete uploaded file (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete files"
        )
    
    full_path = Path(settings.UPLOAD_FOLDER) / file_path
    
    if not full_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    try:
        full_path.resolve().relative_to(Path(settings.UPLOAD_FOLDER).resolve())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        os.remove(full_path)
        return {"message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )

@router.get("/info/{file_path:path}")
async def get_file_info(
    file_path: str,
    current_user: User = Depends(get_current_user)
):
    """Get file information"""
    full_path = Path(settings.UPLOAD_FOLDER) / file_path
    
    if not full_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    try:
        full_path.resolve().relative_to(Path(settings.UPLOAD_FOLDER).resolve())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    stat = full_path.stat()
    content_type, _ = mimetypes.guess_type(str(full_path))
    
    return {
        "filename": full_path.name,
        "file_path": file_path,
        "file_size": stat.st_size,
        "content_type": content_type or "application/octet-stream",
        "created_at": datetime.fromtimestamp(stat.st_ctime),
        "modified_at": datetime.fromtimestamp(stat.st_mtime)
    }
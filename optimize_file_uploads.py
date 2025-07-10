#!/usr/bin/env python3
"""
File upload optimization script
Adds async file processing and validation
"""

import os
import shutil
from pathlib import Path

def optimize_file_endpoints():
    """Update file endpoints for better performance"""
    
    files_endpoint = "app/api/api_v1/endpoints/files.py"
    
    if not os.path.exists(files_endpoint):
        print(f"Creating optimized {files_endpoint}")
        
        # Create the optimized files endpoint
        content = '''from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
import aiofiles
import uuid
import os
from typing import List
from PIL import Image
import asyncio

from app.db.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.core.config import settings

router = APIRouter()

# Allowed file types
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/jpg"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/avi", "video/webm"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50MB

async def validate_and_compress_image(file: UploadFile, max_size: tuple = (1920, 1080)) -> bytes:
    """Validate and compress image file"""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    
    content = await file.read()
    
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {MAX_IMAGE_SIZE // (1024*1024)}MB"
        )
    
    # Compress image
    try:
        from io import BytesIO
        image = Image.open(BytesIO(content))
        
        # Convert to RGB if necessary
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        
        # Resize if too large
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save compressed
        output = BytesIO()
        image.save(output, format="JPEG", quality=85, optimize=True)
        return output.getvalue()
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image file: {str(e)}"
        )

async def validate_video(file: UploadFile) -> bytes:
    """Validate video file"""
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_VIDEO_TYPES)}"
        )
    
    content = await file.read()
    
    if len(content) > MAX_VIDEO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {MAX_VIDEO_SIZE // (1024*1024)}MB"
        )
    
    return content

@router.post("/upload-passport")
async def upload_passport_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload and compress passport image"""
    try:
        # Validate and compress
        compressed_content = await validate_and_compress_image(file)
        
        # Generate unique filename
        file_extension = "jpg"  # Always save as JPEG after compression
        filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = Path(settings.UPLOAD_FOLDER) / "passports" / filename
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save file asynchronously
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(compressed_content)
        
        return {
            "filename": filename,
            "file_path": f"passports/{filename}",
            "url": f"/api/v1/files/serve/passports/{filename}",
            "size": len(compressed_content)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )

@router.post("/upload-agreement")
async def upload_agreement_images(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload multiple agreement images"""
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 files allowed"
        )
    
    uploaded_files = []
    
    try:
        # Process files concurrently
        tasks = []
        for file in files:
            tasks.append(validate_and_compress_image(file))
        
        compressed_contents = await asyncio.gather(*tasks)
        
        # Save files
        for i, (file, content) in enumerate(zip(files, compressed_contents)):
            filename = f"{uuid.uuid4()}.jpg"
            file_path = Path(settings.UPLOAD_FOLDER) / "agreements" / filename
            
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save file asynchronously
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(content)
            
            uploaded_files.append({
                "filename": filename,
                "file_path": f"agreements/{filename}",
                "url": f"/api/v1/files/serve/agreements/{filename}",
                "size": len(content)
            })
        
        return {"files": uploaded_files}
    
    except HTTPException:
        raise
    except Exception as e:
        # Cleanup any uploaded files on error
        for file_info in uploaded_files:
            try:
                os.remove(Path(settings.UPLOAD_FOLDER) / file_info["file_path"])
            except:
                pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )

@router.post("/upload-video")
async def upload_loan_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload loan agreement video"""
    try:
        # Validate video
        content = await validate_video(file)
        
        # Generate unique filename
        file_extension = file.filename.split(".")[-1].lower() if file.filename else "mp4"
        filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = Path(settings.UPLOAD_FOLDER) / "videos" / filename
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save file asynchronously
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)
        
        return {
            "filename": filename,
            "file_path": f"videos/{filename}",
            "url": f"/api/v1/files/serve/videos/{filename}",
            "size": len(content)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video upload failed: {str(e)}"
        )

@router.get("/serve/{file_type}/{filename}")
async def serve_file(file_type: str, filename: str):
    """Serve uploaded files"""
    allowed_types = ["passports", "agreements", "videos"]
    
    if file_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File type not found"
        )
    
    file_path = Path(settings.UPLOAD_FOLDER) / file_type / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )

@router.delete("/delete/{file_type}/{filename}")
async def delete_file(
    file_type: str,
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Delete uploaded file"""
    allowed_types = ["passports", "agreements", "videos"]
    
    if file_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File type not found"
        )
    
    file_path = Path(settings.UPLOAD_FOLDER) / file_type / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    try:
        os.remove(file_path)
        return {"message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )
'''
        
        # Write the optimized file
        with open(files_endpoint, 'w') as f:
            f.write(content)
        
        print("✓ Created optimized file upload endpoints")
    else:
        print("✓ File endpoints already exist")

if __name__ == "__main__":
    optimize_file_endpoints()
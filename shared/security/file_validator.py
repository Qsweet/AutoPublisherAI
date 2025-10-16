"""
File Upload Validation Utilities

Provides comprehensive file upload validation to prevent:
- Malicious file uploads
- File type spoofing
- Oversized files
- Dangerous file extensions
"""

import magic
import hashlib
from pathlib import Path
from typing import Optional, List, Tuple
from fastapi import UploadFile, HTTPException


class FileValidator:
    """
    Comprehensive file upload validator.
    """
    
    # Allowed MIME types by category
    ALLOWED_IMAGES = [
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
        'image/svg+xml',
    ]
    
    ALLOWED_DOCUMENTS = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/plain',
        'text/csv',
    ]
    
    ALLOWED_AUDIO = [
        'audio/mpeg',
        'audio/wav',
        'audio/ogg',
        'audio/mp4',
    ]
    
    ALLOWED_VIDEO = [
        'video/mp4',
        'video/mpeg',
        'video/quicktime',
        'video/webm',
    ]
    
    # Dangerous extensions
    DANGEROUS_EXTENSIONS = [
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr',
        '.vbs', '.js', '.jar', '.msi', '.app', '.deb',
        '.rpm', '.dmg', '.pkg', '.sh', '.bash', '.ps1',
    ]
    
    # Maximum file sizes (in bytes)
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_DOCUMENT_SIZE = 50 * 1024 * 1024  # 50MB
    MAX_AUDIO_SIZE = 100 * 1024 * 1024  # 100MB
    MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB
    
    @staticmethod
    async def validate_upload(
        file: UploadFile,
        allowed_types: Optional[List[str]] = None,
        max_size: Optional[int] = None,
        check_content: bool = True
    ) -> Tuple[bool, str]:
        """
        Validate an uploaded file.
        
        Args:
            file: FastAPI UploadFile object
            allowed_types: List of allowed MIME types (None = all common types)
            max_size: Maximum file size in bytes
            check_content: Whether to check actual file content (vs just extension)
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check filename
        if not file.filename:
            return False, "No filename provided"
        
        # Sanitize filename
        from .sanitizer import InputSanitizer
        safe_filename = InputSanitizer.sanitize_filename(file.filename)
        
        # Check dangerous extensions
        file_ext = Path(safe_filename).suffix.lower()
        if file_ext in FileValidator.DANGEROUS_EXTENSIONS:
            return False, f"File type {file_ext} is not allowed"
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Reset file pointer
        await file.seek(0)
        
        # Check file size
        if max_size and file_size > max_size:
            return False, f"File size ({file_size} bytes) exceeds maximum ({max_size} bytes)"
        
        # Check content type if requested
        if check_content:
            # Detect actual MIME type from content
            mime = magic.from_buffer(content, mime=True)
            
            # Default allowed types
            if allowed_types is None:
                allowed_types = (
                    FileValidator.ALLOWED_IMAGES +
                    FileValidator.ALLOWED_DOCUMENTS +
                    FileValidator.ALLOWED_AUDIO +
                    FileValidator.ALLOWED_VIDEO
                )
            
            if mime not in allowed_types:
                return False, f"File type {mime} is not allowed"
            
            # Check size based on type
            if mime in FileValidator.ALLOWED_IMAGES and file_size > FileValidator.MAX_IMAGE_SIZE:
                return False, f"Image size exceeds maximum ({FileValidator.MAX_IMAGE_SIZE} bytes)"
            
            if mime in FileValidator.ALLOWED_DOCUMENTS and file_size > FileValidator.MAX_DOCUMENT_SIZE:
                return False, f"Document size exceeds maximum ({FileValidator.MAX_DOCUMENT_SIZE} bytes)"
            
            if mime in FileValidator.ALLOWED_AUDIO and file_size > FileValidator.MAX_AUDIO_SIZE:
                return False, f"Audio size exceeds maximum ({FileValidator.MAX_AUDIO_SIZE} bytes)"
            
            if mime in FileValidator.ALLOWED_VIDEO and file_size > FileValidator.MAX_VIDEO_SIZE:
                return False, f"Video size exceeds maximum ({FileValidator.MAX_VIDEO_SIZE} bytes)"
        
        return True, "File is valid"
    
    @staticmethod
    async def validate_image(
        file: UploadFile,
        max_size: int = MAX_IMAGE_SIZE,
        allowed_formats: Optional[List[str]] = None
    ) -> Tuple[bool, str]:
        """
        Validate an image upload.
        
        Args:
            file: FastAPI UploadFile object
            max_size: Maximum file size in bytes
            allowed_formats: List of allowed image formats
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if allowed_formats is None:
            allowed_formats = FileValidator.ALLOWED_IMAGES
        
        return await FileValidator.validate_upload(
            file,
            allowed_types=allowed_formats,
            max_size=max_size,
            check_content=True
        )
    
    @staticmethod
    def calculate_hash(content: bytes, algorithm: str = 'sha256') -> str:
        """
        Calculate hash of file content.
        
        Args:
            content: File content as bytes
            algorithm: Hash algorithm (md5, sha1, sha256, sha512)
        
        Returns:
            Hex digest of hash
        """
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(content)
        return hash_obj.hexdigest()
    
    @staticmethod
    async def scan_for_malware(file: UploadFile) -> Tuple[bool, str]:
        """
        Basic malware scanning (checks for suspicious patterns).
        
        Note: For production, integrate with proper antivirus API like ClamAV.
        
        Args:
            file: FastAPI UploadFile object
        
        Returns:
            Tuple of (is_safe, message)
        """
        content = await file.read()
        await file.seek(0)
        
        # Check for executable headers
        if content.startswith(b'MZ'):  # Windows executable
            return False, "Executable file detected"
        
        if content.startswith(b'\x7fELF'):  # Linux executable
            return False, "Executable file detected"
        
        if content.startswith(b'\xca\xfe\xba\xbe'):  # Mach-O (macOS)
            return False, "Executable file detected"
        
        # Check for script shebangs
        if content.startswith(b'#!/'):
            return False, "Script file detected"
        
        # Check for suspicious patterns
        suspicious_patterns = [
            b'eval(',
            b'exec(',
            b'system(',
            b'shell_exec(',
            b'passthru(',
            b'<script',
            b'javascript:',
        ]
        
        content_lower = content.lower()
        for pattern in suspicious_patterns:
            if pattern in content_lower:
                return False, f"Suspicious pattern detected: {pattern.decode('utf-8', errors='ignore')}"
        
        return True, "File appears safe"


# FastAPI dependency for file validation
async def validate_file_upload(
    file: UploadFile,
    allowed_types: Optional[List[str]] = None,
    max_size: Optional[int] = None
) -> UploadFile:
    """
    FastAPI dependency for validating file uploads.
    
    Args:
        file: Uploaded file
        allowed_types: Allowed MIME types
        max_size: Maximum file size
    
    Returns:
        The file if valid
    
    Raises:
        HTTPException: If file is invalid
    """
    is_valid, error_message = await FileValidator.validate_upload(
        file,
        allowed_types=allowed_types,
        max_size=max_size
    )
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # Basic malware scan
    is_safe, scan_message = await FileValidator.scan_for_malware(file)
    if not is_safe:
        raise HTTPException(status_code=400, detail=f"Security check failed: {scan_message}")
    
    return file


async def validate_image_upload(file: UploadFile) -> UploadFile:
    """FastAPI dependency for validating image uploads."""
    is_valid, error_message = await FileValidator.validate_image(file)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    return file


"""
Input Sanitization Utilities

Provides functions to sanitize and validate user inputs to prevent:
- SQL Injection
- XSS (Cross-Site Scripting)
- Command Injection
- Path Traversal
- HTML Injection
"""

import re
import html
from typing import Optional, List
from pathlib import Path
import bleach


class InputSanitizer:
    """
    Comprehensive input sanitization utility.
    """
    
    # Dangerous patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|\#|\/\*|\*\/)",
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
        r"(;.*--)",
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
    ]
    
    COMMAND_INJECTION_PATTERNS = [
        r"[;&|`$()]",
        r"\$\{.*\}",
        r"\$\(.*\)",
    ]
    
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.",
        r"~\/",
    ]
    
    @staticmethod
    def sanitize_string(
        text: str,
        max_length: Optional[int] = None,
        allow_html: bool = False,
        allowed_tags: Optional[List[str]] = None
    ) -> str:
        """
        Sanitize a string input.
        
        Args:
            text: Input text to sanitize
            max_length: Maximum allowed length
            allow_html: Whether to allow HTML tags
            allowed_tags: List of allowed HTML tags if allow_html is True
        
        Returns:
            Sanitized string
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Trim whitespace
        text = text.strip()
        
        # Enforce max length
        if max_length and len(text) > max_length:
            text = text[:max_length]
        
        # Handle HTML
        if allow_html:
            # Use bleach to clean HTML
            if allowed_tags is None:
                allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li']
            
            text = bleach.clean(
                text,
                tags=allowed_tags,
                attributes={'a': ['href', 'title']},
                strip=True
            )
        else:
            # Escape HTML entities
            text = html.escape(text)
        
        return text
    
    @staticmethod
    def sanitize_email(email: str) -> str:
        """
        Sanitize and validate email address.
        
        Args:
            email: Email address to sanitize
        
        Returns:
            Sanitized email
        
        Raises:
            ValueError: If email is invalid
        """
        email = email.strip().lower()
        
        # Basic email regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")
        
        # Check for dangerous patterns
        if any(re.search(pattern, email, re.IGNORECASE) 
               for pattern in InputSanitizer.SQL_INJECTION_PATTERNS):
            raise ValueError("Email contains suspicious patterns")
        
        return email
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and other attacks.
        
        Args:
            filename: Original filename
        
        Returns:
            Sanitized filename
        """
        # Remove any path components
        filename = Path(filename).name
        
        # Remove dangerous characters
        filename = re.sub(r'[^\w\s.-]', '', filename)
        
        # Remove multiple dots
        filename = re.sub(r'\.{2,}', '.', filename)
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')
        
        return filename
    
    @staticmethod
    def sanitize_url(url: str) -> str:
        """
        Sanitize URL to prevent XSS and other attacks.
        
        Args:
            url: URL to sanitize
        
        Returns:
            Sanitized URL
        
        Raises:
            ValueError: If URL is invalid or dangerous
        """
        url = url.strip()
        
        # Check for javascript: and data: protocols
        if re.match(r'^(javascript|data|vbscript):', url, re.IGNORECASE):
            raise ValueError("Dangerous URL protocol detected")
        
        # Must start with http:// or https://
        if not re.match(r'^https?://', url, re.IGNORECASE):
            raise ValueError("URL must start with http:// or https://")
        
        return url
    
    @staticmethod
    def check_sql_injection(text: str) -> bool:
        """
        Check if text contains potential SQL injection patterns.
        
        Args:
            text: Text to check
        
        Returns:
            True if suspicious patterns found, False otherwise
        """
        for pattern in InputSanitizer.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def check_xss(text: str) -> bool:
        """
        Check if text contains potential XSS patterns.
        
        Args:
            text: Text to check
        
        Returns:
            True if suspicious patterns found, False otherwise
        """
        for pattern in InputSanitizer.XSS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def check_command_injection(text: str) -> bool:
        """
        Check if text contains potential command injection patterns.
        
        Args:
            text: Text to check
        
        Returns:
            True if suspicious patterns found, False otherwise
        """
        for pattern in InputSanitizer.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, text):
                return True
        return False
    
    @staticmethod
    def check_path_traversal(path: str) -> bool:
        """
        Check if path contains path traversal attempts.
        
        Args:
            path: Path to check
        
        Returns:
            True if suspicious patterns found, False otherwise
        """
        for pattern in InputSanitizer.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, path):
                return True
        return False
    
    @staticmethod
    def sanitize_dict(
        data: dict,
        string_fields: Optional[List[str]] = None,
        max_length: int = 1000
    ) -> dict:
        """
        Sanitize all string values in a dictionary.
        
        Args:
            data: Dictionary to sanitize
            string_fields: List of fields to sanitize (None = all strings)
            max_length: Maximum length for strings
        
        Returns:
            Sanitized dictionary
        """
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                if string_fields is None or key in string_fields:
                    sanitized[key] = InputSanitizer.sanitize_string(
                        value,
                        max_length=max_length
                    )
                else:
                    sanitized[key] = value
            elif isinstance(value, dict):
                sanitized[key] = InputSanitizer.sanitize_dict(
                    value,
                    string_fields,
                    max_length
                )
            elif isinstance(value, list):
                sanitized[key] = [
                    InputSanitizer.sanitize_string(item, max_length=max_length)
                    if isinstance(item, str) else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized


# Convenience functions
def sanitize(text: str, **kwargs) -> str:
    """Shorthand for sanitize_string."""
    return InputSanitizer.sanitize_string(text, **kwargs)


def is_safe(text: str) -> bool:
    """
    Check if text is safe (no injection attempts).
    
    Returns:
        True if safe, False if suspicious
    """
    return not any([
        InputSanitizer.check_sql_injection(text),
        InputSanitizer.check_xss(text),
        InputSanitizer.check_command_injection(text),
        InputSanitizer.check_path_traversal(text),
    ])


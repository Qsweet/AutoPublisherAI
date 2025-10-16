"""
Article Data Models

Pydantic models for article generation requests and responses.
These models ensure type safety and automatic validation.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class LanguageCode(str, Enum):
    """Supported languages for content generation."""
    ARABIC = "ar"
    ENGLISH = "en"
    FRENCH = "fr"
    SPANISH = "es"


class SEOLevel(str, Enum):
    """SEO optimization levels."""
    BASIC = "basic"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


class ContentTone(str, Enum):
    """Content tone options."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    AUTHORITATIVE = "authoritative"
    CONVERSATIONAL = "conversational"


class ArticleGenerationRequest(BaseModel):
    """
    Request model for article generation.
    
    This defines all parameters that can be customized when
    requesting a new article.
    """
    
    topic: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="The main topic or subject for the article"
    )
    
    language: LanguageCode = Field(
        default=LanguageCode.ARABIC,
        description="Target language for the article"
    )
    
    target_length: int = Field(
        default=1500,
        ge=300,
        le=5000,
        description="Target word count for the article"
    )
    
    seo_level: SEOLevel = Field(
        default=SEOLevel.HIGH,
        description="Level of SEO optimization to apply"
    )
    
    tone: ContentTone = Field(
        default=ContentTone.PROFESSIONAL,
        description="Desired tone for the content"
    )
    
    target_keywords: Optional[List[str]] = Field(
        default=None,
        max_length=10,
        description="Specific keywords to target (optional)"
    )
    
    include_image: bool = Field(
        default=True,
        description="Whether to generate a featured image"
    )
    
    include_faq: bool = Field(
        default=True,
        description="Whether to include an FAQ section"
    )
    
    target_audience: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Description of target audience (optional)"
    )
    
    @validator('topic')
    def validate_topic(cls, v):
        """Ensure topic is not just whitespace."""
        if not v.strip():
            raise ValueError("Topic cannot be empty or just whitespace")
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "فوائد العمل عن بعد للشركات الناشئة",
                "language": "ar",
                "target_length": 1500,
                "seo_level": "high",
                "tone": "professional",
                "include_image": True,
                "include_faq": True
            }
        }


class KeywordAnalysis(BaseModel):
    """Analysis of keywords for the topic."""
    
    primary_keyword: str = Field(..., description="Main keyword")
    secondary_keywords: List[str] = Field(default_factory=list, description="Related keywords")
    long_tail_keywords: List[str] = Field(default_factory=list, description="Long-tail variations")
    search_volume_estimate: Optional[str] = Field(None, description="Estimated search volume")
    competition_level: Optional[str] = Field(None, description="Competition level")


class ArticleSection(BaseModel):
    """A section of the article."""
    
    heading: str = Field(..., description="Section heading (H2 or H3)")
    content: str = Field(..., description="Section content")
    heading_level: int = Field(default=2, ge=2, le=3, description="Heading level (2 or 3)")


class FAQItem(BaseModel):
    """A single FAQ item."""
    
    question: str = Field(..., description="The question")
    answer: str = Field(..., description="The answer")


class GeneratedImage(BaseModel):
    """Information about a generated image."""
    
    url: str = Field(..., description="URL of the generated image")
    prompt: str = Field(..., description="Prompt used to generate the image")
    alt_text: str = Field(..., description="SEO-optimized alt text")
    width: Optional[int] = Field(None, description="Image width in pixels")
    height: Optional[int] = Field(None, description="Image height in pixels")


class ArticleMetadata(BaseModel):
    """SEO metadata for the article."""
    
    title: str = Field(..., max_length=60, description="SEO-optimized title")
    meta_description: str = Field(..., max_length=160, description="Meta description")
    slug: str = Field(..., description="URL-friendly slug")
    tags: List[str] = Field(default_factory=list, description="Article tags")
    categories: List[str] = Field(default_factory=list, description="Article categories")


class ArticleGenerationResponse(BaseModel):
    """
    Complete response for a generated article.
    
    This contains all the generated content, metadata, and analysis.
    """
    
    # Core content
    title: str = Field(..., description="Article title")
    introduction: str = Field(..., description="Article introduction/hook")
    sections: List[ArticleSection] = Field(..., description="Main article sections")
    conclusion: str = Field(..., description="Article conclusion")
    
    # Optional sections
    faq: Optional[List[FAQItem]] = Field(None, description="FAQ section")
    
    # SEO & Metadata
    metadata: ArticleMetadata = Field(..., description="SEO metadata")
    keyword_analysis: KeywordAnalysis = Field(..., description="Keyword analysis")
    
    # Images
    featured_image: Optional[GeneratedImage] = Field(None, description="Featured image")
    
    # Statistics
    word_count: int = Field(..., description="Actual word count")
    estimated_reading_time: int = Field(..., description="Reading time in minutes")
    
    # Generation info
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    language: LanguageCode = Field(..., description="Content language")
    
    # Full HTML (optional, for direct publishing)
    html_content: Optional[str] = Field(None, description="Complete HTML version")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "فوائد العمل عن بعد: دليل شامل للشركات الناشئة",
                "word_count": 1523,
                "estimated_reading_time": 6,
                "language": "ar"
            }
        }


class ArticleGenerationStatus(BaseModel):
    """Status of an article generation task."""
    
    task_id: str = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Current status (pending, processing, completed, failed)")
    progress: int = Field(default=0, ge=0, le=100, description="Progress percentage")
    message: Optional[str] = Field(None, description="Status message")
    result: Optional[ArticleGenerationResponse] = Field(None, description="Result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


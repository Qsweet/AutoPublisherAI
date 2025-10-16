"""
Content Strategy Models

Data models for content strategy planning and analysis.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field
from enum import Enum


class IndustryType(str, Enum):
    """Industry categories."""
    TECHNOLOGY = "technology"
    BUSINESS = "business"
    HEALTH = "health"
    EDUCATION = "education"
    LIFESTYLE = "lifestyle"
    FINANCE = "finance"
    MARKETING = "marketing"
    ECOMMERCE = "ecommerce"
    TRAVEL = "travel"
    FOOD = "food"
    FASHION = "fashion"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    OTHER = "other"


class ContentType(str, Enum):
    """Content types."""
    BLOG_POST = "blog_post"
    TUTORIAL = "tutorial"
    GUIDE = "guide"
    LISTICLE = "listicle"
    CASE_STUDY = "case_study"
    REVIEW = "review"
    NEWS = "news"
    OPINION = "opinion"


class PublishingFrequency(str, Enum):
    """Publishing frequency options."""
    DAILY = "daily"
    EVERY_OTHER_DAY = "every_other_day"
    THREE_TIMES_WEEK = "three_times_week"
    TWICE_WEEK = "twice_week"
    WEEKLY = "weekly"


class StrategyRequest(BaseModel):
    """Request model for generating content strategy."""
    
    industry: IndustryType = Field(
        ...,
        description="Industry or niche of the website"
    )
    
    target_audience: str = Field(
        ...,
        description="Description of target audience",
        min_length=10,
        max_length=500
    )
    
    main_topics: List[str] = Field(
        ...,
        description="Main topics to cover (3-10 topics)",
        min_length=3,
        max_length=10
    )
    
    competitors: Optional[List[str]] = Field(
        default=None,
        description="Competitor websites (optional)"
    )
    
    current_traffic: Optional[int] = Field(
        default=None,
        description="Current monthly traffic (if available)"
    )
    
    target_traffic: Optional[int] = Field(
        default=None,
        description="Target monthly traffic goal"
    )
    
    publishing_frequency: PublishingFrequency = Field(
        default=PublishingFrequency.THREE_TIMES_WEEK,
        description="Desired publishing frequency"
    )
    
    language: str = Field(
        default="ar",
        description="Content language (ar, en, etc.)"
    )
    
    duration_days: int = Field(
        default=90,
        description="Strategy duration in days",
        ge=30,
        le=365
    )


class ArticleIdea(BaseModel):
    """Single article idea with metadata."""
    
    title: str = Field(..., description="Article title")
    
    description: str = Field(..., description="Brief description")
    
    content_type: ContentType = Field(..., description="Type of content")
    
    keywords: List[str] = Field(..., description="Target keywords")
    
    estimated_word_count: int = Field(..., description="Estimated word count")
    
    difficulty: str = Field(..., description="SEO difficulty: easy, medium, hard")
    
    estimated_traffic: int = Field(..., description="Estimated monthly traffic")
    
    priority: int = Field(..., description="Priority score (1-10)")
    
    suggested_publish_date: date = Field(..., description="Suggested publish date")


class WeeklyPlan(BaseModel):
    """Weekly content plan."""
    
    week_number: int = Field(..., description="Week number (1-13 for 90 days)")
    
    start_date: date = Field(..., description="Week start date")
    
    end_date: date = Field(..., description="Week end date")
    
    articles: List[ArticleIdea] = Field(..., description="Articles for this week")
    
    focus_topic: str = Field(..., description="Main topic focus for the week")
    
    estimated_traffic: int = Field(..., description="Estimated traffic for this week")


class TrafficProjection(BaseModel):
    """Traffic growth projection."""
    
    month: int = Field(..., description="Month number (1-3 for 90 days)")
    
    estimated_traffic: int = Field(..., description="Estimated monthly traffic")
    
    growth_percentage: float = Field(..., description="Growth percentage from previous month")
    
    new_articles: int = Field(..., description="Number of new articles in this month")


class KeywordCluster(BaseModel):
    """Keyword cluster for topic organization."""
    
    cluster_name: str = Field(..., description="Cluster name")
    
    main_keyword: str = Field(..., description="Main keyword")
    
    related_keywords: List[str] = Field(..., description="Related keywords")
    
    search_volume: int = Field(..., description="Estimated monthly search volume")
    
    difficulty: str = Field(..., description="SEO difficulty")
    
    article_count: int = Field(..., description="Number of articles in this cluster")


class ContentStrategy(BaseModel):
    """Complete content strategy response."""
    
    strategy_id: str = Field(..., description="Unique strategy ID")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    industry: IndustryType = Field(..., description="Industry")
    
    target_audience: str = Field(..., description="Target audience")
    
    duration_days: int = Field(..., description="Strategy duration")
    
    total_articles: int = Field(..., description="Total number of articles")
    
    keyword_clusters: List[KeywordCluster] = Field(..., description="Keyword clusters")
    
    weekly_plans: List[WeeklyPlan] = Field(..., description="Weekly content plans")
    
    traffic_projections: List[TrafficProjection] = Field(..., description="Traffic projections")
    
    summary: Dict[str, Any] = Field(..., description="Strategy summary")
    
    recommendations: List[str] = Field(..., description="Strategic recommendations")


class StrategyAnalysis(BaseModel):
    """Analysis of existing content strategy."""
    
    total_articles: int
    avg_word_count: int
    top_keywords: List[str]
    content_gaps: List[str]
    recommendations: List[str]


"""
PCD-Lite Schema Definitions
Defines data models for the Personalized Content Discovery prototype
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class QueryType(str, Enum):
    """Types of user queries"""
    VOICE = "voice"
    TEXT = "text"


class RecommendationStrategy(str, Enum):
    """A/B testing strategies"""
    POPULARITY = "A"  # Strategy A: Popularity-based
    SIMILARITY = "B"  # Strategy B: TF-IDF similarity


class Movie(BaseModel):
    """Movie data model"""
    id: int
    title: str
    genre: List[str]
    cast: List[str]
    overview: str
    runtime: int  # in minutes
    popularity: float
    release_year: int
    director: str
    rating: float


class ParsedFilters(BaseModel):
    """Parsed query filters"""
    genres: List[str] = []
    actors: List[str] = []
    runtime_min: Optional[int] = None
    runtime_max: Optional[int] = None
    vibe: Optional[str] = None  # e.g., "funny", "serious", "romantic"
    keywords: List[str] = []
    year_min: Optional[int] = None
    year_max: Optional[int] = None


class SearchRequest(BaseModel):
    """Search request model"""
    query: str
    query_type: QueryType = QueryType.TEXT
    session_id: Optional[str] = None
    user_id: Optional[str] = None


class SearchResponse(BaseModel):
    """Search response model"""
    request_id: str
    session_id: str
    variant: RecommendationStrategy
    parsed_filters: ParsedFilters
    recommendations: List[Movie]
    total_results: int
    processing_time_ms: float
    debug_info: Optional[Dict[str, Any]] = None


class ClickRequest(BaseModel):
    """Click tracking request"""
    request_id: str
    session_id: str
    movie_id: int
    position: int  # Position in recommendation list
    variant: RecommendationStrategy


class ClickResponse(BaseModel):
    """Click tracking response"""
    success: bool
    message: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str = "1.0.0"
    uptime_seconds: float


class DebugInfo(BaseModel):
    """Debug information for last query"""
    last_query: Optional[str] = None
    parsed_filters: Optional[ParsedFilters] = None
    variant: Optional[RecommendationStrategy] = None
    result_count: Optional[int] = None
    processing_time_ms: Optional[float] = None
    timestamp: Optional[datetime] = None


class EventLog(BaseModel):
    """Event logging model"""
    event_id: str
    session_id: str
    event_type: str  # "impression" or "click"
    variant: RecommendationStrategy
    movie_id: Optional[int] = None
    position: Optional[int] = None
    filters: Optional[ParsedFilters] = None
    timestamp: datetime
    request_id: str


class AnalyticsMetrics(BaseModel):
    """Analytics metrics model"""
    total_sessions: int
    total_impressions: int
    total_clicks: int
    ctr: float  # Click-through rate
    variant_a_impressions: int
    variant_a_clicks: int
    variant_a_ctr: float
    variant_b_impressions: int
    variant_b_clicks: int
    variant_b_ctr: float
    avg_processing_time_ms: float
    most_popular_genres: List[Dict[str, Any]]
    most_clicked_movies: List[Dict[str, Any]]

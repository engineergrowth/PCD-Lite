"""
PCD-Lite Main FastAPI Application
Personalized Content Discovery prototype for TiVo interview demo
"""

import time
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .schema import (
    SearchRequest, SearchResponse, ClickRequest, ClickResponse, 
    HealthResponse, DebugInfo, RecommendationStrategy, QueryType
)
from .data_loader import DataLoader
from .mapping import QueryParser, MetadataMapper
from .recs import RecommendationEngine
from .voice import VoiceProcessor
from .store import EventStore

# Initialize components
data_loader = DataLoader()
query_parser = QueryParser()
metadata_mapper = MetadataMapper()
recommendation_engine = RecommendationEngine(data_loader)
voice_processor = VoiceProcessor()
event_store = EventStore()

# Global state for debugging
last_query_info: Optional[DebugInfo] = None

# Lifespan event handler
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the application on startup"""
    print("PCD-Lite API starting up...")
    print(f"Loaded {len(data_loader.get_all_movies())} movies from catalog")
    print("API ready for requests!")
    yield
    print("PCD-Lite API shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="PCD-Lite API",
    description="Personalized Content Discovery prototype for TiVo interview demo",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        uptime_seconds=time.time()
    )

# Search endpoint
@app.post("/search", response_model=SearchResponse)
async def search_content(
    request: SearchRequest,
    x_request_id: Optional[str] = Header(None),
    fail: Optional[int] = Query(None)
):
    """Search for content based on natural language query"""
    start_time = time.time()
    
    # Generate request ID if not provided
    if not x_request_id:
        x_request_id = str(uuid.uuid4())
    
    # Simulate fault injection
    if fail == 1:
        raise HTTPException(status_code=500, detail="Simulated server error for testing")
    
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Process voice query if needed
        if request.query_type == QueryType.VOICE:
            voice_result = voice_processor.process_voice_query(request.query)
            processed_query = voice_result['corrected_query']
        else:
            processed_query = request.query
        
        # Parse query into structured filters
        parsed_filters = query_parser.parse_query(processed_query, request.query_type)
        
        # Normalize filters to core schema
        normalized_filters = metadata_mapper.normalize_filters(parsed_filters)
        
        # Assign A/B testing variant
        variant = recommendation_engine.assign_variant(session_id)
        
        # Get recommendations
        recommendations = recommendation_engine.get_recommendations(
            parsed_filters, variant, limit=10
        )
        
        # Log impressions for each recommended movie
        for i, movie in enumerate(recommendations):
            event_store.log_impression(
                session_id=session_id,
                variant=variant,
                movie_id=movie.id,
                position=i + 1,
                filters=parsed_filters,
                request_id=x_request_id
            )
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Store debug info
        global last_query_info
        last_query_info = DebugInfo(
            last_query=request.query,
            parsed_filters=parsed_filters,
            variant=variant,
            result_count=len(recommendations),
            processing_time_ms=processing_time_ms,
            timestamp=datetime.now()
        )
        
        # Create response
        response = SearchResponse(
            request_id=x_request_id,
            session_id=session_id,
            variant=variant,
            parsed_filters=parsed_filters,
            recommendations=recommendations,
            total_results=len(recommendations),
            processing_time_ms=processing_time_ms,
            debug_info={
                "normalized_filters": normalized_filters,
                "query_type": request.query_type.value,
                "voice_processing": voice_result if request.query_type == QueryType.VOICE else None
            }
        )
        
        return response
        
    except Exception as e:
        print(f"Error in search endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Click tracking endpoint
@app.post("/click", response_model=ClickResponse)
async def track_click(
    request: ClickRequest,
    x_request_id: Optional[str] = Header(None)
):
    """Track user clicks on recommended content"""
    try:
        # Generate request ID if not provided
        if not x_request_id:
            x_request_id = str(uuid.uuid4())
        
        # Log click event
        success = event_store.log_click(
            session_id=request.session_id,
            variant=request.variant,
            movie_id=request.movie_id,
            position=request.position,
            request_id=x_request_id
        )
        
        if success:
            return ClickResponse(
                success=True,
                message="Click tracked successfully"
            )
        else:
            return ClickResponse(
                success=False,
                message="Failed to track click"
            )
            
    except Exception as e:
        print(f"Error in click endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Debug endpoint
@app.get("/debug/last-query", response_model=DebugInfo)
async def get_last_query_debug():
    """Get debug information for the last query"""
    global last_query_info
    if last_query_info is None:
        raise HTTPException(status_code=404, detail="No queries have been processed yet")
    return last_query_info

# Analytics endpoint
@app.get("/analytics")
async def get_analytics(days: int = Query(7, ge=1, le=30)):
    """Get analytics metrics for the specified period"""
    try:
        metrics = event_store.get_analytics_metrics(days=days)
        return {
            "period_days": days,
            "metrics": metrics.dict()
        }
    except Exception as e:
        print(f"Error in analytics endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Variant performance endpoint
@app.get("/analytics/variants")
async def get_variant_performance(days: int = Query(7, ge=1, le=30)):
    """Get A/B testing performance metrics by variant"""
    try:
        performance = event_store.get_variant_performance(days=days)
        return {
            "period_days": days,
            "performance": performance
        }
    except Exception as e:
        print(f"Error in variant performance endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Session events endpoint
@app.get("/session/{session_id}/events")
async def get_session_events(session_id: str):
    """Get all events for a specific session"""
    try:
        events = event_store.get_session_events(session_id)
        return {
            "session_id": session_id,
            "event_count": len(events),
            "events": events
        }
    except Exception as e:
        print(f"Error in session events endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Voice suggestions endpoint
@app.get("/voice/suggestions")
async def get_voice_suggestions(partial_query: Optional[str] = Query(None)):
    """Get voice query suggestions based on partial input"""
    try:
        suggestions = voice_processor.get_voice_suggestions(partial_query or "")
        return {
            "partial_query": partial_query,
            "suggestions": suggestions
        }
    except Exception as e:
        print(f"Error in voice suggestions endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Movie catalog endpoint
@app.get("/catalog")
async def get_catalog(limit: int = Query(20, ge=1, le=100)):
    """Get movie catalog with optional limit"""
    try:
        movies = data_loader.get_all_movies()[:limit]
        return {
            "total_movies": len(data_loader.get_all_movies()),
            "returned_movies": len(movies),
            "movies": [movie.dict() for movie in movies]
        }
    except Exception as e:
        print(f"Error in catalog endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "detail": "The requested resource was not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred"}
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "PCD-Lite API - Personalized Content Discovery Prototype",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "search": "/search",
            "click": "/click",
            "debug": "/debug/last-query",
            "analytics": "/analytics",
            "catalog": "/catalog"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

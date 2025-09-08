"""
Unit tests for recommendation engine
"""

import pytest
from app.recs import RecommendationEngine, RecommendationMetrics
from app.schema import ParsedFilters, RecommendationStrategy, Movie
from app.data_loader import DataLoader

def test_recommendation_engine_initialization():
    """Test RecommendationEngine initialization"""
    data_loader = DataLoader()
    engine = RecommendationEngine(data_loader)
    
    assert engine is not None
    assert engine.data_loader is not None
    assert engine.tfidf_vectorizer is not None
    assert engine.tfidf_matrix is not None

def test_assign_variant():
    """Test variant assignment"""
    data_loader = DataLoader()
    engine = RecommendationEngine(data_loader)
    
    # Test consistent assignment for same session
    session_id = "test-session-123"
    variant1 = engine.assign_variant(session_id)
    variant2 = engine.assign_variant(session_id)
    
    assert variant1 == variant2
    assert variant1 in [RecommendationStrategy.POPULARITY, RecommendationStrategy.SIMILARITY]

def test_popularity_strategy():
    """Test popularity-based recommendation strategy"""
    data_loader = DataLoader()
    engine = RecommendationEngine(data_loader)
    
    filters = ParsedFilters(genres=["Comedy"])
    recommendations = engine._popularity_strategy(
        data_loader.get_all_movies(), filters, limit=5
    )
    
    assert isinstance(recommendations, list)
    assert len(recommendations) <= 5
    assert all(isinstance(movie, Movie) for movie in recommendations)

def test_similarity_strategy():
    """Test TF-IDF similarity recommendation strategy"""
    data_loader = DataLoader()
    engine = RecommendationEngine(data_loader)
    
    filters = ParsedFilters(keywords=["war", "love"])
    recommendations = engine._similarity_strategy(
        data_loader.get_all_movies(), filters, limit=5
    )
    
    assert isinstance(recommendations, list)
    assert len(recommendations) <= 5
    assert all(isinstance(movie, Movie) for movie in recommendations)

def test_get_recommendations_popularity():
    """Test getting recommendations with popularity strategy"""
    data_loader = DataLoader()
    engine = RecommendationEngine(data_loader)
    
    filters = ParsedFilters(genres=["Drama"])
    recommendations = engine.get_recommendations(
        filters, RecommendationStrategy.POPULARITY, limit=3
    )
    
    assert isinstance(recommendations, list)
    assert len(recommendations) <= 3
    assert all(isinstance(movie, Movie) for movie in recommendations)

def test_get_recommendations_similarity():
    """Test getting recommendations with similarity strategy"""
    data_loader = DataLoader()
    engine = RecommendationEngine(data_loader)
    
    filters = ParsedFilters(keywords=["action", "thriller"])
    recommendations = engine.get_recommendations(
        filters, RecommendationStrategy.SIMILARITY, limit=3
    )
    
    assert isinstance(recommendations, list)
    assert len(recommendations) <= 3
    assert all(isinstance(movie, Movie) for movie in recommendations)

def test_filter_movies_by_genre():
    """Test filtering movies by genre"""
    data_loader = DataLoader()
    engine = RecommendationEngine(data_loader)
    
    filters = ParsedFilters(genres=["Comedy"])
    filtered_movies = engine._filter_movies(filters)
    
    assert isinstance(filtered_movies, list)
    assert all(isinstance(movie, Movie) for movie in filtered_movies)
    # All filtered movies should have Comedy genre
    for movie in filtered_movies:
        assert any("Comedy" in genre for genre in movie.genre)

def test_filter_movies_by_actor():
    """Test filtering movies by actor"""
    data_loader = DataLoader()
    engine = RecommendationEngine(data_loader)
    
    filters = ParsedFilters(actors=["Tom Hanks"])
    filtered_movies = engine._filter_movies(filters)
    
    assert isinstance(filtered_movies, list)
    assert all(isinstance(movie, Movie) for movie in filtered_movies)
    # All filtered movies should have Tom Hanks in cast
    for movie in filtered_movies:
        assert any("Tom Hanks" in actor for actor in movie.cast)

def test_filter_movies_by_runtime():
    """Test filtering movies by runtime"""
    data_loader = DataLoader()
    engine = RecommendationEngine(data_loader)
    
    filters = ParsedFilters(runtime_max=120)
    filtered_movies = engine._filter_movies(filters)
    
    assert isinstance(filtered_movies, list)
    assert all(isinstance(movie, Movie) for movie in filtered_movies)
    # All filtered movies should be <= 120 minutes
    for movie in filtered_movies:
        assert movie.runtime <= 120

def test_filter_movies_by_year():
    """Test filtering movies by year"""
    data_loader = DataLoader()
    engine = RecommendationEngine(data_loader)
    
    filters = ParsedFilters(year_min=1990, year_max=2000)
    filtered_movies = engine._filter_movies(filters)
    
    assert isinstance(filtered_movies, list)
    assert all(isinstance(movie, Movie) for movie in filtered_movies)
    # All filtered movies should be from 1990-2000
    for movie in filtered_movies:
        assert 1990 <= movie.release_year <= 2000

def test_filter_movies_by_keywords():
    """Test filtering movies by keywords"""
    data_loader = DataLoader()
    engine = RecommendationEngine(data_loader)
    
    filters = ParsedFilters(keywords=["war", "love"])
    filtered_movies = engine._filter_movies(filters)
    
    assert isinstance(filtered_movies, list)
    assert all(isinstance(movie, Movie) for movie in filtered_movies)
    # All filtered movies should contain keywords in overview
    for movie in filtered_movies:
        overview_lower = movie.overview.lower()
        assert any(keyword in overview_lower for keyword in ["war", "love"])

def test_calculate_vibe_boost():
    """Test vibe boost calculation"""
    data_loader = DataLoader()
    engine = RecommendationEngine(data_loader)
    
    # Test with a comedy movie
    movie = Movie(
        id=1,
        title="Test Comedy",
        genre=["Comedy"],
        cast=["Test Actor"],
        overview="A funny comedy movie",
        runtime=90,
        popularity=8.0,
        release_year=2020,
        director="Test Director",
        rating=8.0
    )
    
    boost = engine._calculate_vibe_boost(movie, "funny")
    assert isinstance(boost, float)
    assert boost >= 0.0
    assert boost <= 1.0

def test_calculate_vibe_boost_unknown_vibe():
    """Test vibe boost calculation with unknown vibe"""
    data_loader = DataLoader()
    engine = RecommendationEngine(data_loader)
    
    movie = Movie(
        id=1,
        title="Test Movie",
        genre=["Drama"],
        cast=["Test Actor"],
        overview="A drama movie",
        runtime=90,
        popularity=8.0,
        release_year=2020,
        director="Test Director",
        rating=8.0
    )
    
    boost = engine._calculate_vibe_boost(movie, "unknown_vibe")
    assert boost == 0.0

def test_recommendation_metrics_calculate_ctr():
    """Test CTR calculation"""
    ctr = RecommendationMetrics.calculate_ctr(100, 5)
    assert ctr == 5.0
    
    ctr = RecommendationMetrics.calculate_ctr(100, 0)
    assert ctr == 0.0
    
    ctr = RecommendationMetrics.calculate_ctr(0, 5)
    assert ctr == 0.0

def test_recommendation_metrics_variant_performance():
    """Test variant performance calculation"""
    events = [
        {"variant": "A", "event_type": "impression"},
        {"variant": "A", "event_type": "impression"},
        {"variant": "A", "event_type": "click"},
        {"variant": "B", "event_type": "impression"},
        {"variant": "B", "event_type": "impression"},
        {"variant": "B", "event_type": "impression"},
        {"variant": "B", "event_type": "click"},
    ]
    
    performance = RecommendationMetrics.calculate_variant_performance(events)
    
    assert "variant_a" in performance
    assert "variant_b" in performance
    assert performance["variant_a"]["impressions"] == 2
    assert performance["variant_a"]["clicks"] == 1
    assert performance["variant_b"]["impressions"] == 3
    assert performance["variant_b"]["clicks"] == 1

def test_empty_filters():
    """Test recommendations with empty filters"""
    data_loader = DataLoader()
    engine = RecommendationEngine(data_loader)
    
    filters = ParsedFilters()
    recommendations = engine.get_recommendations(
        filters, RecommendationStrategy.POPULARITY, limit=5
    )
    
    assert isinstance(recommendations, list)
    assert len(recommendations) <= 5
    assert all(isinstance(movie, Movie) for movie in recommendations)

def test_limit_parameter():
    """Test recommendations with different limits"""
    data_loader = DataLoader()
    engine = RecommendationEngine(data_loader)
    
    filters = ParsedFilters(genres=["Drama"])
    
    # Test with limit 1
    recommendations_1 = engine.get_recommendations(
        filters, RecommendationStrategy.POPULARITY, limit=1
    )
    assert len(recommendations_1) <= 1
    
    # Test with limit 10
    recommendations_10 = engine.get_recommendations(
        filters, RecommendationStrategy.POPULARITY, limit=10
    )
    assert len(recommendations_10) <= 10

def test_no_matching_movies():
    """Test recommendations when no movies match filters"""
    data_loader = DataLoader()
    engine = RecommendationEngine(data_loader)
    
    # Use very specific filters that likely won't match
    filters = ParsedFilters(
        genres=["NonExistentGenre"],
        actors=["NonExistentActor"],
        runtime_max=1
    )
    
    recommendations = engine.get_recommendations(
        filters, RecommendationStrategy.POPULARITY, limit=5
    )
    
    assert isinstance(recommendations, list)
    assert len(recommendations) == 0

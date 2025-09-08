"""
Unit tests for query parsing and metadata mapping
"""

import pytest
from app.mapping import QueryParser, MetadataMapper
from app.schema import ParsedFilters, QueryType

def test_query_parser_initialization():
    """Test QueryParser initialization"""
    parser = QueryParser()
    assert parser is not None
    assert hasattr(parser, 'genre_mapping')
    assert hasattr(parser, 'actor_mapping')
    assert hasattr(parser, 'runtime_patterns')

def test_parse_simple_genre_query():
    """Test parsing simple genre query"""
    parser = QueryParser()
    filters = parser.parse_query("find comedy movies")
    
    assert isinstance(filters, ParsedFilters)
    assert "Comedy" in filters.genres
    assert len(filters.genres) > 0

def test_parse_actor_query():
    """Test parsing actor query"""
    parser = QueryParser()
    filters = parser.parse_query("show me movies with Tom Hanks")
    
    assert isinstance(filters, ParsedFilters)
    assert "Tom Hanks" in filters.actors
    assert len(filters.actors) > 0

def test_parse_runtime_query():
    """Test parsing runtime query"""
    parser = QueryParser()
    filters = parser.parse_query("find movies shorter than 120 minutes")
    
    assert isinstance(filters, ParsedFilters)
    assert filters.runtime_max == 120
    assert filters.runtime_min is None

def test_parse_complex_query():
    """Test parsing complex query with multiple filters"""
    parser = QueryParser()
    filters = parser.parse_query("find comedy movies with Tom Hanks shorter than 150 minutes")
    
    assert isinstance(filters, ParsedFilters)
    assert "Comedy" in filters.genres
    assert "Tom Hanks" in filters.actors
    assert filters.runtime_max == 150

def test_parse_vibe_query():
    """Test parsing vibe query"""
    parser = QueryParser()
    filters = parser.parse_query("find funny romantic movies")
    
    assert isinstance(filters, ParsedFilters)
    assert filters.vibe == "funny"
    assert "Romance" in filters.genres

def test_parse_year_query():
    """Test parsing year query"""
    parser = QueryParser()
    filters = parser.parse_query("find movies from the 1990s")
    
    assert isinstance(filters, ParsedFilters)
    assert filters.year_min == 1990
    assert filters.year_max == 1999

def test_parse_keywords():
    """Test parsing keywords from query"""
    parser = QueryParser()
    filters = parser.parse_query("find movies about war and love")
    
    assert isinstance(filters, ParsedFilters)
    assert "war" in filters.keywords
    assert "love" in filters.keywords

def test_parse_voice_query():
    """Test parsing voice query"""
    parser = QueryParser()
    filters = parser.parse_query("find funny movies with tom hanks", QueryType.VOICE)
    
    assert isinstance(filters, ParsedFilters)
    assert "Comedy" in filters.genres
    assert "Tom Hanks" in filters.actors

def test_parse_empty_query():
    """Test parsing empty query"""
    parser = QueryParser()
    filters = parser.parse_query("")
    
    assert isinstance(filters, ParsedFilters)
    assert len(filters.genres) == 0
    assert len(filters.actors) == 0
    assert filters.runtime_min is None
    assert filters.runtime_max is None

def test_parse_unknown_terms():
    """Test parsing query with unknown terms"""
    parser = QueryParser()
    filters = parser.parse_query("find xyz movies with abc actor")
    
    assert isinstance(filters, ParsedFilters)
    # Should not crash and return empty filters
    assert len(filters.genres) == 0
    assert len(filters.actors) == 0

def test_metadata_mapper_initialization():
    """Test MetadataMapper initialization"""
    mapper = MetadataMapper()
    assert mapper is not None
    assert hasattr(mapper, 'normalized_genres')

def test_normalize_filters():
    """Test normalizing parsed filters"""
    mapper = MetadataMapper()
    filters = ParsedFilters(
        genres=["comedy", "drama"],
        actors=["Tom Hanks"],
        runtime_min=90,
        runtime_max=120,
        vibe="funny",
        keywords=["war", "love"]
    )
    
    normalized = mapper.normalize_filters(filters)
    
    assert isinstance(normalized, dict)
    assert "genres" in normalized
    assert "actors" in normalized
    assert "runtime_min" in normalized
    assert "runtime_max" in normalized
    assert "vibe" in normalized
    assert "keywords" in normalized
    
    # Check genre normalization
    assert "Comedy" in normalized["genres"]
    assert "Drama" in normalized["genres"]
    
    # Check actor normalization
    assert "tom hanks" in normalized["actors"]
    
    # Check keyword normalization
    assert "war" in normalized["keywords"]
    assert "love" in normalized["keywords"]

def test_normalize_empty_filters():
    """Test normalizing empty filters"""
    mapper = MetadataMapper()
    filters = ParsedFilters()
    
    normalized = mapper.normalize_filters(filters)
    
    assert isinstance(normalized, dict)
    assert normalized["genres"] == []
    assert normalized["actors"] == []
    assert normalized["runtime_min"] is None
    assert normalized["runtime_max"] is None
    assert normalized["vibe"] is None
    assert normalized["keywords"] == []

def test_genre_normalization():
    """Test genre normalization specifically"""
    mapper = MetadataMapper()
    
    # Test various genre inputs
    test_cases = [
        (["comedy"], ["Comedy"]),
        (["drama"], ["Drama"]),
        (["action"], ["Action"]),
        (["romance"], ["Romance"]),
        (["horror"], ["Horror"]),
        (["sci-fi"], ["Sci-Fi"]),
        (["fantasy"], ["Fantasy"]),
        (["crime"], ["Crime"]),
        (["thriller"], ["Thriller"]),
        (["biography"], ["Biography"]),
        (["history"], ["History"]),
        (["family"], ["Family"])
    ]
    
    for input_genres, expected_genres in test_cases:
        filters = ParsedFilters(genres=input_genres)
        normalized = mapper.normalize_filters(filters)
        assert normalized["genres"] == expected_genres

def test_actor_normalization():
    """Test actor normalization specifically"""
    mapper = MetadataMapper()
    
    filters = ParsedFilters(actors=["Tom Hanks", "Leonardo DiCaprio"])
    normalized = mapper.normalize_filters(filters)
    
    assert "tom hanks" in normalized["actors"]
    assert "leonardo dicaprio" in normalized["actors"]

def test_runtime_parsing_variations():
    """Test various runtime parsing patterns"""
    parser = QueryParser()
    
    test_cases = [
        ("shorter than 120 minutes", None, 120),
        ("longer than 90 minutes", 90, None),
        ("under 100 mins", None, 100),
        ("over 2 hours", 120, None),
        ("less than 1.5 hours", None, 90),
        ("more than 3 hours", 180, None)
    ]
    
    for query, expected_min, expected_max in test_cases:
        filters = parser.parse_query(f"find movies {query}")
        assert filters.runtime_min == expected_min
        assert filters.runtime_max == expected_max

def test_year_parsing_variations():
    """Test various year parsing patterns"""
    parser = QueryParser()
    
    test_cases = [
        ("from 1990", 1990, None),
        ("before 2000", None, 2000),
        ("after 1980", 1980, None),
        ("in the 1990s", 1990, 1999),
        ("since 1995", 1995, None),
        ("until 2010", None, 2010)
    ]
    
    for query, expected_min, expected_max in test_cases:
        filters = parser.parse_query(f"find movies {query}")
        assert filters.year_min == expected_min
        assert filters.year_max == expected_max

"""
Recommendation Strategies for PCD-Lite
Implements A/B testing strategies for content recommendations
"""

import random
import math
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .schema import Movie, ParsedFilters, RecommendationStrategy


class RecommendationEngine:
    """Main recommendation engine with A/B testing strategies"""
    
    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self._build_tfidf_index()
    
    def _build_tfidf_index(self):
        """Build TF-IDF index for similarity-based recommendations"""
        movies = self.data_loader.get_all_movies()
        documents = []
        
        for movie in movies:
            # Combine title, overview, and genres for TF-IDF
            doc = f"{movie.title} {movie.overview} {' '.join(movie.genre)}"
            documents.append(doc)
        
        self.tfidf_vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=1000,
            ngram_range=(1, 2)
        )
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
    
    def get_recommendations(self, filters: ParsedFilters, variant: RecommendationStrategy, limit: int = 10) -> List[Movie]:
        """Get recommendations based on strategy variant"""
        # First filter movies based on parsed filters
        filtered_movies = self._filter_movies(filters)
        
        # Apply recommendation strategy
        if variant == RecommendationStrategy.POPULARITY:
            if not filtered_movies:
                return []
            return self._popularity_strategy(filtered_movies, filters, limit)
        elif variant == RecommendationStrategy.SIMILARITY:
            # For similarity strategy, use all movies if no filtered movies
            movies_to_use = filtered_movies if filtered_movies else self.data_loader.get_all_movies()
            return self._similarity_strategy(movies_to_use, filters, limit)
        else:
            return filtered_movies[:limit] if filtered_movies else []
    
    def _filter_movies(self, filters: ParsedFilters) -> List[Movie]:
        """Filter movies based on parsed filters"""
        all_movies = self.data_loader.get_all_movies()
        filtered = all_movies.copy()
        
        # Filter by genre
        if filters.genres:
            filtered = [m for m in filtered if any(genre.lower() in [g.lower() for g in m.genre] for genre in filters.genres)]
        
        # Filter by actors
        if filters.actors:
            filtered = [m for m in filtered if any(actor.lower() in [c.lower() for c in m.cast] for actor in filters.actors)]
        
        # Filter by runtime
        if filters.runtime_min is not None:
            filtered = [m for m in filtered if m.runtime >= filters.runtime_min]
        if filters.runtime_max is not None:
            filtered = [m for m in filtered if m.runtime <= filters.runtime_max]
        
        # Filter by year
        if filters.year_min is not None:
            filtered = [m for m in filtered if m.release_year >= filters.year_min]
        if filters.year_max is not None:
            filtered = [m for m in filtered if m.release_year <= filters.year_max]
        
        # Filter by keywords in overview
        if filters.keywords:
            keywords = [k.lower() for k in filters.keywords]
            filtered = [m for m in filtered if any(keyword in m.overview.lower() for keyword in keywords)]
        
        return filtered
    
    def _popularity_strategy(self, movies: List[Movie], filters: ParsedFilters, limit: int) -> List[Movie]:
        """Strategy A: Popularity-based with rule-based boosts"""
        scored_movies = []
        
        for movie in movies:
            score = movie.popularity
            
            # Apply boosts based on filters
            if filters.genres:
                genre_boost = sum(1 for genre in filters.genres if genre.lower() in [g.lower() for g in movie.genre])
                score += genre_boost * 0.5
            
            if filters.actors:
                actor_boost = sum(1 for actor in filters.actors if actor.lower() in [c.lower() for c in movie.cast])
                score += actor_boost * 0.3
            
            if filters.vibe:
                vibe_boost = self._calculate_vibe_boost(movie, filters.vibe)
                score += vibe_boost
            
            # Runtime preference boost
            if filters.runtime_min and filters.runtime_max:
                target_runtime = (filters.runtime_min + filters.runtime_max) / 2
                runtime_diff = abs(movie.runtime - target_runtime)
                runtime_boost = max(0, 1 - (runtime_diff / 60))  # Normalize by 60 minutes
                score += runtime_boost * 0.2
            
            scored_movies.append((movie, score))
        
        # Sort by score and return top results
        scored_movies.sort(key=lambda x: x[1], reverse=True)
        return [movie for movie, score in scored_movies[:limit]]
    
    def _similarity_strategy(self, movies: List[Movie], filters: ParsedFilters, limit: int) -> List[Movie]:
        """Strategy B: TF-IDF similarity with genre/cast boosts"""
        if not movies or not self.tfidf_vectorizer:
            return movies[:limit]
        
        # Create query document
        query_parts = []
        if filters.keywords:
            query_parts.extend(filters.keywords)
        if filters.genres:
            query_parts.extend(filters.genres)
        if filters.actors:
            query_parts.extend(filters.actors)
        
        query_doc = ' '.join(query_parts)
        
        # Get TF-IDF vector for query
        query_vector = self.tfidf_vectorizer.transform([query_doc])
        
        # Calculate similarities
        similarities = []
        for movie in movies:
            # Find movie index in TF-IDF matrix
            movie_index = None
            for i, m in enumerate(self.data_loader.get_all_movies()):
                if m.id == movie.id:
                    movie_index = i
                    break
            
            if movie_index is not None:
                movie_vector = self.tfidf_matrix[movie_index]
                similarity = cosine_similarity(query_vector, movie_vector)[0][0]
                
                # Apply boosts
                boost = 0
                if filters.genres:
                    genre_boost = sum(1 for genre in filters.genres if genre.lower() in [g.lower() for g in movie.genre])
                    boost += genre_boost * 0.3
                
                if filters.actors:
                    actor_boost = sum(1 for actor in filters.actors if actor.lower() in [c.lower() for c in movie.cast])
                    boost += actor_boost * 0.2
                
                if filters.vibe:
                    vibe_boost = self._calculate_vibe_boost(movie, filters.vibe)
                    boost += vibe_boost
                
                final_score = similarity + boost
                similarities.append((movie, final_score))
            else:
                similarities.append((movie, 0))
        
        # Sort by similarity score and return top results
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [movie for movie, score in similarities[:limit]]
    
    def _calculate_vibe_boost(self, movie: Movie, vibe: str) -> float:
        """Calculate vibe-based boost for a movie"""
        vibe_keywords = {
            'funny': ['comedy', 'funny', 'hilarious', 'humor', 'laugh'],
            'serious': ['drama', 'serious', 'emotional', 'intense', 'heavy'],
            'romantic': ['romance', 'romantic', 'love', 'romantic comedy'],
            'exciting': ['action', 'thriller', 'adventure', 'exciting', 'thrilling'],
            'scary': ['horror', 'scary', 'frightening', 'terrifying'],
            'thought-provoking': ['drama', 'biography', 'history', 'philosophical'],
            'light': ['comedy', 'family', 'romance', 'fun', 'entertaining'],
            'dark': ['crime', 'thriller', 'drama', 'gritty', 'intense']
        }
        
        if vibe not in vibe_keywords:
            return 0
        
        keywords = vibe_keywords[vibe]
        boost = 0
        
        # Check genre match
        for genre in movie.genre:
            if any(keyword in genre.lower() for keyword in keywords):
                boost += 0.5
        
        # Check overview match
        overview_lower = movie.overview.lower()
        for keyword in keywords:
            if keyword in overview_lower:
                boost += 0.1
        
        return min(boost, 1.0)  # Cap at 1.0
    
    def assign_variant(self, session_id: str) -> RecommendationStrategy:
        """Assign A/B testing variant based on session ID"""
        # Use session ID hash for consistent assignment
        hash_value = hash(session_id) % 2
        return RecommendationStrategy.POPULARITY if hash_value == 0 else RecommendationStrategy.SIMILARITY


class RecommendationMetrics:
    """Calculate recommendation metrics and performance"""
    
    @staticmethod
    def calculate_ctr(impressions: int, clicks: int) -> float:
        """Calculate click-through rate"""
        if impressions == 0:
            return 0.0
        return (clicks / impressions) * 100
    
    @staticmethod
    def calculate_variant_performance(events: List[Dict]) -> Dict[str, Any]:
        """Calculate performance metrics by variant"""
        variant_a_impressions = sum(1 for e in events if e.get('variant') == 'A' and e.get('event_type') == 'impression')
        variant_a_clicks = sum(1 for e in events if e.get('variant') == 'A' and e.get('event_type') == 'click')
        variant_b_impressions = sum(1 for e in events if e.get('variant') == 'B' and e.get('event_type') == 'impression')
        variant_b_clicks = sum(1 for e in events if e.get('variant') == 'B' and e.get('event_type') == 'click')
        
        return {
            'variant_a': {
                'impressions': variant_a_impressions,
                'clicks': variant_a_clicks,
                'ctr': RecommendationMetrics.calculate_ctr(variant_a_impressions, variant_a_clicks)
            },
            'variant_b': {
                'impressions': variant_b_impressions,
                'clicks': variant_b_clicks,
                'ctr': RecommendationMetrics.calculate_ctr(variant_b_impressions, variant_b_clicks)
            }
        }

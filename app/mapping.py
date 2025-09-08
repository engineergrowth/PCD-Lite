"""
Query Parsing and Metadata Mapping for PCD-Lite
Handles natural language query parsing and metadata normalization
"""

import re
from typing import List, Dict, Any, Optional
from .schema import ParsedFilters, QueryType


class QueryParser:
    """Parses natural language queries into structured filters"""
    
    def __init__(self):
        # Genre mapping - common terms to standardized genres
        self.genre_mapping = {
            'comedy': ['comedy', 'funny', 'humor', 'humorous', 'laugh'],
            'drama': ['drama', 'serious', 'emotional', 'touching'],
            'thriller': ['thriller', 'suspense', 'mystery', 'suspenseful'],
            'action': ['action', 'adventure', 'exciting', 'fast-paced'],
            'romance': ['romance', 'romantic', 'love', 'romantic comedy', 'rom-com'],
            'horror': ['horror', 'scary', 'frightening', 'terrifying'],
            'sci-fi': ['sci-fi', 'science fiction', 'futuristic', 'space', 'alien'],
            'fantasy': ['fantasy', 'magical', 'wizard', 'magic'],
            'crime': ['crime', 'criminal', 'gangster', 'mob', 'detective'],
            'biography': ['biography', 'biographical', 'true story', 'real story'],
            'history': ['historical', 'history', 'period piece'],
            'family': ['family', 'kids', 'children', 'family-friendly']
        }
        
        # Actor name variations
        self.actor_mapping = {
            'tom hanks': ['tom hanks', 'thomas hanks'],
            'leonardo dicaprio': ['leonardo dicaprio', 'leo dicaprio'],
            'morgan freeman': ['morgan freeman'],
            'robert de niro': ['robert de niro', 'bobby de niro'],
            'al pacino': ['al pacino', 'alfredo pacino'],
            'brad pitt': ['brad pitt', 'bradley pitt'],
            'matt damon': ['matt damon', 'matthew damon'],
            'julia roberts': ['julia roberts'],
            'meryl streep': ['meryl streep'],
            'denzel washington': ['denzel washington'],
            'keanu reeves': ['keanu reeves'],
            'christian bale': ['christian bale'],
            'heath ledger': ['heath ledger'],
            'robin williams': ['robin williams'],
            'anthony hopkins': ['anthony hopkins'],
            'jodie foster': ['jodie foster'],
            'harrison ford': ['harrison ford'],
            'mark hamill': ['mark hamill'],
            'carrie fisher': ['carrie fisher'],
            'samuel l. jackson': ['samuel l. jackson', 'sam jackson'],
            'john travolta': ['john travolta'],
            'uma thurman': ['uma thurman'],
            'tim robbins': ['tim robbins'],
            'marlon brando': ['marlon brando'],
            'james caan': ['james caan'],
            'edward norton': ['edward norton'],
            'helena bonham carter': ['helena bonham carter'],
            'laurence fishburne': ['laurence fishburne'],
            'carrie-anne moss': ['carrie-anne moss'],
            'ray liotta': ['ray liotta'],
            'joe pesci': ['joe pesci'],
            'scott glenn': ['scott glenn'],
            'viggo mortensen': ['viggo mortensen'],
            'ian mckellen': ['ian mckellen'],
            'elijah wood': ['elijah wood'],
            'orlando bloom': ['orlando bloom'],
            'marion cotillard': ['marion cotillard'],
            'tom hardy': ['tom hardy'],
            'jack nicholson': ['jack nicholson'],
            'louise fletcher': ['louise fletcher'],
            'ben affleck': ['ben affleck'],
            'kevin spacey': ['kevin spacey'],
            'gabriel byrne': ['gabriel byrne'],
            'chazz palminteri': ['chazz palminteri']
        }
        
        # Runtime patterns
        self.runtime_patterns = [
            r'(\d+(?:\.\d+)?)\s*minutes?',
            r'(\d+(?:\.\d+)?)\s*mins?',
            r'(\d+(?:\.\d+)?)\s*hours?',
            r'(\d+(?:\.\d+)?)\s*hrs?',
            r'short(?:er)?\s*(?:than\s*)?(\d+(?:\.\d+)?)\s*minutes?',
            r'long(?:er)?\s*(?:than\s*)?(\d+(?:\.\d+)?)\s*minutes?',
            r'under\s*(\d+(?:\.\d+)?)\s*minutes?',
            r'over\s*(\d+(?:\.\d+)?)\s*hours?',
            r'less\s*than\s*(\d+(?:\.\d+)?)\s*minutes?',
            r'more\s*than\s*(\d+(?:\.\d+)?)\s*hours?',
            r'short(?:er)?\s*(?:than\s*)?(\d+(?:\.\d+)?)',
            r'under\s*(\d+(?:\.\d+)?)'
        ]
        
        # Vibe keywords
        self.vibe_keywords = {
            'funny': ['funny', 'hilarious', 'comedy', 'laugh', 'humor'],
            'serious': ['serious', 'dramatic', 'intense', 'heavy', 'emotional'],
            'romantic': ['romantic', 'love', 'romance', 'sweet', 'cute'],
            'exciting': ['exciting', 'thrilling', 'action-packed', 'adrenaline'],
            'scary': ['scary', 'frightening', 'terrifying', 'horror'],
            'thought-provoking': ['thought-provoking', 'deep', 'philosophical', 'meaningful'],
            'light': ['light', 'easy', 'fun', 'entertaining', 'feel-good'],
            'dark': ['dark', 'gritty', 'disturbing', 'intense']
        }
    
    def parse_query(self, query: str, query_type: QueryType = QueryType.TEXT) -> ParsedFilters:
        """Parse a natural language query into structured filters"""
        query_lower = query.lower().strip()
        
        # Initialize filters
        filters = ParsedFilters()
        
        # Extract genres
        filters.genres = self._extract_genres(query_lower)
        
        # Extract actors
        filters.actors = self._extract_actors(query_lower)
        
        # Extract runtime constraints
        runtime_min, runtime_max = self._extract_runtime(query_lower)
        filters.runtime_min = runtime_min
        filters.runtime_max = runtime_max
        
        # Extract vibe
        filters.vibe = self._extract_vibe(query_lower)
        
        # Extract keywords
        filters.keywords = self._extract_keywords(query_lower)
        
        # Extract year constraints
        year_min, year_max = self._extract_year(query_lower)
        filters.year_min = year_min
        filters.year_max = year_max
        
        return filters
    
    def _extract_genres(self, query: str) -> List[str]:
        """Extract genre information from query"""
        genres = []
        for genre, keywords in self.genre_mapping.items():
            if any(keyword in query for keyword in keywords):
                genres.append(genre.title())
        return genres
    
    def _extract_actors(self, query: str) -> List[str]:
        """Extract actor names from query"""
        actors = []
        for actor, variations in self.actor_mapping.items():
            if any(variation in query for variation in variations):
                actors.append(actor.title())
        return actors
    
    def _extract_runtime(self, query: str) -> tuple[Optional[int], Optional[int]]:
        """Extract runtime constraints from query"""
        runtime_min = None
        runtime_max = None
        
        for pattern in self.runtime_patterns:
            matches = re.findall(pattern, query)
            for match in matches:
                minutes = float(match)
                
                # Convert hours to minutes
                if 'hour' in pattern or 'hr' in pattern:
                    minutes *= 60
                
                # Convert to integer for consistency
                minutes = int(minutes)
                
                # Determine if it's min or max based on context
                if any(word in query for word in ['short', 'under', 'less than']):
                    runtime_max = minutes
                elif any(word in query for word in ['long', 'over', 'more than']):
                    runtime_min = minutes
                else:
                    # Default to max if ambiguous
                    runtime_max = minutes
                
                # Break after first match to avoid overriding
                break
        
        return runtime_min, runtime_max
    
    def _extract_vibe(self, query: str) -> Optional[str]:
        """Extract vibe/mood from query"""
        for vibe, keywords in self.vibe_keywords.items():
            if any(keyword in query for keyword in keywords):
                return vibe
        return None
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract general keywords from query"""
        # Remove common stop words and extract meaningful terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'find', 'show', 'me', 'movies', 'movie', 'film', 'films'}
        
        # Extract words that are not stop words and are longer than 2 characters
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords
    
    def _extract_year(self, query: str) -> tuple[Optional[int], Optional[int]]:
        """Extract year constraints from query"""
        year_min = None
        year_max = None
        
        # Look for year patterns
        year_patterns = [
            r'(\d{4})',
            r'from\s*(\d{4})',
            r'after\s*(\d{4})',
            r'since\s*(\d{4})',
            r'before\s*(\d{4})',
            r'until\s*(\d{4})',
            r'(\d{4})s',  # 1990s
            r'(\d{4})s?',  # 1990s or 1990
        ]
        
        for pattern in year_patterns:
            matches = re.findall(pattern, query)
            for match in matches:
                year = int(match)
                
                # Determine if it's min or max based on context
                if 's' in match or '1990s' in query:  # 1990s
                    year_min = year
                    year_max = year + 9
                elif any(word in query for word in ['from', 'after', 'since']):
                    year_min = year
                elif any(word in query for word in ['before', 'until']):
                    year_max = year
                else:
                    # Default to exact year (set both min and max)
                    year_min = year
                    year_max = year
        
        return year_min, year_max


class MetadataMapper:
    """Maps parsed filters to normalized core schema"""
    
    def __init__(self):
        self.normalized_genres = {
            'Comedy': ['comedy', 'funny', 'humor', 'humorous'],
            'Drama': ['drama', 'serious', 'emotional', 'touching'],
            'Thriller': ['thriller', 'suspense', 'mystery'],
            'Action': ['action', 'adventure', 'exciting'],
            'Romance': ['romance', 'romantic', 'love'],
            'Horror': ['horror', 'scary', 'frightening'],
            'Sci-Fi': ['sci-fi', 'science fiction', 'futuristic'],
            'Fantasy': ['fantasy', 'magical', 'wizard'],
            'Crime': ['crime', 'criminal', 'gangster'],
            'Biography': ['biography', 'biographical'],
            'History': ['historical', 'history'],
            'Family': ['family', 'kids', 'children']
        }
    
    def normalize_filters(self, filters: ParsedFilters) -> Dict[str, Any]:
        """Normalize parsed filters to core schema format"""
        normalized = {
            'genres': self._normalize_genres(filters.genres),
            'actors': [actor.lower() for actor in filters.actors],
            'runtime_min': filters.runtime_min,
            'runtime_max': filters.runtime_max,
            'vibe': filters.vibe,
            'keywords': [kw.lower() for kw in filters.keywords],
            'year_min': filters.year_min,
            'year_max': filters.year_max
        }
        
        return normalized
    
    def _normalize_genres(self, genres: List[str]) -> List[str]:
        """Normalize genre names to standard format"""
        normalized = []
        for genre in genres:
            genre_lower = genre.lower()
            for standard_genre, variations in self.normalized_genres.items():
                if genre_lower in variations or genre_lower == standard_genre.lower():
                    normalized.append(standard_genre)
                    break
        return list(set(normalized))  # Remove duplicates

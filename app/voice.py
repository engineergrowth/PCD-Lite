"""
Voice Processing Module for PCD-Lite
Handles voice-to-text conversion and voice query processing
"""

import re
from typing import Optional, Dict, Any
from .schema import QueryType


class VoiceProcessor:
    """Processes voice queries and converts them to text"""
    
    def __init__(self):
        # Common voice recognition corrections
        self.voice_corrections = {
            # Movie-related terms
            'movie': ['movie', 'film', 'picture', 'flick'],
            'movies': ['movies', 'films', 'pictures', 'flicks'],
            'comedy': ['comedy', 'funny', 'humor', 'humorous'],
            'drama': ['drama', 'serious', 'emotional'],
            'action': ['action', 'adventure', 'thriller'],
            'romance': ['romance', 'romantic', 'love'],
            'horror': ['horror', 'scary', 'frightening'],
            'sci-fi': ['sci-fi', 'science fiction', 'sci fi'],
            'fantasy': ['fantasy', 'magical', 'wizard'],
            'crime': ['crime', 'criminal', 'gangster'],
            'thriller': ['thriller', 'suspense', 'mystery'],
            'biography': ['biography', 'biographical'],
            'history': ['historical', 'history'],
            'family': ['family', 'kids', 'children'],
            
            # Time-related terms
            'minutes': ['minutes', 'mins', 'min'],
            'hours': ['hours', 'hrs', 'hr'],
            'short': ['short', 'shorter', 'brief'],
            'long': ['long', 'longer', 'extended'],
            'under': ['under', 'below', 'less than'],
            'over': ['over', 'above', 'more than'],
            
            # Common voice recognition errors
            'tom hanks': ['tom hanks', 'tom hank', 'thomas hanks'],
            'leonardo dicaprio': ['leonardo dicaprio', 'leo dicaprio', 'leonardo de caprio'],
            'morgan freeman': ['morgan freeman', 'morgan freeman'],
            'robert de niro': ['robert de niro', 'bobby de niro', 'robert deniro'],
            'brad pitt': ['brad pitt', 'bradley pitt', 'brad pit'],
            'matt damon': ['matt damon', 'matthew damon', 'matt damon'],
            'julia roberts': ['julia roberts', 'julie roberts'],
            'meryl streep': ['meryl streep', 'merrill streep'],
            'denzel washington': ['denzel washington', 'denzel washington'],
            'keanu reeves': ['keanu reeves', 'keanu reeves'],
            'christian bale': ['christian bale', 'christian bale'],
            'heath ledger': ['heath ledger', 'heath ledger'],
            'robin williams': ['robin williams', 'robin williams'],
            'anthony hopkins': ['anthony hopkins', 'anthony hopkins'],
            'jodie foster': ['jodie foster', 'jody foster'],
            'harrison ford': ['harrison ford', 'harrison ford'],
            'mark hamill': ['mark hamill', 'mark hammill'],
            'carrie fisher': ['carrie fisher', 'carrie fisher'],
            'samuel l. jackson': ['samuel l. jackson', 'sam jackson', 'samuel jackson'],
            'john travolta': ['john travolta', 'john travolta'],
            'uma thurman': ['uma thurman', 'uma thurman'],
            'tim robbins': ['tim robbins', 'tim robbins'],
            'marlon brando': ['marlon brando', 'marlon brando'],
            'james caan': ['james caan', 'james caan'],
            'edward norton': ['edward norton', 'ed norton'],
            'helena bonham carter': ['helena bonham carter', 'helena bonham carter'],
            'laurence fishburne': ['laurence fishburne', 'laurence fishburne'],
            'carrie-anne moss': ['carrie-anne moss', 'carrie anne moss'],
            'ray liotta': ['ray liotta', 'ray liotta'],
            'joe pesci': ['joe pesci', 'joe pesci'],
            'scott glenn': ['scott glenn', 'scott glenn'],
            'viggo mortensen': ['viggo mortensen', 'viggo mortensen'],
            'ian mckellen': ['ian mckellen', 'ian mckellen'],
            'elijah wood': ['elijah wood', 'elijah wood'],
            'orlando bloom': ['orlando bloom', 'orlando bloom'],
            'marion cotillard': ['marion cotillard', 'marion cotillard'],
            'tom hardy': ['tom hardy', 'tom hardy'],
            'jack nicholson': ['jack nicholson', 'jack nicholson'],
            'louise fletcher': ['louise fletcher', 'louise fletcher'],
            'ben affleck': ['ben affleck', 'ben affleck'],
            'kevin spacey': ['kevin spacey', 'kevin spacey'],
            'gabriel byrne': ['gabriel byrne', 'gabriel byrne'],
            'chazz palminteri': ['chazz palminteri', 'chazz palminteri']
        }
        
        # Common voice recognition patterns
        self.voice_patterns = [
            r'find\s+(.+)',
            r'show\s+me\s+(.+)',
            r'i\s+want\s+(.+)',
            r'look\s+for\s+(.+)',
            r'search\s+for\s+(.+)',
            r'give\s+me\s+(.+)',
            r'recommend\s+(.+)',
            r'suggest\s+(.+)',
            r'what\s+(.+)',
            r'can\s+you\s+find\s+(.+)',
            r'help\s+me\s+find\s+(.+)',
            r'i\s+am\s+looking\s+for\s+(.+)',
            r'i\s+need\s+(.+)',
            r'do\s+you\s+have\s+(.+)',
            r'are\s+there\s+any\s+(.+)'
        ]
    
    def process_voice_query(self, voice_text: str) -> Dict[str, Any]:
        """Process voice query and return structured data"""
        # Clean and normalize voice text
        cleaned_text = self._clean_voice_text(voice_text)
        
        # Extract query content
        query_content = self._extract_query_content(cleaned_text)
        
        # Apply voice corrections
        corrected_query = self._apply_voice_corrections(query_content)
        
        return {
            'original_text': voice_text,
            'cleaned_text': cleaned_text,
            'query_content': query_content,
            'corrected_query': corrected_query,
            'query_type': QueryType.VOICE
        }
    
    def _clean_voice_text(self, text: str) -> str:
        """Clean and normalize voice text"""
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove common voice artifacts
        text = re.sub(r'\b(um|uh|er|ah|like|you know|i mean)\b', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove punctuation that might interfere
        text = re.sub(r'[^\w\s]', ' ', text)
        
        return text.strip()
    
    def _extract_query_content(self, text: str) -> str:
        """Extract the actual query content from voice patterns"""
        for pattern in self.voice_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no pattern matches, return the original text
        return text
    
    def _apply_voice_corrections(self, text: str) -> str:
        """Apply voice recognition corrections"""
        corrected_text = text
        
        for correct_term, variations in self.voice_corrections.items():
            for variation in variations:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(variation) + r'\b'
                corrected_text = re.sub(pattern, correct_term, corrected_text, flags=re.IGNORECASE)
        
        return corrected_text
    
    def simulate_voice_recognition(self, text: str) -> str:
        """Simulate voice recognition with common errors"""
        # Add common voice recognition errors
        errors = {
            'comedy': 'comedy',
            'drama': 'drama',
            'action': 'action',
            'romance': 'romance',
            'horror': 'horror',
            'sci-fi': 'sci fi',
            'fantasy': 'fantasy',
            'crime': 'crime',
            'thriller': 'thriller',
            'biography': 'biography',
            'history': 'history',
            'family': 'family',
            'minutes': 'minutes',
            'hours': 'hours',
            'short': 'short',
            'long': 'long',
            'under': 'under',
            'over': 'over',
            'tom hanks': 'tom hanks',
            'leonardo dicaprio': 'leonardo dicaprio',
            'morgan freeman': 'morgan freeman',
            'robert de niro': 'robert de niro',
            'brad pitt': 'brad pitt',
            'matt damon': 'matt damon',
            'julia roberts': 'julia roberts',
            'meryl streep': 'meryl streep',
            'denzel washington': 'denzel washington',
            'keanu reeves': 'keanu reeves',
            'christian bale': 'christian bale',
            'heath ledger': 'heath ledger',
            'robin williams': 'robin williams',
            'anthony hopkins': 'anthony hopkins',
            'jodie foster': 'jodie foster',
            'harrison ford': 'harrison ford',
            'mark hamill': 'mark hamill',
            'carrie fisher': 'carrie fisher',
            'samuel l. jackson': 'samuel l. jackson',
            'john travolta': 'john travolta',
            'uma thurman': 'uma thurman',
            'tim robbins': 'tim robbins',
            'marlon brando': 'marlon brando',
            'james caan': 'james caan',
            'edward norton': 'edward norton',
            'helena bonham carter': 'helena bonham carter',
            'laurence fishburne': 'laurence fishburne',
            'carrie-anne moss': 'carrie anne moss',
            'ray liotta': 'ray liotta',
            'joe pesci': 'joe pesci',
            'scott glenn': 'scott glenn',
            'viggo mortensen': 'viggo mortensen',
            'ian mckellen': 'ian mckellen',
            'elijah wood': 'elijah wood',
            'orlando bloom': 'orlando bloom',
            'marion cotillard': 'marion cotillard',
            'tom hardy': 'tom hardy',
            'jack nicholson': 'jack nicholson',
            'louise fletcher': 'louise fletcher',
            'ben affleck': 'ben affleck',
            'kevin spacey': 'kevin spacey',
            'gabriel byrne': 'gabriel byrne',
            'chazz palminteri': 'chazz palminteri'
        }
        
        # Apply corrections
        for correct_term, variation in errors.items():
            pattern = r'\b' + re.escape(variation) + r'\b'
            text = re.sub(pattern, correct_term, text, flags=re.IGNORECASE)
        
        return text
    
    def get_voice_suggestions(self, partial_query: str) -> list[str]:
        """Get voice query suggestions based on partial input"""
        suggestions = []
        
        # Common voice query starters
        starters = [
            "find comedy movies",
            "show me action films",
            "recommend romantic movies",
            "look for horror films",
            "search for sci-fi movies",
            "give me drama movies",
            "suggest thriller movies",
            "what comedy movies are there",
            "can you find action movies",
            "help me find romantic movies",
            "i am looking for horror movies",
            "i need comedy movies",
            "do you have action movies",
            "are there any romantic movies"
        ]
        
        # Filter suggestions based on partial query
        if partial_query:
            partial_lower = partial_query.lower()
            suggestions = [s for s in starters if partial_lower in s.lower()]
        else:
            suggestions = starters[:5]  # Return first 5 if no partial query
        
        return suggestions[:10]  # Limit to 10 suggestions

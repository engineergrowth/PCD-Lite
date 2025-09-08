"""
Data Loader for PCD-Lite
Loads and manages the movie catalog dataset
"""

import pandas as pd
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from .schema import Movie


class DataLoader:
    """Handles loading and managing movie catalog data"""
    
    def __init__(self, data_path: str = "data/catalog.csv"):
        self.data_path = Path(data_path)
        self.catalog: List[Movie] = []
        self.df: pd.DataFrame = None
        self.load_catalog()
    
    def load_catalog(self) -> None:
        """Load movie catalog from CSV file"""
        try:
            if not self.data_path.exists():
                self._create_sample_catalog()
            
            self.df = pd.read_csv(self.data_path)
            self.catalog = self._df_to_movies(self.df)
            print(f"Loaded {len(self.catalog)} movies from catalog")
            
        except Exception as e:
            print(f"Error loading catalog: {e}")
            self._create_sample_catalog()
            self.df = pd.read_csv(self.data_path)
            self.catalog = self._df_to_movies(self.df)
    
    def _create_sample_catalog(self) -> None:
        """Create a sample movie catalog if none exists"""
        sample_movies = [
            {
                "id": 1,
                "title": "Forrest Gump",
                "genre": "Drama,Comedy,Romance",
                "cast": "Tom Hanks,Robin Wright,Gary Sinise",
                "overview": "The story of a simple man who unwittingly becomes involved in several historical events.",
                "runtime": 142,
                "popularity": 8.5,
                "release_year": 1994,
                "director": "Robert Zemeckis",
                "rating": 8.8
            },
            {
                "id": 2,
                "title": "The Shawshank Redemption",
                "genre": "Drama",
                "cast": "Tim Robbins,Morgan Freeman,Bob Gunton",
                "overview": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
                "runtime": 142,
                "popularity": 9.2,
                "release_year": 1994,
                "director": "Frank Darabont",
                "rating": 9.3
            },
            {
                "id": 3,
                "title": "The Godfather",
                "genre": "Drama,Crime",
                "cast": "Marlon Brando,Al Pacino,James Caan",
                "overview": "The aging patriarch of an organized crime dynasty transfers control to his reluctant son.",
                "runtime": 175,
                "popularity": 9.0,
                "release_year": 1972,
                "director": "Francis Ford Coppola",
                "rating": 9.2
            },
            {
                "id": 4,
                "title": "Pulp Fiction",
                "genre": "Crime,Drama",
                "cast": "John Travolta,Samuel L. Jackson,Uma Thurman",
                "overview": "The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.",
                "runtime": 154,
                "popularity": 8.9,
                "release_year": 1994,
                "director": "Quentin Tarantino",
                "rating": 8.9
            },
            {
                "id": 5,
                "title": "The Dark Knight",
                "genre": "Action,Crime,Drama",
                "cast": "Christian Bale,Heath Ledger,Aaron Eckhart",
                "overview": "When the menace known as the Joker wreaks havoc on Gotham, Batman must accept one of the greatest psychological tests.",
                "runtime": 152,
                "popularity": 9.0,
                "release_year": 2008,
                "director": "Christopher Nolan",
                "rating": 9.0
            },
            {
                "id": 6,
                "title": "Schindler's List",
                "genre": "Drama,History",
                "cast": "Liam Neeson,Ralph Fiennes,Ben Kingsley",
                "overview": "In German-occupied Poland during World War II, industrialist Oskar Schindler gradually becomes concerned for his Jewish workforce.",
                "runtime": 195,
                "popularity": 8.9,
                "release_year": 1993,
                "director": "Steven Spielberg",
                "rating": 8.9
            },
            {
                "id": 7,
                "title": "The Lord of the Rings: The Return of the King",
                "genre": "Adventure,Drama,Fantasy",
                "cast": "Elijah Wood,Viggo Mortensen,Ian McKellen",
                "overview": "Gandalf and Aragorn lead the World of Men against Sauron's army to draw his gaze from Frodo and Sam.",
                "runtime": 201,
                "popularity": 8.9,
                "release_year": 2003,
                "director": "Peter Jackson",
                "rating": 8.9
            },
            {
                "id": 8,
                "title": "Fight Club",
                "genre": "Drama",
                "cast": "Brad Pitt,Edward Norton,Helena Bonham Carter",
                "overview": "An insomniac office worker and a devil-may-care soap maker form an underground fight club.",
                "runtime": 139,
                "popularity": 8.8,
                "release_year": 1999,
                "director": "David Fincher",
                "rating": 8.8
            },
            {
                "id": 9,
                "title": "The Matrix",
                "genre": "Action,Sci-Fi",
                "cast": "Keanu Reeves,Laurence Fishburne,Carrie-Anne Moss",
                "overview": "A computer hacker learns about the true nature of reality and his role in the war against its controllers.",
                "runtime": 136,
                "popularity": 8.7,
                "release_year": 1999,
                "director": "Lana Wachowski",
                "rating": 8.7
            },
            {
                "id": 10,
                "title": "Goodfellas",
                "genre": "Biography,Crime,Drama",
                "cast": "Robert De Niro,Ray Liotta,Joe Pesci",
                "overview": "The story of Henry Hill and his life in the mob, covering his relationship with his wife Karen Hill.",
                "runtime": 146,
                "popularity": 8.7,
                "release_year": 1990,
                "director": "Martin Scorsese",
                "rating": 8.7
            },
            {
                "id": 11,
                "title": "The Silence of the Lambs",
                "genre": "Crime,Drama,Thriller",
                "cast": "Jodie Foster,Anthony Hopkins,Scott Glenn",
                "overview": "A young F.B.I. cadet must receive the help of an incarcerated and manipulative cannibal killer.",
                "runtime": 118,
                "popularity": 8.6,
                "release_year": 1991,
                "director": "Jonathan Demme",
                "rating": 8.6
            },
            {
                "id": 12,
                "title": "Star Wars: Episode V - The Empire Strikes Back",
                "genre": "Action,Adventure,Fantasy",
                "cast": "Mark Hamill,Harrison Ford,Carrie Fisher",
                "overview": "After the Rebels are brutally overpowered by the Empire on the ice planet Hoth, Luke Skywalker begins Jedi training.",
                "runtime": 124,
                "popularity": 8.7,
                "release_year": 1980,
                "director": "Irvin Kershner",
                "rating": 8.7
            },
            {
                "id": 13,
                "title": "The Lord of the Rings: The Fellowship of the Ring",
                "genre": "Adventure,Drama,Fantasy",
                "cast": "Elijah Wood,Ian McKellen,Orlando Bloom",
                "overview": "A meek Hobbit from the Shire and eight companions set out on a journey to destroy the powerful One Ring.",
                "runtime": 178,
                "popularity": 8.8,
                "release_year": 2001,
                "director": "Peter Jackson",
                "rating": 8.8
            },
            {
                "id": 14,
                "title": "Inception",
                "genre": "Action,Sci-Fi,Thriller",
                "cast": "Leonardo DiCaprio,Marion Cotillard,Tom Hardy",
                "overview": "A thief who steals corporate secrets through dream-sharing technology is given a chance at redemption.",
                "runtime": 148,
                "popularity": 8.8,
                "release_year": 2010,
                "director": "Christopher Nolan",
                "rating": 8.8
            },
            {
                "id": 15,
                "title": "The Lord of the Rings: The Two Towers",
                "genre": "Adventure,Drama,Fantasy",
                "cast": "Elijah Wood,Ian McKellen,Viggo Mortensen",
                "overview": "While Frodo and Sam edge closer to Mordor with the help of the shifty Gollum, the divided fellowship makes a stand.",
                "runtime": 179,
                "popularity": 8.7,
                "release_year": 2002,
                "director": "Peter Jackson",
                "rating": 8.7
            },
            {
                "id": 16,
                "title": "One Flew Over the Cuckoo's Nest",
                "genre": "Drama",
                "cast": "Jack Nicholson,Louise Fletcher,Michael Berryman",
                "overview": "A criminal pleads insanity and is admitted to a mental institution, where he rebels against the oppressive nurse.",
                "runtime": 133,
                "popularity": 8.7,
                "release_year": 1975,
                "director": "Milos Forman",
                "rating": 8.7
            },
            {
                "id": 17,
                "title": "Good Will Hunting",
                "genre": "Drama,Romance",
                "cast": "Robin Williams,Matt Damon,Ben Affleck",
                "overview": "Will Hunting, a janitor at M.I.T., has a gift for mathematics, but needs help from a psychologist.",
                "runtime": 126,
                "popularity": 8.3,
                "release_year": 1997,
                "director": "Gus Van Sant",
                "rating": 8.3
            },
            {
                "id": 18,
                "title": "The Matrix Reloaded",
                "genre": "Action,Sci-Fi",
                "cast": "Keanu Reeves,Laurence Fishburne,Carrie-Anne Moss",
                "overview": "Neo and the rebel leaders estimate they have 72 hours until 250,000 machines discover Zion.",
                "runtime": 138,
                "popularity": 7.2,
                "release_year": 2003,
                "director": "Lana Wachowski",
                "rating": 7.2
            },
            {
                "id": 19,
                "title": "The Usual Suspects",
                "genre": "Crime,Mystery,Thriller",
                "cast": "Kevin Spacey,Gabriel Byrne,Chazz Palminteri",
                "overview": "A sole survivor tells of the twisty events leading up to a horrific gun battle on a boat.",
                "runtime": 106,
                "popularity": 8.5,
                "release_year": 1995,
                "director": "Bryan Singer",
                "rating": 8.5
            },
            {
                "id": 20,
                "title": "Se7en",
                "genre": "Crime,Drama,Mystery",
                "cast": "Morgan Freeman,Brad Pitt,Kevin Spacey",
                "overview": "Two detectives, a rookie and a veteran, hunt a serial killer who uses the seven deadly sins as his motives.",
                "runtime": 127,
                "popularity": 8.6,
                "release_year": 1995,
                "director": "David Fincher",
                "rating": 8.6
            }
        ]
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(sample_movies)
        df.to_csv(self.data_path, index=False)
        print(f"Created sample catalog with {len(sample_movies)} movies at {self.data_path}")
    
    def _df_to_movies(self, df: pd.DataFrame) -> List[Movie]:
        """Convert DataFrame to list of Movie objects"""
        movies = []
        for _, row in df.iterrows():
            movie = Movie(
                id=int(row['id']),
                title=row['title'],
                genre=row['genre'].split(',') if isinstance(row['genre'], str) else [],
                cast=row['cast'].split(',') if isinstance(row['cast'], str) else [],
                overview=row['overview'],
                runtime=int(row['runtime']),
                popularity=float(row['popularity']),
                release_year=int(row['release_year']),
                director=row['director'],
                rating=float(row['rating'])
            )
            movies.append(movie)
        return movies
    
    def get_all_movies(self) -> List[Movie]:
        """Get all movies in the catalog"""
        return self.catalog
    
    def get_movie_by_id(self, movie_id: int) -> Optional[Movie]:
        """Get a specific movie by ID"""
        for movie in self.catalog:
            if movie.id == movie_id:
                return movie
        return None
    
    def search_movies(self, filters: Dict[str, Any]) -> List[Movie]:
        """Search movies based on filters"""
        results = self.catalog.copy()
        
        # Filter by genre
        if filters.get('genres'):
            results = [m for m in results if any(genre.lower() in [g.lower() for g in m.genre] for genre in filters['genres'])]
        
        # Filter by actors
        if filters.get('actors'):
            results = [m for m in results if any(actor.lower() in [c.lower() for c in m.cast] for actor in filters['actors'])]
        
        # Filter by runtime
        if filters.get('runtime_min'):
            results = [m for m in results if m.runtime >= filters['runtime_min']]
        if filters.get('runtime_max'):
            results = [m for m in results if m.runtime <= filters['runtime_max']]
        
        # Filter by year
        if filters.get('year_min'):
            results = [m for m in results if m.release_year >= filters['year_min']]
        if filters.get('year_max'):
            results = [m for m in results if m.release_year <= filters['year_max']]
        
        # Filter by keywords in overview
        if filters.get('keywords'):
            keywords = [k.lower() for k in filters['keywords']]
            results = [m for m in results if any(keyword in m.overview.lower() for keyword in keywords)]
        
        return results

"""
Event Logging and Storage for PCD-Lite
Handles event logging, storage, and analytics data management
"""

import sqlite3
import csv
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import uuid
from .schema import EventLog, AnalyticsMetrics, ParsedFilters, RecommendationStrategy


class EventStore:
    """Handles event logging and storage"""
    
    def __init__(self, db_path: str = "data/events.db", csv_path: str = "data/events.csv"):
        self.db_path = Path(db_path)
        self.csv_path = Path(csv_path)
        self._init_database()
        self._init_csv()
    
    def _init_database(self):
        """Initialize SQLite database for event storage"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    variant TEXT NOT NULL,
                    movie_id INTEGER,
                    position INTEGER,
                    filters TEXT,
                    timestamp TEXT NOT NULL,
                    request_id TEXT NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_session_id ON events(session_id)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_variant ON events(variant)
            ''')
            
            conn.commit()
    
    def _init_csv(self):
        """Initialize CSV file for event logging"""
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.csv_path.exists():
            with open(self.csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'event_id', 'session_id', 'event_type', 'variant', 'movie_id',
                    'position', 'filters', 'timestamp', 'request_id'
                ])
    
    def log_event(self, event: EventLog) -> bool:
        """Log an event to both database and CSV"""
        try:
            # Log to database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO events (event_id, session_id, event_type, variant, movie_id, 
                                     position, filters, timestamp, request_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.event_id,
                    event.session_id,
                    event.event_type,
                    event.variant.value,
                    event.movie_id,
                    event.position,
                    json.dumps(event.filters.dict()) if event.filters else None,
                    event.timestamp.isoformat(),
                    event.request_id
                ))
                conn.commit()
            
            # Log to CSV
            with open(self.csv_path, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    event.event_id,
                    event.session_id,
                    event.event_type,
                    event.variant.value,
                    event.movie_id,
                    event.position,
                    json.dumps(event.filters.dict()) if event.filters else None,
                    event.timestamp.isoformat(),
                    event.request_id
                ])
            
            return True
            
        except Exception as e:
            print(f"Error logging event: {e}")
            return False
    
    def log_impression(self, session_id: str, variant: RecommendationStrategy, 
                      movie_id: int, position: int, filters: ParsedFilters, 
                      request_id: str) -> bool:
        """Log an impression event"""
        event = EventLog(
            event_id=str(uuid.uuid4()),
            session_id=session_id,
            event_type="impression",
            variant=variant,
            movie_id=movie_id,
            position=position,
            filters=filters,
            timestamp=datetime.now(),
            request_id=request_id
        )
        return self.log_event(event)
    
    def log_click(self, session_id: str, variant: RecommendationStrategy, 
                  movie_id: int, position: int, request_id: str) -> bool:
        """Log a click event"""
        event = EventLog(
            event_id=str(uuid.uuid4()),
            session_id=session_id,
            event_type="click",
            variant=variant,
            movie_id=movie_id,
            position=position,
            filters=None,
            timestamp=datetime.now(),
            request_id=request_id
        )
        return self.log_event(event)
    
    def get_events(self, session_id: Optional[str] = None, 
                   event_type: Optional[str] = None,
                   variant: Optional[RecommendationStrategy] = None,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get events with optional filtering"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM events WHERE 1=1"
                params = []
                
                if session_id:
                    query += " AND session_id = ?"
                    params.append(session_id)
                
                if event_type:
                    query += " AND event_type = ?"
                    params.append(event_type)
                
                if variant:
                    query += " AND variant = ?"
                    params.append(variant.value)
                
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date.isoformat())
                
                query += " ORDER BY timestamp DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                events = []
                for row in rows:
                    event = {
                        'event_id': row[0],
                        'session_id': row[1],
                        'event_type': row[2],
                        'variant': row[3],
                        'movie_id': row[4],
                        'position': row[5],
                        'filters': json.loads(row[6]) if row[6] else None,
                        'timestamp': row[7],
                        'request_id': row[8]
                    }
                    events.append(event)
                
                return events
                
        except Exception as e:
            print(f"Error getting events: {e}")
            return []
    
    def get_analytics_metrics(self, days: int = 7) -> AnalyticsMetrics:
        """Calculate analytics metrics for the specified period"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        events = self.get_events(start_date=start_date, end_date=end_date)
        
        if not events:
            return AnalyticsMetrics(
                total_sessions=0,
                total_impressions=0,
                total_clicks=0,
                ctr=0.0,
                variant_a_impressions=0,
                variant_a_clicks=0,
                variant_a_ctr=0.0,
                variant_b_impressions=0,
                variant_b_clicks=0,
                variant_b_ctr=0.0,
                avg_processing_time_ms=0.0,
                most_popular_genres=[],
                most_clicked_movies=[]
            )
        
        # Calculate basic metrics
        total_sessions = len(set(e['session_id'] for e in events))
        total_impressions = len([e for e in events if e['event_type'] == 'impression'])
        total_clicks = len([e for e in events if e['event_type'] == 'click'])
        ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0.0
        
        # Calculate variant-specific metrics
        variant_a_impressions = len([e for e in events if e['event_type'] == 'impression' and e['variant'] == 'A'])
        variant_a_clicks = len([e for e in events if e['event_type'] == 'click' and e['variant'] == 'A'])
        variant_a_ctr = (variant_a_clicks / variant_a_impressions * 100) if variant_a_impressions > 0 else 0.0
        
        variant_b_impressions = len([e for e in events if e['event_type'] == 'impression' and e['variant'] == 'B'])
        variant_b_clicks = len([e for e in events if e['event_type'] == 'click' and e['variant'] == 'B'])
        variant_b_ctr = (variant_b_clicks / variant_b_impressions * 100) if variant_b_impressions > 0 else 0.0
        
        # Calculate processing time (placeholder - would need to be tracked separately)
        avg_processing_time_ms = 150.0  # Placeholder value
        
        # Calculate most popular genres
        genre_counts = {}
        for event in events:
            if event['filters'] and 'genres' in event['filters']:
                for genre in event['filters']['genres']:
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        most_popular_genres = [
            {'genre': genre, 'count': count}
            for genre, count in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
        ][:5]
        
        # Calculate most clicked movies
        movie_click_counts = {}
        for event in events:
            if event['event_type'] == 'click' and event['movie_id']:
                movie_id = event['movie_id']
                movie_click_counts[movie_id] = movie_click_counts.get(movie_id, 0) + 1
        
        most_clicked_movies = [
            {'movie_id': movie_id, 'clicks': count}
            for movie_id, count in sorted(movie_click_counts.items(), key=lambda x: x[1], reverse=True)
        ][:5]
        
        return AnalyticsMetrics(
            total_sessions=total_sessions,
            total_impressions=total_impressions,
            total_clicks=total_clicks,
            ctr=ctr,
            variant_a_impressions=variant_a_impressions,
            variant_a_clicks=variant_a_clicks,
            variant_a_ctr=variant_a_ctr,
            variant_b_impressions=variant_b_impressions,
            variant_b_clicks=variant_b_clicks,
            variant_b_ctr=variant_b_ctr,
            avg_processing_time_ms=avg_processing_time_ms,
            most_popular_genres=most_popular_genres,
            most_clicked_movies=most_clicked_movies
        )
    
    def get_session_events(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all events for a specific session"""
        return self.get_events(session_id=session_id)
    
    def get_variant_performance(self, days: int = 7) -> Dict[str, Any]:
        """Get performance metrics by variant"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        events = self.get_events(start_date=start_date, end_date=end_date)
        
        variant_a_events = [e for e in events if e['variant'] == 'A']
        variant_b_events = [e for e in events if e['variant'] == 'B']
        
        return {
            'variant_a': {
                'impressions': len([e for e in variant_a_events if e['event_type'] == 'impression']),
                'clicks': len([e for e in variant_a_events if e['event_type'] == 'click']),
                'sessions': len(set(e['session_id'] for e in variant_a_events))
            },
            'variant_b': {
                'impressions': len([e for e in variant_b_events if e['event_type'] == 'impression']),
                'clicks': len([e for e in variant_b_events if e['event_type'] == 'click']),
                'sessions': len(set(e['session_id'] for e in variant_b_events))
            }
        }
    
    def clear_old_events(self, days: int = 30) -> int:
        """Clear events older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM events WHERE timestamp < ?', (cutoff_date.isoformat(),))
                deleted_count = cursor.rowcount
                conn.commit()
                return deleted_count
        except Exception as e:
            print(f"Error clearing old events: {e}")
            return 0

# PCD-Lite: Personalized Content Discovery Prototype

A comprehensive prototype showcasing TiVo's Personalized Content Discovery workflow, built for a Customer Solutions Engineer interview at Xperi. This demo-ready application demonstrates natural language search, metadata mapping, A/B testing, and analytics in a production-like environment.

## 🎯 Project Overview

PCD-Lite simulates the complete TiVo PCD workflow:
- **Natural Language/Voice Search** → **Metadata Mapping** → **JSON Recommendation API** → **A/B Testing** → **Analytics Dashboard**

The system is designed to be demo-able in under 10 minutes while showcasing enterprise-level features and architecture.

## 🏗️ Architecture

![PCD-Lite Architecture](diagram.mmd)

### Core Components

1. **FastAPI Backend** - RESTful API with comprehensive endpoints
2. **Query Processing** - Natural language parsing and voice processing
3. **A/B Testing Engine** - Two recommendation strategies with session-based assignment
4. **Event Logging** - Comprehensive tracking and analytics
5. **Streamlit Dashboard** - Real-time analytics and visualization
6. **Movie Catalog** - Curated dataset with 30+ movies

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip or conda

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd pcd-lite

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

#### 1. Start the FastAPI Server

```bash
# From the project root
python -m app.main
```

The API will be available at `http://localhost:8000`

#### 2. Start the Analytics Dashboard

```bash
# In a new terminal
streamlit run dashboard/app.py
```

The dashboard will be available at `http://localhost:8501`

#### 3. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Search for comedy movies
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "find comedy movies", "query_type": "text"}'
```

## 📊 Demo Script (10 Minutes)

### Phase 1: Basic Search (2 minutes)

1. **Text Search**
   ```bash
   curl -X POST "http://localhost:8000/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "find comedy movies with Tom Hanks"}'
   ```

2. **Voice Search**
   ```bash
   curl -X POST "http://localhost:8000/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "show me action movies shorter than 120 minutes", "query_type": "voice"}'
   ```

3. **Complex Query**
   ```bash
   curl -X POST "http://localhost:8000/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "recommend romantic drama movies from the 1990s with good ratings"}'
   ```

### Phase 2: A/B Testing Demo (3 minutes)

1. **Check Debug Info**
   ```bash
   curl http://localhost:8000/debug/last-query
   ```

2. **Track Clicks**
   ```bash
   curl -X POST "http://localhost:8000/click" \
     -H "Content-Type: application/json" \
     -d '{"request_id": "test-123", "session_id": "session-456", "movie_id": 1, "position": 1, "variant": "A"}'
   ```

3. **View Analytics**
   - Open Streamlit dashboard at `http://localhost:8501`
   - Show A/B testing results
   - Demonstrate CTR visualization

### Phase 3: Advanced Features (3 minutes)

1. **Fault Injection**
   ```bash
   curl -X POST "http://localhost:8000/search?fail=1" \
     -H "Content-Type: application/json" \
     -d '{"query": "test error handling"}'
   ```

2. **Session Analysis**
   ```bash
   curl http://localhost:8000/session/session-456/events
   ```

3. **Voice Suggestions**
   ```bash
   curl "http://localhost:8000/voice/suggestions?partial_query=comedy"
   ```

### Phase 4: Analytics Deep Dive (2 minutes)

1. **Variant Performance**
   ```bash
   curl "http://localhost:8000/analytics/variants?days=7"
   ```

2. **Dashboard Features**
   - Show real-time metrics
   - Demonstrate session tracking
   - Explain A/B testing results

## 🔧 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/search` | POST | Search for content |
| `/click` | POST | Track user clicks |
| `/debug/last-query` | GET | Debug information |

### Analytics Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analytics` | GET | Overall analytics metrics |
| `/analytics/variants` | GET | A/B testing performance |
| `/session/{id}/events` | GET | Session-specific events |

### Utility Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/catalog` | GET | Movie catalog |
| `/voice/suggestions` | GET | Voice query suggestions |

## 🧪 A/B Testing Strategies

### Strategy A: Popularity-Based
- Uses movie popularity scores
- Applies rule-based boosts for genre/actor matches
- Runtime preference adjustments
- Vibe-based scoring

### Strategy B: TF-IDF Similarity
- Content-based filtering using movie overviews
- Cosine similarity calculations
- Genre and cast matching
- Advanced text analysis

## 📈 Analytics Features

### Real-time Metrics
- Click-through rate (CTR)
- Impressions and clicks by variant
- Session tracking
- Processing time analysis

### Visualizations
- CTR comparison charts
- Genre popularity distribution
- Session event timelines
- Performance trends

## 🎬 Sample Queries

### Text Queries
- "find comedy movies"
- "show me action movies with Tom Cruise"
- "recommend romantic movies from the 1990s"
- "find short movies under 100 minutes"
- "what are the best drama movies?"

### Voice Queries
- "find funny movies with robin williams"
- "show me sci-fi movies"
- "recommend family movies"
- "find thriller movies shorter than 2 hours"

## 🔍 Interview Talking Points

### How PCD-Lite Mirrors TiVo's PCD Workflow

1. **Natural Language Processing**
   - Query parsing and intent recognition
   - Voice-to-text conversion with error correction
   - Metadata normalization and mapping

2. **Recommendation Engine**
   - Multiple strategies for content discovery
   - A/B testing framework for optimization
   - Real-time performance tracking

3. **Analytics and Monitoring**
   - Comprehensive event logging
   - Real-time dashboard for insights
   - Session-based user tracking

### Production Scalability Considerations

1. **AWS Load Balancing**
   - Application Load Balancer for traffic distribution
   - Health checks and auto-scaling
   - SSL termination and security

2. **Auto Scaling**
   - Dynamic instance management
   - Cost optimization
   - Performance-based scaling

3. **Log Aggregation**
   - Integration with Kibana for log analysis
   - Splunk for enterprise logging
   - Real-time monitoring and alerting

### Technical Highlights

1. **Clean Architecture**
   - Modular design with separation of concerns
   - Comprehensive error handling
   - Production-ready logging and monitoring

2. **Performance Optimization**
   - Efficient data structures
   - Caching strategies
   - Async processing where applicable

3. **Debugging and Monitoring**
   - Comprehensive debug endpoints
   - Request tracing with X-Request-Id headers
   - Performance metrics collection

## 🛠️ Development Setup

### Project Structure

```
pcd-lite/
├── app/                    # FastAPI application
│   ├── main.py            # Main application
│   ├── schema.py          # Data models
│   ├── mapping.py         # Query parsing
│   ├── recs.py            # Recommendation engine
│   ├── voice.py           # Voice processing
│   ├── store.py           # Event logging
│   └── data_loader.py     # Data management
├── dashboard/             # Streamlit dashboard
│   └── app.py            # Dashboard application
├── data/                 # Data files
│   └── catalog.csv       # Movie catalog
├── postman_collection.json # API testing
├── diagram.mmd           # Architecture diagram
└── README.md            # This file
```

### Dependencies

```txt
fastapi==0.104.1
uvicorn==0.24.0
streamlit==1.28.1
pandas==2.1.3
scikit-learn==1.3.2
plotly==5.17.0
requests==2.31.0
pydantic==2.5.0
```

## 🧪 Testing

### Unit Tests

```bash
# Run unit tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=app tests/
```

### API Testing

Use the provided Postman collection:
1. Import `postman_collection.json`
2. Set base URL to `http://localhost:8000`
3. Run the collection

## 🚀 Deployment Considerations

### Docker Deployment

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# Database Configuration
DATABASE_URL=sqlite:///data/events.db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

## 📊 Performance Metrics

### Expected Performance
- **Search Response Time**: < 200ms
- **Click Tracking**: < 50ms
- **Analytics Queries**: < 500ms
- **Concurrent Users**: 100+ (single instance)

### Monitoring
- Request/response times
- Error rates
- A/B testing performance
- User engagement metrics

## 🔒 Security Considerations

1. **Input Validation**
   - Comprehensive query sanitization
   - SQL injection prevention
   - XSS protection

2. **Rate Limiting**
   - API rate limiting
   - Session-based throttling
   - DDoS protection

3. **Data Privacy**
   - Session anonymization
   - Data retention policies
   - GDPR compliance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is created for interview demonstration purposes.



## 📞 Contact

For questions about this prototype or the implementation, please reach out during the interview process.

---

**Built with ❤️ for the TiVo Personalized Content Discovery team at Xperi**

# TV Series Tracker

A full-stack application for discovering, tracking, and exploring TV series with AI-powered insights. Built as a technical reference implementation demonstrating Clean Architecture, SOLID principles, and modern web development practices.

## 🎯 Features

### Core Functionality
- **🔍 TV Series Search**: Async search with debouncing using the TVMaze API
- **📺 Series Details**: Poster, summary, genres, rating, and episodes grouped by season
- **✅ Episode Tracking**: Mark/unmark episodes as watched with persistent state
- **💬 Comments**: Leave comments on series or specific episodes
- **🤖 AI Insights**: Generate AI-powered analysis for shows and episodes

### Technical Highlights
- Clean Architecture with dependency injection
- Async/await throughout the stack
- Type safety (Python type hints + TypeScript)
- Graceful error handling with fallbacks
- Docker-ready with single-command deployment

## 🏗️ Architecture

This project follows **Clean Architecture** principles with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│  React + TypeScript + Tailwind CSS                          │
│  ┌─────────┐ ┌────────────┐ ┌───────┐ ┌───────┐            │
│  │  Pages  │ │ Components │ │ Hooks │ │ Types │            │
│  └─────────┘ └────────────┘ └───────┘ └───────┘            │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/REST
┌─────────────────────────▼───────────────────────────────────┐
│                        Backend                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ API Layer (FastAPI)                                  │    │
│  │ Routes, Schemas, Dependencies                        │    │
│  └──────────────────────┬──────────────────────────────┘    │
│  ┌──────────────────────▼──────────────────────────────┐    │
│  │ Application Layer                                    │    │
│  │ Services (Use Cases)                                 │    │
│  └──────────────────────┬──────────────────────────────┘    │
│  ┌──────────────────────▼──────────────────────────────┐    │
│  │ Domain Layer                                         │    │
│  │ Entities, Interfaces (Ports)                         │    │
│  └──────────────────────┬──────────────────────────────┘    │
│  ┌──────────────────────▼──────────────────────────────┐    │
│  │ Infrastructure Layer (Adapters)                      │    │
│  │ Repositories, TVMaze Client, AI Generator            │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    ┌──────────┐   ┌───────────┐   ┌─────────────┐
    │ Database │   │  TVMaze   │   │ HuggingFace │
    │ PostgreSQL│   │    API    │   │     API     │
    └──────────┘   └───────────┘   └─────────────┘
```

### Backend Structure (Python 3.10 + FastAPI)

```
backend/
├── app/
│   ├── domain/              # Core business logic (no dependencies)
│   │   ├── entities.py      # Show, Episode, Comment, WatchedEpisode, AIInsight
│   │   └── interfaces.py    # Abstract interfaces (ports)
│   ├── application/         # Use cases
│   │   └── services.py      # ShowService, CommentService, AIInsightService
│   ├── infrastructure/      # External implementations (adapters)
│   │   ├── database.py      # Async SQLAlchemy configuration
│   │   ├── models.py        # ORM models
│   │   ├── repositories.py  # Repository implementations
│   │   ├── tvmaze_client.py # TVMaze API client
│   │   └── ai_generator.py  # HuggingFace integration
│   ├── api/                 # FastAPI layer
│   │   ├── routes.py        # API endpoints
│   │   ├── schemas.py       # Pydantic models
│   │   └── dependencies.py  # Dependency injection
│   └── main.py              # Application entry point
├── tests/                   # Unit tests
│   ├── test_entities.py     # Domain entity tests
│   ├── test_services.py     # Service tests with mocks
│   └── test_repositories.py # Repository tests (in-memory DB)
└── requirements.txt
```

### Frontend Structure (React 19 + TypeScript 5.9.3 + Tailwind CSS 4)

```
frontend/
├── src/
│   ├── api/
│   │   └── client.ts        # API client with error handling
│   ├── components/
│   │   ├── SearchBar.tsx    # Debounced search input
│   │   ├── ShowCard.tsx     # Show card for search results
│   │   ├── EpisodeCard.tsx  # Episode with watch toggle
│   │   ├── CommentsSection.tsx
│   │   ├── AIInsightPanel.tsx
│   │   ├── Modal.tsx
│   │   └── LoadingSpinner.tsx
│   ├── pages/
│   │   ├── SearchPage.tsx   # Main search interface
│   │   └── ShowDetailPage.tsx # Show details with episodes
│   ├── hooks/
│   │   ├── useDebounce.ts   # Debounce hook for search
│   │   └── useLocalStorage.ts
│   ├── types/
│   │   └── index.ts         # TypeScript type definitions
│   └── index.css            # Tailwind CSS + custom styles
├── Dockerfile
└── nginx.conf               # Production nginx configuration
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose v3.3+
- (Optional) HuggingFace API key for AI features

### Run with Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd tv-series

# Start all services (app runs on port 7777)
docker-compose up --build
```

The application will be available at **http://localhost:7777**

### Environment Variables

**Backend** (`backend/env.example`):
```bash
# Database (development uses SQLite, Docker uses PostgreSQL)
DATABASE_URL=sqlite+aiosqlite:///./tv_series.db

# HuggingFace API Key (optional - fallback enabled)
HUGGINGFACE_API_KEY=
```

**Frontend** (`frontend/env.example`):
```bash
# API URL (uses Vite proxy in development)
VITE_API_URL=/api
```

## 💻 Development Setup

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server (proxies /api to backend)
npm run dev
```

Access the app at **http://localhost:5173** (Vite dev server)

## 🧪 Testing

```bash
cd backend

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_services.py

# Run with coverage report
pytest --cov=app --cov-report=html
```

### Test Structure
| File | Description |
|------|-------------|
| `test_entities.py` | Domain entity creation and validation |
| `test_services.py` | Application services with mock dependencies |
| `test_repositories.py` | Repository CRUD operations (in-memory SQLite) |

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/search?q={query}` | Search TV shows |
| GET | `/api/shows/{id}` | Get show details with episodes by season |
| GET | `/api/shows/{id}/watched` | Get watched episode IDs for a show |
| POST | `/api/watched` | Mark episode as watched |
| DELETE | `/api/watched/{show_id}/{episode_id}` | Unmark episode |
| GET | `/api/shows/{id}/comments` | Get show comments |
| GET | `/api/shows/{id}/episodes/{ep_id}/comments` | Get episode comments |
| POST | `/api/comments` | Add a comment |
| DELETE | `/api/comments/{id}` | Delete a comment |
| POST | `/api/insights` | Generate AI insight for show/episode |
| GET | `/api/health` | Health check |

## 🎨 Design Decisions & Trade-offs

| Decision | Rationale | Trade-off |
|----------|-----------|-----------|
| **Clean Architecture** | Testability, maintainability, swappable infrastructure | More boilerplate code |
| **Interface Segregation** | AI, API client, repositories behind interfaces | Requires mock implementations for tests |
| **Simple State (no Redux)** | React state + API calls sufficient for scope | Would need state lib for larger app |
| **AI Fallback Strategy** | Graceful degradation when API unavailable | Fallback insights are generic |
| **SQLite (dev) / PostgreSQL (prod)** | Simple dev setup, reliable production | Minor behavioral differences |
| **Single Container Option** | Jenkins pipeline simplicity | Less granular scaling |

## 🔧 Technology Stack

| Layer | Technologies |
|-------|--------------|
| **Backend** | Python 3.10, FastAPI, SQLAlchemy (async), Pydantic, httpx |
| **Frontend** | React 19, TypeScript 5.9.3, Tailwind CSS 4, Vite 7 |
| **Database** | PostgreSQL 15 (Docker), SQLite (development) |
| **AI** | HuggingFace Inference API (Mistral-7B-Instruct) |
| **Infrastructure** | Docker, Docker Compose v3.3, Nginx |
| **Testing** | pytest, pytest-asyncio, pytest-cov |

## 📋 Project Requirements Checklist

- [x] TV Series Search (TVMaze API)
- [x] Series Details (poster, summary, genres, episodes by season)
- [x] Episode Tracking (mark as watched, persists across reloads)
- [x] Comments (on series and episodes)
- [x] AI-Powered Insights (HuggingFace integration with fallback)
- [x] Clean Architecture / SOLID principles
- [x] Unit tests for business logic
- [x] Docker Compose v3.3 (app + database containers)
- [x] Single command deployment
- [x] Runs on port 7777

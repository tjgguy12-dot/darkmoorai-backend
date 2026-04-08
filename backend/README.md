# DarkmoorAI Backend

🧠 Intelligence, evolved - RAG-powered AI assistant backend

## Features

- 🔍 **RAG Engine** - Retrieval-augmented generation with vector search
- 📚 **Free Knowledge Sources** - Wikipedia, arXiv, PubMed, Open Library, Project Gutenberg
- 🤖 **DeepSeek Integration** - Cost-optimized AI with per-user budgets
- 📄 **Document Processing** - PDF, Word, Excel, images with OCR
- 💰 **Cost Tracking** - $0.10/user/day budget control
- 🔐 **Authentication** - JWT with refresh tokens, API keys
- 📊 **Analytics** - User behavior tracking and reporting
- 🚀 **Async** - FastAPI with async database and Redis

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (asyncpg)
- **Cache**: Redis
- **Vector Store**: FAISS
- **AI**: DeepSeek API, Sentence Transformers
- **Workers**: Celery
- **Monitoring**: Prometheus, Grafana
- **Testing**: pytest

## Quick Start

```bash
# Clone repository
git clone https://github.com/darkmoor/darkmoorai-backend.git
cd darkmoorai-backend

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys

# Start services
docker-compose up -d

# Run migrations
python scripts/init_db.py

# Seed data (optional)
python scripts/seed_data.py

# Start development server
uvicorn app.main:app --reload
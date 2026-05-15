# SmartDoc NLP API Platform

A production-grade document intelligence REST API built with FastAPI, MySQL, and NLP.
Upload any document and get instant AI-powered analysis.

## Features
- JWT Authentication with refresh token rotation
- Role-based access control (admin / user / readonly)
- Automatic NLP analysis on every uploaded document:
  - Extractive summarization
  - Keyword extraction
  - Named Entity Recognition (people, places, organizations)
  - Sentiment analysis
- Async background job processing
- Auto-generated Swagger/OpenAPI documentation

## Tech Stack
- **FastAPI** — REST API framework
- **MySQL** — relational database
- **SQLAlchemy** — ORM for database interactions
- **spaCy** — NLP engine (NER, keywords)
- **JWT (python-jose)** — authentication
- **bcrypt (passlib)** — password hashing
- **Pydantic** — data validation

## Project Structure

smartdoc/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # environment config
│   ├── database.py          # MySQL connection
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── user.py
│   │   └── document.py
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── user.py
│   │   └── document.py
│   ├── routers/             # API route handlers
│   │   ├── auth.py
│   │   └── documents.py
│   ├── services/            # Business logic
│   │   ├── auth_service.py
│   │   └── nlp_service.py
│   └── middleware/          # JWT auth guards
│       └── auth_middleware.py
├── .env                     # environment variables (not committed)
├── requirements.txt
└── README.md

## Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/smartdoc.git
cd smartdoc
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4. Configure environment
Create a `.env` file:
DATABASE_URL=mysql+pymysql://root:yourpassword@localhost:3306/smartdoc
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

### 5. Create MySQL database
```sql
CREATE DATABASE smartdoc;
```

### 6. Run the server
```bash
uvicorn app.main:app --reload
```

Visit **http://127.0.0.1:8000/docs** for interactive API documentation.

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Create new account |
| POST | `/api/v1/auth/login` | Login and get tokens |
| GET | `/api/v1/auth/me` | Get current user profile |
| POST | `/api/v1/auth/refresh` | Refresh access token |

### Documents
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/documents/` | Upload document for NLP analysis |
| GET | `/api/v1/documents/` | List all your documents |
| GET | `/api/v1/documents/{id}` | Get document with NLP results |
| GET | `/api/v1/documents/{id}/status` | Check analysis status |
| DELETE | `/api/v1/documents/{id}` | Delete a document |

## Example Usage

### Register
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "mypassword"}'
```

### Upload Document
```bash
curl -X POST http://localhost:8000/api/v1/documents/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "report.txt",
    "content": "Your document text here..."
  }'
```

### Get NLP Results
```bash
curl http://localhost:8000/api/v1/documents/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Example NLP Response
```json
{
  "id": 1,
  "filename": "report.txt",
  "status": "done",
  "analysis_result": {
    "summary": "AI is transforming technology. Major companies invest in ML research.",
    "keywords": ["artificial intelligence", "machine learning", "python"],
    "sentiment": "POSITIVE",
    "sentiment_score": 0.87,
    "entities": [
      {"text": "Google", "label": "ORG", "description": "Companies, agencies, institutions"},
      {"text": "Microsoft", "label": "ORG", "description": "Companies, agencies, institutions"},
      {"text": "Python", "label": "PRODUCT", "description": "Products"}
    ]
  }
}
```

## Database Schema

```sql
users
├── id (PK, AUTO INCREMENT)
├── email (UNIQUE, INDEX)
├── hashed_password
├── role (admin/user/readonly)
└── created_at

documents
├── id (PK, AUTO INCREMENT)
├── user_id (FK → users.id)
├── filename
├── content
├── status (pending/processing/done/failed)
└── created_at

analysis_results
├── id (PK, AUTO INCREMENT)
├── document_id (FK → documents.id)
├── summary
├── keywords (JSON)
├── sentiment
├── sentiment_score
├── entities (JSON)
└── created_at
```

## Key Design Decisions
- **Async NLP processing** — documents return instantly (202), analysis runs in background
- **JWT + Refresh tokens** — short-lived access tokens (30min) with long-lived refresh tokens (7 days)
- **RBAC** — role-based access control via FastAPI dependency injection
- **Connection pooling** — SQLAlchemy manages MySQL connections efficiently
- **Pydantic validation** — all input/output strictly typed and validated
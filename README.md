# 📝 Todo List API

A clean, fully-featured REST API for managing todos — built with **FastAPI** and **Python 3.10+**.

## ✨ Features

| Feature | Detail |
|---|---|
| Full CRUD | Create, Read, Update (full & partial), Delete |
| Filtering | By `done` status, `priority`, or keyword search |
| Auto Docs | Swagger UI at `/docs` & ReDoc at `/redoc` |
| Validation | Pydantic v2 models with detailed error messages |
| CORS Ready | Accepts requests from any origin |

---

## 🗂 Project Structure

```
todo_api/
├── main.py          # App entry point, all routes
├── models.py        # Pydantic request/response schemas
├── database.py      # In-memory store (swap for SQL/Mongo later)
└── requirements.txt # Python dependencies
```

---

## 🚀 Setup & Run

### 1. Install Python
Download from **https://www.python.org/downloads/** — make sure to tick **"Add Python to PATH"** during install.

### 2. Install dependencies
```bash
cd c:\Users\FABLAB\.gemini\antigravity\scratch\todo_api
pip install -r requirements.txt
```

### 3. Start the server
```bash
uvicorn main:app --reload
```

The API is now live at **http://127.0.0.1:8000** 🎉

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/todos` | List all todos |
| `GET` | `/todos?done=false` | List uncompleted todos |
| `GET` | `/todos?priority=high` | Filter by priority |
| `GET` | `/todos?search=groceries` | Keyword search |
| `GET` | `/todos/{id}` | Get one todo |
| `POST` | `/todos` | Create a todo |
| `PUT` | `/todos/{id}` | Full update |
| `PATCH` | `/todos/{id}` | Partial update |
| `DELETE` | `/todos/{id}` | Delete one todo |
| `DELETE` | `/todos` | Clear all completed |

---

## 📬 Example Requests

### Create a todo
```bash
curl -X POST http://127.0.0.1:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "priority": "high", "due_date": "2026-04-30"}'
```

### Mark as done (PATCH)
```bash
curl -X PATCH http://127.0.0.1:8000/todos/<id> \
  -H "Content-Type: application/json" \
  -d '{"done": true}'
```

### Get only incomplete todos
```bash
curl http://127.0.0.1:8000/todos?done=false
```

---

## 🏗 Upgrading to a Real Database

Replace `database.py` with SQLAlchemy + SQLite (or Postgres):

```python
# Example: SQLite with SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///./todos.db")
SessionLocal = sessionmaker(bind=engine)
```

---

## 🔮 Ideas for Extension

- [ ] JWT Authentication / user accounts
- [ ] Tags / categories
- [ ] Recurring todos
- [ ] Pagination (`?skip=0&limit=20`)
- [ ] WebSocket live updates
- [ ] SQLite or PostgreSQL persistence

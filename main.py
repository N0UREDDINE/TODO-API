"""
Todo List REST API — built with FastAPI
Endpoints:
  GET    /todos          → list all todos (supports ?done=true/false filter)
  GET    /todos/{id}     → get a single todo
  POST   /todos          → create a new todo
  PUT    /todos/{id}     → fully update a todo
  PATCH  /todos/{id}     → partially update a todo (e.g. only mark done)
  DELETE /todos/{id}     → delete a todo
  DELETE /todos          → clear all completed todos

Interactive docs: http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime, timezone
import uuid

from models import TodoCreate, TodoUpdate, TodoPatch, TodoResponse
from database import db

# ── App setup ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="📝 Todo List API",
    description="A clean, fully-featured REST API for managing your todos.",
    version="1.0.0",
    contact={"name": "FABLAB", "email": "fablab@example.com"},
    license_info={"name": "MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    """Health-check / welcome endpoint."""
    return {
        "message": "📝 Todo List API is running!",
        "docs": "http://127.0.0.1:8000/docs",
        "version": "1.0.0",
    }


@app.get("/todos", response_model=List[TodoResponse], tags=["Todos"])
def list_todos(
    done: Optional[bool] = Query(None, description="Filter by completion status"),
    priority: Optional[str] = Query(None, description="Filter by priority: low | medium | high"),
    search: Optional[str] = Query(None, description="Search in title / description"),
):
    """Return all todos. Optionally filter by completion state, priority, or keyword."""
    todos = list(db.values())

    if done is not None:
        todos = [t for t in todos if t["done"] == done]

    if priority:
        todos = [t for t in todos if t["priority"] == priority]

    if search:
        q = search.lower()
        todos = [
            t for t in todos
            if q in t["title"].lower() or q in (t.get("description") or "").lower()
        ]

    # Sort by creation time (newest first)
    todos.sort(key=lambda t: t["created_at"], reverse=True)
    return todos


@app.get("/todos/{todo_id}", response_model=TodoResponse, tags=["Todos"])
def get_todo(todo_id: str):
    """Retrieve a single todo by its ID."""
    todo = db.get(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo '{todo_id}' not found.")
    return todo


@app.post("/todos", response_model=TodoResponse, status_code=201, tags=["Todos"])
def create_todo(payload: TodoCreate):
    """Create a new todo item."""
    todo_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    todo = {
        "id": todo_id,
        "title": payload.title,
        "description": payload.description,
        "done": False,
        "priority": payload.priority,
        "due_date": payload.due_date,
        "created_at": now,
        "updated_at": now,
    }

    db[todo_id] = todo
    return todo


@app.put("/todos/{todo_id}", response_model=TodoResponse, tags=["Todos"])
def update_todo(todo_id: str, payload: TodoUpdate):
    """Fully replace a todo's data (all fields required)."""
    if todo_id not in db:
        raise HTTPException(status_code=404, detail=f"Todo '{todo_id}' not found.")

    now = datetime.now(timezone.utc).isoformat()
    db[todo_id].update({
        "title": payload.title,
        "description": payload.description,
        "done": payload.done,
        "priority": payload.priority,
        "due_date": payload.due_date,
        "updated_at": now,
    })
    return db[todo_id]


@app.patch("/todos/{todo_id}", response_model=TodoResponse, tags=["Todos"])
def patch_todo(todo_id: str, payload: TodoPatch):
    """Partially update a todo (only send the fields you want to change)."""
    if todo_id not in db:
        raise HTTPException(status_code=404, detail=f"Todo '{todo_id}' not found.")

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update.")

    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    db[todo_id].update(updates)
    return db[todo_id]


@app.delete("/todos/{todo_id}", status_code=204, tags=["Todos"])
def delete_todo(todo_id: str):
    """Permanently delete a todo."""
    if todo_id not in db:
        raise HTTPException(status_code=404, detail=f"Todo '{todo_id}' not found.")
    del db[todo_id]


@app.delete("/todos", tags=["Todos"])
def clear_completed():
    """Remove all completed (done=true) todos at once."""
    completed_ids = [tid for tid, t in db.items() if t["done"]]
    for tid in completed_ids:
        del db[tid]
    return {"deleted": len(completed_ids), "message": f"Removed {len(completed_ids)} completed todo(s)."}

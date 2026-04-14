"""
In-memory "database" — a plain dict keyed by todo ID.
For production, swap this with SQLite / PostgreSQL / MongoDB etc.
"""

from typing import Dict, Any

# dict[id_str → todo_dict]
db: Dict[str, Any] = {}

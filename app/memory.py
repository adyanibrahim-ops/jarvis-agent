import sqlite3
from datetime import datetime


DB_NAME = "jarvis_memory.db"


def init_memory():

    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_memory(content: str):

    conn = sqlite3.connect(DB_NAME)

    conn.execute(
        "INSERT INTO memories (content, created_at) VALUES (?, ?)",
        (content, datetime.now().isoformat())
    )

    conn.commit()
    conn.close()


def get_memories():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.execute(
        "SELECT id, content, created_at FROM memories ORDER BY id DESC"
    )

    memories = cursor.fetchall()

    conn.close()

    return memories


def search_memories(query: str):

    conn = sqlite3.connect(DB_NAME)

    words = query.lower().split()

    memories = []

    cursor = conn.execute(
        "SELECT id, content, created_at FROM memories"
    )

    for memory in cursor.fetchall():

        memory_id, content, created_at = memory

        content_lower = content.lower()

        score = sum(
            1 for word in words
            if len(word) > 2 and word in content_lower
        )

        if score > 0:
            memories.append((score, memory))

    conn.close()

    memories.sort(reverse=True, key=lambda x: x[0])

    return [memory for score, memory in memories]


def delete_memory(memory_id: int):

    conn = sqlite3.connect(DB_NAME)

    conn.execute(
        "DELETE FROM memories WHERE id = ?",
        (memory_id,)
    )

    conn.commit()
    conn.close()
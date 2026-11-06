"""
EduRAG Document & Upload Metadata Database
Powered by Python's built-in SQLite3 engine.
"""

from datetime import datetime, timedelta
import hashlib
import logging
import secrets
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("edurag.db")

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "edurag.db"


def init_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                scheme TEXT NOT NULL,
                subject_code TEXT NOT NULL,
                sem TEXT NOT NULL,
                material_type TEXT NOT NULL,
                title TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size_bytes INTEGER NOT NULL,
                file_hash TEXT UNIQUE NOT NULL,
                page_count INTEGER DEFAULT 0,
                is_indexed INTEGER DEFAULT 0,
                chunk_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_sub ON documents(subject_code)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_type ON documents(material_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_hash ON documents(file_hash)")

        # Google OAuth & User Profile Management
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                google_id TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                picture TEXT,
                email_verified INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_email ON users(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_google ON users(google_id)")

        # User Authentication Sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_user ON sessions(user_id)")
        conn.commit()


def calculate_sha256(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


def insert_document(
    scheme: str,
    subject_code: str,
    sem: str,
    material_type: str,
    title: str,
    file_name: str,
    file_path: str,
    file_size_bytes: int,
    file_hash: str,
    page_count: int = 0,
    is_indexed: int = 0,
    chunk_count: int = 0,
) -> Dict[str, Any]:
    init_db()
    doc_id = "doc_" + uuid.uuid4().hex[:12]
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE file_hash = ?", (file_hash,))
        existing = cursor.fetchone()
        if existing:
            return dict(existing)

        cursor.execute("""
            INSERT INTO documents (
                id, scheme, subject_code, sem, material_type, title,
                file_name, file_path, file_size_bytes, file_hash,
                page_count, is_indexed, chunk_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id, scheme, subject_code, sem, material_type, title,
            file_name, file_path, file_size_bytes, file_hash,
            page_count, is_indexed, chunk_count
        ))
        conn.commit()
        cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        return dict(cursor.fetchone())


def list_documents(
    subject_code: Optional[str] = None,
    material_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = "SELECT * FROM documents WHERE 1=1"
        params = []
        if subject_code:
            query += " AND UPPER(subject_code) = ?"
            params.append(subject_code.upper().strip())
        if material_type:
            query += " AND material_type = ?"
            params.append(material_type)
        query += " ORDER BY created_at DESC"
        cursor.execute(query, params)
        return [dict(r) for r in cursor.fetchall()]


def get_document(doc_id: str) -> Optional[Dict[str, Any]]:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def update_document_index_status(doc_id: str, is_indexed: int, chunk_count: int, page_count: int):
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE documents 
            SET is_indexed = ?, chunk_count = ?, page_count = ?
            WHERE id = ?
        """, (is_indexed, chunk_count, page_count, doc_id))
        conn.commit()


def delete_document(doc_id: str) -> Optional[str]:
    init_db()
    doc = get_document(doc_id)
    if not doc:
        return None
    file_path = doc["file_path"]
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        conn.commit()
    try:
        p = Path(file_path)
        if p.exists():
            p.unlink()
    except Exception as e:
        logger.warning(f"Failed deleting file {file_path}: {e}")
    return file_path


# ---------------------------------------------------------------------------
# Google Auth & Session Storage
# ---------------------------------------------------------------------------
def upsert_google_user(
    google_id: str,
    email: str,
    name: Optional[str] = None,
    picture: Optional[str] = None,
    email_verified: bool = True,
) -> Dict[str, Any]:
    """Insert or update a Google authenticated user record."""
    init_db()
    norm_email = email.strip().lower()
    now_iso = datetime.utcnow().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE google_id = ? OR email = ?", (google_id, norm_email))
        row = cursor.fetchone()
        if row:
            user_id = row["id"]
            cursor.execute("""
                UPDATE users
                SET google_id = ?, name = COALESCE(?, name), picture = COALESCE(?, picture),
                    email_verified = ?, last_login = ?
                WHERE id = ?
            """, (google_id, name, picture, 1 if email_verified else 0, now_iso, user_id))
        else:
            user_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO users (id, google_id, email, name, picture, email_verified, created_at, last_login)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, google_id, norm_email, name or "", picture or "", 1 if email_verified else 0, now_iso, now_iso))
        conn.commit()
        cursor.execute("SELECT id, google_id, email, name, picture, email_verified, created_at, last_login FROM users WHERE id = ?", (user_id,))
        return dict(cursor.fetchone())


def create_user_session(user_id: str, duration_days: int = 30) -> str:
    """Generate and store a cryptographic session token for an authenticated user."""
    init_db()
    token = secrets.token_urlsafe(32)
    expires_at = (datetime.utcnow() + timedelta(days=duration_days)).isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (token, user_id, expires_at)
            VALUES (?, ?, ?)
        """, (token, user_id, expires_at))
        conn.commit()
    return token


def get_user_from_session(token: str) -> Optional[Dict[str, Any]]:
    """Retrieve the user associated with a valid, non-expired session token."""
    if not token or not token.strip():
        return None
    init_db()
    now_iso = datetime.utcnow().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.google_id, u.email, u.name, u.picture, u.email_verified, u.created_at, u.last_login
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ? AND s.expires_at > ?
        """, (token.strip(), now_iso))
        row = cursor.fetchone()
        return dict(row) if row else None


def delete_session(token: str) -> bool:
    """Revoke and delete a session token on logout."""
    if not token:
        return False
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE token = ?", (token.strip(),))
        deleted = cursor.rowcount > 0
        conn.commit()
        return deleted

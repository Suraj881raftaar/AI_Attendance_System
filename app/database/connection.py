"""
Database connection management for AI-Enabled Smart Attendance System.
Handles SQLite connection lifecycle, foreign key enforcement, and error handling.
"""

import sqlite3
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional, Union

from app.config import get_db_path

logger = logging.getLogger(__name__)


def get_connection(db_path: Optional[Union[str, Path]] = None) -> sqlite3.Connection:
    """
    Create and return a raw SQLite database connection with row factory and foreign keys enabled.
    
    :param db_path: Optional path to SQLite database. Defaults to config database path.
    :return: sqlite3.Connection instance.
    """
    if db_path is None:
        target_path = get_db_path()
    else:
        target_path = Path(db_path)

    # Ensure parent directory exists if using file path
    if str(target_path) != ":memory:":
        target_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        conn = sqlite3.connect(str(target_path))
        conn.row_factory = sqlite3.Row
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Failed to connect to SQLite database at '{target_path}': {e}")
        raise


@contextmanager
def get_db_connection(db_path: Optional[Union[str, Path]] = None) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for database connections.
    Automatically commits transactions on success or rolls back on exception.
    Ensures connection is closed cleanly.
    """
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database transaction error: {e}")
        raise
    finally:
        conn.close()


import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).parent / "alexandria.db"


def get_connection():

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():

    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS directories (

                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT NOT NULL UNIQUE,
                parent TEXT,
                modified REAL,
                depth INTEGER,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS files (

                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT NOT NULL UNIQUE,
                extension TEXT,
                size INTEGER,
                modified REAL,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )
        """)

        connection.commit()


def save_directories(directories):

    with get_connection() as connection:

        connection.executemany("""
            INSERT INTO directories (
                name, path, parent, modified, depth
            )

            VALUES (?, ?, ?, ?, ?)

            ON CONFLICT(path) DO UPDATE SET

                name = excluded.name,
                parent = excluded.parent,
                modified = excluded.modified,
                depth = excluded.depth

        """, [
            (
                directory["name"],
                directory["path"],
                directory["parent"],
                directory["modified"],
                directory["depth"]
            )
            for directory in directories
        ])

        connection.commit()


def save_files(files):

    with get_connection() as connection:

        connection.executemany("""
            INSERT INTO files (
                name, path, extension, size, modified
            )

            VALUES (?, ?, ?, ?, ?)

            ON CONFLICT(path) DO UPDATE SET

                name = excluded.name,
                extension = excluded.extension,
                size = excluded.size,
                modified = excluded.modified

        """, [
            (
                file["name"],
                file["path"],
                file["extension"],
                file["size"],
                file["modified"]
            )
            for file in files
        ])

        connection.commit()


def get_all_directories():

    with get_connection() as connection:

        rows = connection.execute("""
            SELECT * FROM directories
            ORDER BY path
        """).fetchall()

        return [dict(row) for row in rows]


def count_files():

    with get_connection() as connection:

        result = connection.execute("""
            SELECT COUNT(*) AS total
            FROM files
        """).fetchone()

        return result["total"]


if __name__ == "__main__":

    initialize_database()

    print("Alexandria database initialized.")


import sqlite3
from pathlib import Path
import json
import os


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

        connection.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                root_path TEXT NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                finished_at TIMESTAMP,
                status TEXT NOT NULL DEFAULT 'running',
                files_discovered INTEGER DEFAULT 0,
                directories_scanned INTEGER DEFAULT 0,
                errors INTEGER DEFAULT 0
            )
        """)

        scan_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(scans)"
            ).fetchall()
        }

        if "scope" not in scan_columns:
            connection.execute("""
                ALTER TABLE scans
                ADD COLUMN scope TEXT NOT NULL DEFAULT '{}'
            """)

        if "is_comprehensive" not in scan_columns:
            connection.execute("""
                ALTER TABLE scans
                ADD COLUMN is_comprehensive INTEGER NOT NULL DEFAULT 0
            """)

        # Migrate existing databases without losing stored files.
        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(files)"
            ).fetchall()
        }

        if "last_seen_scan_id" not in columns:
            connection.execute("""
                ALTER TABLE files
                ADD COLUMN last_seen_scan_id INTEGER
            """)

        connection.commit()


def start_scan(root_path, scope=None, is_comprehensive=False):

    with get_connection() as connection:

        cursor = connection.execute("""
            INSERT INTO scans (
                root_path,
                scope,
                is_comprehensive
            )
            VALUES (?, ?, ?)
        """, (
            str(root_path),
            json.dumps(scope or {}),
            int(is_comprehensive)
        ))

        connection.commit()

        return cursor.lastrowid

def finish_scan(
    scan_id,
    status,
    files_discovered,
    directories_scanned,
    errors
):

    with get_connection() as connection:

        connection.execute("""
            UPDATE scans

            SET
                finished_at = CURRENT_TIMESTAMP,
                status = ?,
                files_discovered = ?,
                directories_scanned = ?,
                errors = ?

            WHERE id = ?
        """, (
            status,
            files_discovered,
            directories_scanned,
            errors,
            scan_id
        ))

        connection.commit()

def get_stale_files(scan_id):

    with get_connection() as connection:

        # Retrieve the scan.
        scan = connection.execute("""
            SELECT *
            FROM scans
            WHERE id = ?
        """, (scan_id,)).fetchone()

        if scan is None:
            raise ValueError(f"Scan {scan_id} does not exist.")

        # Verify that the scan completed successfully.
        if scan["status"] != "completed":
            raise ValueError("Cannot detect stale files: scan is not completed.")

        if scan["errors"] != 0:
            raise ValueError("Cannot detect stale files: scan contains errors.")

        # Verify that the scan covered the entire requested root.
        if scan["is_comprehensive"] != 1:
            raise ValueError("Cannot detect stale files: scan was not comprehensive.")

        # Ensure this is the latest scan for this root.
        latest_scan = connection.execute("""
            SELECT MAX(id)
            FROM scans
            WHERE root_path = ?
        """, (scan["root_path"],)).fetchone()[0]

        if latest_scan != scan_id:
            raise ValueError("Cannot use an outdated scan for stale-file detection.")

        root_path = os.path.normcase(
            os.path.abspath(scan["root_path"])
        )

        # Retrieve files not encountered in this scan.
        rows = connection.execute("""
            SELECT *
            FROM files
            WHERE last_seen_scan_id IS NOT ?
              AND discovered_at <= ?
        """, (
            scan_id,
            scan["started_at"]
        )).fetchall()

        stale_files = []

        for row in rows:

            file_path = os.path.normcase(
                os.path.abspath(row["path"])
            )

            try:
                if os.path.commonpath(
                    [root_path, file_path]
                ) == root_path:

                    stale_files.append(dict(row))

            except ValueError:
                continue

        return stale_files


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


def save_files(files, scan_id=None):

    with get_connection() as connection:

        connection.executemany("""
            INSERT INTO files (
                name, path, extension, size, modified,
                last_seen_scan_id
            )

            VALUES (?, ?, ?, ?, ?, ?)

            ON CONFLICT(path) DO UPDATE SET

                name = excluded.name,
                extension = excluded.extension,
                size = excluded.size,
                modified = excluded.modified,
                last_seen_scan_id = COALESCE(
                    excluded.last_seen_scan_id,
                    files.last_seen_scan_id
                )

        """, [
            (
                file["name"],
                file["path"],
                file["extension"],
                file["size"],
                file["modified"],
                scan_id
            )
            for file in files
        ])

        connection.commit()

def classify_files(files):

    new_files = []
    updated_files = []
    unchanged_files = []

    with get_connection() as connection:

        for file in files:

            existing = connection.execute("""
                SELECT *
                FROM files
                WHERE path = ?
            """, (file["path"],)).fetchone()

            if existing is None:
                new_files.append(file)
                continue

            # Compare the existing metadata with the discovered metadata.
            changed = (
                existing["name"] != file["name"]
                or existing["extension"] != file["extension"]
                or existing["size"] != file["size"]
                or existing["modified"] != file["modified"]
            )

            if changed:
                updated_files.append(file)
            else:
                unchanged_files.append(file)

    return {
        "new": new_files,
        "updated": updated_files,
        "unchanged": unchanged_files
    }


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

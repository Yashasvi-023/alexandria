
from pathlib import Path

from storage.database import get_connection


# -----------------------------
# DIRECTORY RETRIEVAL
# -----------------------------

def search_directories(term, limit=50):

    if not term.strip():
        raise ValueError("Search term cannot be empty.")

    if limit < 1:
        raise ValueError("Limit must be at least 1.")

    with get_connection() as connection:

        rows = connection.execute("""
            SELECT name, path, parent, modified, depth
            FROM directories
            WHERE
                instr(lower(name), lower(?)) > 0
                OR instr(lower(path), lower(?)) > 0
            ORDER BY name
            LIMIT ?
        """, (term, term, limit)).fetchall()

        return [dict(row) for row in rows]


def find_directory(path):

    with get_connection() as connection:

        row = connection.execute("""
            SELECT name, path, parent, modified, depth
            FROM directories
            WHERE lower(path) = lower(?)
        """, (str(path),)).fetchone()

        return dict(row) if row else None


def get_children(parent_path, limit=100):

    if limit < 1:
        raise ValueError("Limit must be at least 1.")

    with get_connection() as connection:

        rows = connection.execute("""
            SELECT name, path, parent, modified, depth
            FROM directories
            WHERE lower(parent) = lower(?)
            ORDER BY name
            LIMIT ?
        """, (str(parent_path), limit)).fetchall()

        return [dict(row) for row in rows]


def count_directories():

    with get_connection() as connection:

        result = connection.execute("""
            SELECT COUNT(*) AS total
            FROM directories
        """).fetchone()

        return result["total"]


def get_parent(directory_path):

    directory = find_directory(directory_path)

    if not directory:
        return None

    return find_directory(directory["parent"])


def get_siblings(directory_path):

    directory = find_directory(directory_path)

    if not directory:
        return []

    with get_connection() as connection:

        rows = connection.execute("""
            SELECT name, path, parent, modified, depth
            FROM directories
            WHERE lower(parent) = lower(?)
            AND lower(path) != lower(?)
            ORDER BY name
        """, (
            directory["parent"],
            directory["path"]
        )).fetchall()

        return [dict(row) for row in rows]


def get_ancestors(directory_path):

    ancestors = []
    current = find_directory(directory_path)

    while current:

        parent = find_directory(current["parent"])

        if not parent:
            break

        ancestors.append(parent)
        current = parent

    return ancestors


def get_descendants(directory_path):

    directory = find_directory(directory_path)

    if not directory:
        return []

    prefix = directory["path"].rstrip("\\/") + "\\"

    with get_connection() as connection:

        rows = connection.execute("""
            SELECT name, path, parent, modified, depth
            FROM directories
            WHERE substr(lower(path), 1, length(lower(?))) = lower(?)
            ORDER BY depth, path
        """, (prefix, prefix)).fetchall()

        return [dict(row) for row in rows]


# -----------------------------
# FILE RETRIEVAL
# -----------------------------

def search_files(term=None, extension=None, limit=50):

    if not term and not extension:
        raise ValueError("Provide a search term or extension.")

    if limit < 1:
        raise ValueError("Limit must be at least 1.")

    if extension:
        extension = extension.lower()

        if not extension.startswith("."):
            extension = "." + extension

    conditions = []
    parameters = []

    if term:
        conditions.append("""
            (
                instr(lower(name), lower(?)) > 0
                OR instr(lower(path), lower(?)) > 0
            )
        """)
        parameters.extend([term, term])

    if extension:
        conditions.append("lower(extension) = ?")
        parameters.append(extension)

    query = """
        SELECT name, path, extension, size, modified
        FROM files
        WHERE """ + " AND ".join(conditions) + """
        ORDER BY name
        LIMIT ?
    """

    parameters.append(limit)

    with get_connection() as connection:

        rows = connection.execute(
            query, parameters
        ).fetchall()

        return [dict(row) for row in rows]


def get_files_in_directory(directory_path, recursive=False):

    root = Path(directory_path).resolve()
    prefix = str(root).rstrip("\\/") + "\\"

    with get_connection() as connection:

        rows = connection.execute("""
            SELECT name, path, extension, size, modified
            FROM files
            WHERE substr(lower(path), 1, length(lower(?))) = lower(?)
            ORDER BY name
        """, (prefix, prefix)).fetchall()

        results = [dict(row) for row in rows]

    if not recursive:

        results = [
            file for file in results
            if Path(file["path"]).parent == root
        ]

    return results


def get_largest_files(directory_path=None, limit=10):

    if limit < 1:
        raise ValueError("Limit must be at least 1.")

    with get_connection() as connection:

        if directory_path:

            root = Path(directory_path).resolve()
            prefix = str(root).rstrip("\\/") + "\\"

            rows = connection.execute("""
                SELECT name, path, extension, size, modified
                FROM files
                WHERE substr(lower(path), 1, length(lower(?))) = lower(?)
                ORDER BY size DESC
                LIMIT ?
            """, (prefix, prefix, limit)).fetchall()

        else:

            rows = connection.execute("""
                SELECT name, path, extension, size, modified
                FROM files
                ORDER BY size DESC
                LIMIT ?
            """, (limit,)).fetchall()

        return [dict(row) for row in rows]

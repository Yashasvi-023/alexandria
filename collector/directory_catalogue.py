
import os
import stat
import argparse
from pathlib import Path
from datetime import datetime

from storage.database import initialize_database, save_directories


def build_catalogue(root_path, max_depth=5, excluded_dirs=None):

    root = Path(root_path).expanduser().resolve()

    if not root.exists():
        raise FileNotFoundError(root)

    if not root.is_dir():
        raise NotADirectoryError(root)

    excluded_dirs = {
        name.lower() for name in (excluded_dirs or [])
    }

    catalogue = []
    errors = 0
    scanned = 0

    stack = [(root, 0)]

    while stack:

        current, depth = stack.pop()
        scanned += 1

        if depth >= max_depth:
            continue

        try:
            with os.scandir(current) as entries:

                for entry in entries:

                    try:
                        info = entry.stat(follow_symlinks=False)

                        attributes = getattr(
                            info, "st_file_attributes", 0
                        )

                        if attributes & getattr(
                            stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400
                        ):
                            continue

                        if not stat.S_ISDIR(info.st_mode):
                            continue

                        if entry.name.lower() in excluded_dirs:
                            continue

                        directory = Path(entry.path)

                        catalogue.append({
                            "name": entry.name,
                            "path": str(directory),
                            "parent": str(current),
                            "modified": info.st_mtime,
                            "depth": depth + 1
                        })

                        stack.append((directory, depth + 1))

                    except OSError:
                        errors += 1

        except OSError:
            errors += 1

    return catalogue, errors, scanned


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Alexandria Directory Catalogue"
    )

    parser.add_argument("path", help="Starting directory")

    parser.add_argument(
        "--max-depth",
        type=int,
        default=5,
        help="Maximum directory depth"
    )

    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Directory names to exclude. Can be repeated."
    )

    parser.add_argument(
        "--show",
        type=int,
        default=0,
        help="Number of directory entries to display"
    )

    args = parser.parse_args()

    if args.max_depth < 0 or args.show < 0:
        parser.error("--max-depth and --show cannot be negative")

    try:

        directories, errors, scanned = build_catalogue(
            args.path,
            max_depth=args.max_depth,
            excluded_dirs=args.exclude
        )

        # Initialise Alexandria's database.
        initialize_database()

        # Persist the discovered directories.
        save_directories(directories)

        print("\nALEXANDRIA DIRECTORY CATALOGUE\n")

        if args.show > 0:

            for directory in directories[:args.show]:

                modified = datetime.fromtimestamp(
                    directory["modified"]
                ).strftime("%Y-%m-%d %H:%M:%S")

                print(f"Name:     {directory['name']}")
                print(f"Path:     {directory['path']}")
                print(f"Parent:   {directory['parent']}")
                print(f"Depth:    {directory['depth']}")
                print(f"Modified: {modified}")
                print("-" * 50)

        print("\nCATALOGUE SUMMARY")
        print(f"Root:                  {args.path}")
        print(f"Directories discovered: {len(directories)}")
        print(f"Directories scanned:    {scanned}")
        print(f"Maximum depth:          {args.max_depth}")
        print(f"Excluded names:         {args.exclude}")
        print(f"Scan errors:            {errors}")
        print(f"Directories saved:      {len(directories)}")

    except (FileNotFoundError, NotADirectoryError) as error:
        print(f"\nError: {error}")

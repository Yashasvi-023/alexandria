
import argparse

from collector.discovery import discover
from storage.database import initialize_database, save_files, count_files


def main():

    parser = argparse.ArgumentParser(
        description="Alexandria File Catalogue"
    )

    parser.add_argument("path", help="Directory to catalogue")

    parser.add_argument(
        "--extension",
        help="Filter by extension, e.g. .py"
    )

    parser.add_argument(
        "--min-size",
        type=int,
        default=0
    )

    parser.add_argument(
        "--max-size",
        type=int,
        default=None
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None
    )

    parser.add_argument(
        "--exclude",
        action="append",
        default=[]
    )

    parser.add_argument(
        "--no-recursive",
        action="store_true"
    )

    args = parser.parse_args()

    if args.min_size < 0:
        parser.error("--min-size cannot be negative")

    if args.max_size is not None and args.max_size < 0:
        parser.error("--max-size cannot be negative")

    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be at least 1")

    if args.max_size is not None and args.max_size < args.min_size:
        parser.error("--max-size cannot be smaller than --min-size")

    try:

        files = discover(
            path=args.path,
            extension=args.extension,
            min_size=args.min_size,
            max_size=args.max_size,
            recursive=not args.no_recursive,
            limit=args.limit,
            excluded_dirs=args.exclude
        )

        initialize_database()
        save_files(files)

        print("\nALEXANDRIA FILE CATALOGUE\n")

        for file in files[:10]:

            print(f"Name:      {file['name']}")
            print(f"Extension: {file['extension']}")
            print(f"Size:      {file['size']} bytes")
            print(f"Path:      {file['path']}")
            print("-" * 50)

        print("\nCATALOGUE SUMMARY")
        print(f"Files discovered: {len(files)}")
        print(f"Total files stored: {count_files()}")

    except (FileNotFoundError, NotADirectoryError) as error:

        print(f"\nError: {error}")


if __name__ == "__main__":
    main()

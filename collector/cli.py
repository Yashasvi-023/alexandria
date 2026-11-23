
import argparse
from collector.discovery import discover


def main():
    parser = argparse.ArgumentParser(
        description="Alexandria File Discovery"
    )

    parser.add_argument("path", help="Directory to search")
    parser.add_argument("--extension", help="Filter by extension")
    parser.add_argument("--min-size", type=int, default=0)
    parser.add_argument("--max-size", type=int, default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--no-recursive", action="store_true")

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
        result = discover(
            path=args.path,
            extension=args.extension,
            min_size=args.min_size,
            max_size=args.max_size,
            recursive=not args.no_recursive,
            limit=args.limit,
            excluded_dirs=args.exclude
        )

        print("\nALEXANDRIA FILE DISCOVERY\n")

        for file in result.files:
            print(
                f"{file['name']} | "
                f"{file['size'] / (1024 ** 2):.2f} MB"
            )

        print("\nDISCOVERY SUMMARY")
        print(f"Files discovered: {len(result.files)}")
        print(f"Directories scanned: {result.scanned_directories}")
        print(f"Errors encountered: {len(result.errors)}")

        if result.errors:
            print("\nDISCOVERY ERRORS")
            for error in result.errors:
                print(error)

    except (FileNotFoundError, NotADirectoryError) as error:
        print(f"\nError: {error}")


if __name__ == "__main__":
    main()

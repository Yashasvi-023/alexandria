
import argparse

from collector.discovery import discover
from storage.database import (
    initialize_database,
    start_scan,
    finish_scan,
    save_files,
    count_files,
    classify_files,
    get_stale_files
)


def main():
    parser = argparse.ArgumentParser(
        description="Alexandria File Catalogue"
    )

    parser.add_argument("path", help="Directory to catalogue")
    parser.add_argument("--extension", help="Filter by extension, e.g. .py")
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

    initialize_database()

    scope = {
        "extension": args.extension,
        "min_size": args.min_size,
        "max_size": args.max_size,
        "limit": args.limit,
        "recursive": not args.no_recursive,
        "excluded_dirs": args.exclude
    }

    is_comprehensive = (
        args.extension is None
        and args.min_size == 0
        and args.max_size is None
        and args.limit is None
        and not args.no_recursive
        and not args.exclude
    )

    scan_id = start_scan(
        args.path,
        scope=scope,
        is_comprehensive=is_comprehensive
    )

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

        files = result.files

        classification = classify_files(files)

        save_files(files, scan_id=scan_id)

        # A scan with discovery errors is incomplete.
        status = "completed" if not result.errors else "incomplete"

        finish_scan(
            scan_id=scan_id,
            status=status,
            files_discovered=len(files),
            directories_scanned=result.scanned_directories,
            errors=len(result.errors)
        )

        print("\nALEXANDRIA FILE CATALOGUE\n")

        for file in files[:10]:
            print(f"Name:      {file['name']}")
            print(f"Extension: {file['extension']}")
            print(f"Size:      {file['size']} bytes")
            print(f"Path:      {file['path']}")
            print("-" * 50)

        print("\nCATALOGUE SUMMARY")
        print(f"Scan ID: {scan_id}")
        print(f"Scan status: {status}")
        print(f"Files discovered: {len(files)}")
        print(f"Directories scanned: {result.scanned_directories}")
        print(f"Errors encountered: {len(result.errors)}")
        print(f"Total files stored: {count_files()}")

        print("\nSYNCHRONIZATION REPORT")

        print(f"New files:       {len(classification['new'])}")
        print(f"Updated files:   {len(classification['updated'])}")
        print(f"Unchanged files: {len(classification['unchanged'])}")

        try:
            stale_files = get_stale_files(scan_id)

            print(f"Stale candidates: {len(stale_files)}")

            for file in stale_files:
                print(f"  - {file['name']}")

        except ValueError as error:
            print(f"Stale detection unavailable: {error}")

        print("\nACTION: DRY RUN")
        print("No stale database records were deleted.")

        if result.errors:
            print("\nDISCOVERY ERRORS")
            for error in result.errors:
                print(error)

    except Exception:
        finish_scan(
            scan_id=scan_id,
            status="failed",
            files_discovered=0,
            directories_scanned=0,
            errors=1
        )
        raise


if __name__ == "__main__":
    main()

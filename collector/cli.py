
import argparse
from discovery import discover


def main():

    parser = argparse.ArgumentParser(
        description="Alexandria File Discovery"
    )

    parser.add_argument("path", help="Directory to search")
    parser.add_argument("--extension", help="Filter by file extension")
    parser.add_argument("--min-size", type=int, default=0)
    parser.add_argument("--max-size", type=int, default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--no-recursive", action="store_true")

    args = parser.parse_args()

    try:
        files = discover(
            path=args.path,
            extension=args.extension,
            min_size=args.min_size,
            max_size=args.max_size,
            recursive=not args.no_recursive,
            limit=args.limit
        )

        print("\nALEXANDRIA DISCOVERY RESULTS\n")

        if not files:
            print("No matching files found.")

        for file in files:
            print(
                f"{file['name']} | "
                f"{file['size'] / (1024 ** 2):.2f} MB | "
                f"{file['path']}"
            )

        print(f"\nTotal results: {len(files)}")

    except (FileNotFoundError, NotADirectoryError) as error:
        print(f"\nError: {error}")


if __name__ == "__main__":
    main()


import os
import stat
from pathlib import Path


def format_size(size):
    units = ["B", "KB", "MB", "GB", "TB"]

    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

    return f"{size:.2f} PB"


def scan_directory(root):
    total_size = 0
    file_count = 0
    directory_count = 0
    errors = 0
    largest_file = (0, None)

    stack = [root]

    while stack:
        current = stack.pop()

        try:
            with os.scandir(current) as entries:

                for entry in entries:
                    try:
                        info = entry.stat(follow_symlinks=False)

                        # Skip symbolic links and Windows junctions
                        if info.st_file_attributes & getattr(
                            stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400
                        ):
                            continue

                        if stat.S_ISDIR(info.st_mode):
                            directory_count += 1
                            stack.append(Path(entry.path))

                        elif stat.S_ISREG(info.st_mode):
                            size = info.st_size

                            total_size += size
                            file_count += 1

                            if size > largest_file[0]:
                                largest_file = (size, entry.path)

                    except OSError:
                        errors += 1

        except OSError:
            errors += 1

    return {
        "path": str(root),
        "total_size": total_size,
        "files": file_count,
        "directories": directory_count,
        "largest_file": largest_file[1],
        "largest_file_size": largest_file[0],
        "errors": errors
    }


def main():
    home = Path.home()

    folders = [
        "Desktop",
        "Documents",
        "Downloads",
        "Pictures",
        "Videos",
        "Music"
    ]

    print("\n========== ALEXANDRIA ==========")
    print("Filesystem Discovery")
    print("================================\n")

    for folder in folders:
        path = home / folder

        if not path.is_dir():
            continue

        result = scan_directory(path)

        print(f"\nFolder: {folder}")
        print(f"Location: {result['path']}")
        print(f"Total Size: {format_size(result['total_size'])}")
        print(f"Files: {result['files']}")
        print(f"Subdirectories: {result['directories']}")
        print(f"Scan Errors: {result['errors']}")

        if result["largest_file"]:
            print(
                f"Largest File: {result['largest_file']}"
            )
            print(
                f"File Size: {format_size(result['largest_file_size'])}"
            )

    print("\n================================")
    print("Discovery Complete.")
    print("================================")


if __name__ == "__main__":
    main()


import os
import stat
from pathlib import Path


def discover(
    path,
    extension=None,
    min_size=0,
    max_size=None,
    recursive=True,
    limit=None,
    excluded_dirs=None
):

    path = Path(path).expanduser()

    if not path.exists():
        raise FileNotFoundError(path)

    if not path.is_dir():
        raise NotADirectoryError(path)

    excluded_dirs = {
        name.lower() for name in (excluded_dirs or [])
    }

    results = []
    stack = [path]

    while stack:

        current = stack.pop()

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

                        if stat.S_ISDIR(info.st_mode):

                            if (
                                recursive
                                and entry.name.lower() not in excluded_dirs
                            ):
                                stack.append(Path(entry.path))

                            continue

                        if not stat.S_ISREG(info.st_mode):
                            continue

                        size = info.st_size

                        if size < min_size:
                            continue

                        if max_size is not None and size > max_size:
                            continue

                        file_path = Path(entry.path)

                        if (
                            extension
                            and file_path.suffix.lower() != extension.lower()
                        ):
                            continue

                        results.append({
                            "name": entry.name,
                            "path": str(file_path),
                            "extension": file_path.suffix.lower(),
                            "size": size,
                            "modified": info.st_mtime
                        })

                    except OSError:
                        continue

        except OSError:
            continue

    results.sort(
        key=lambda item: item["size"],
        reverse=True
    )

    if limit is not None:
        results = results[:limit]

    return results


if __name__ == "__main__":

    files = discover(
        path=r"C:\Program Files",
        min_size=50 * 1024 * 1024,
        limit=10
    )

    print("\nALEXANDRIA DISCOVERY RESULTS\n")

    for file in files:

        print(
            f"{file['name']} | "
            f"{file['size'] / (1024 ** 2):.2f} MB"
        )

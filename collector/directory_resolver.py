
import os
import sys
import winreg
import argparse
from pathlib import Path


def get_windows_folders():

    registry_path = (
        r"Software\Microsoft\Windows\CurrentVersion"
        r"\Explorer\User Shell Folders"
    )

    folders = {}

    registry_mapping = {
        "desktop": "Desktop",
        "documents": "Personal",
        "downloads": "{374DE290-123F-4565-9164-39C4925E467B}",
        "pictures": "My Pictures",
        "music": "My Music",
        "videos": "My Video"
    }

    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        registry_path
    ) as key:

        for name, registry_name in registry_mapping.items():

            try:
                value, _ = winreg.QueryValueEx(key, registry_name)

                folders[name] = Path(
                    os.path.expandvars(value)
                )

            except FileNotFoundError:
                continue

    return folders


def get_known_directories():

    folders = get_windows_folders()

    folders.update({
        "home": Path.home(),
        "program files": Path(os.environ.get("ProgramFiles", r"C:\Program Files")),
        "program files x86": Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")),
        "windows": Path(os.environ.get("WINDIR", r"C:\Windows"))
    })

    return folders


def resolve_directory(name):

    name = name.strip().lower()

    folders = get_known_directories()

    if name not in folders:
        raise ValueError(f"Unknown directory: {name}")

    path = folders[name]

    if not path.exists():
        raise FileNotFoundError(f"Directory does not exist: {path}")

    if not path.is_dir():
        raise NotADirectoryError(f"Not a directory: {path}")

    return path.resolve()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Alexandria Directory Resolver"
    )

    parser.add_argument(
        "directory",
        help="Name of a known directory"
    )

    args = parser.parse_args()

    try:
        result = resolve_directory(args.directory)

        print("\nALEXANDRIA DIRECTORY RESOLVER\n")
        print(f"Requested: {args.directory}")
        print(f"Resolved:  {result}")

    except (ValueError, FileNotFoundError, NotADirectoryError) as error:
        print(f"\nError: {error}")

from datetime import datetime
from pathlib import Path
from typing import List


def get_files(path: str, extensions: tuple) -> List[Path]:
    """Given a string path, Returns the desired file extensions"""
    all_files = []
    for ext in extensions:
        all_files.extend(Path(path).rglob(ext, recurse_symlinks=True))
    return all_files

def time_convert(atime):
    """Return a datetime object from timestamp"""
    return datetime.fromtimestamp(atime).date()


def size_convert(size: int):
    """Convert to human readable size"""
    newform = format(size / 1024 ** 3, ".3f")
    return newform + "GiB"

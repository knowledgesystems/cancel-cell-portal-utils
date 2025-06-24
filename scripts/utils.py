from datetime import datetime
from pathlib import Path
from typing import List

import anndata as ad

def get_files(path: str, extensions: tuple) -> List[Path]:
    """Given a string path, Returns the desired file extensions"""
    all_files = []
    for ext in extensions:
        all_files.extend(Path(path).rglob(ext, recurse_symlinks=True))
    return all_files

def convert_h5ad_to_zarr(fpath: str | Path):
    # Read in h5ad file
    if isinstance(fpath, str):
        file = Path(fpath)
    else:
        file = fpath
    h5ad = ad.read_h5ad(file)

    # Write out zarr
    h5ad.write_zarr(Path(f"{file.name}.output.zarr"))

def time_convert(atime):
    """Return a datetime object from timestamp"""
    return datetime.fromtimestamp(atime).date()


def size_convert(size: int):
    """Convert to human readable size"""
    newform = format(size / 1024 ** 3, ".3f")
    return newform + "GiB"

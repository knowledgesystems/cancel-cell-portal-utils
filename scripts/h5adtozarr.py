import argparse
from pathlib import Path

import anndata as ad


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description="Helper script to convert h5ad to zarr format")
    parser.add_argument("--input", "-i", help="Input h5ad file", required=True)
    parser.add_argument("--output", "-o", help="Output zarr file")
    args = parser.parse_args()

    # Read in h5ad file
    file = Path(args.input)
    h5ad = ad.read_h5ad(file)

    # Write out zarr
    h5ad.write_zarr(Path(f"{file.name}.output.zarr"))

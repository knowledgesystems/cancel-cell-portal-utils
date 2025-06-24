import argparse

from scripts.utils import convert_h5ad_to_zarr


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description="Helper script to convert h5ad to zarr format")
    parser.add_argument("--input", "-i", help="Input h5ad file", required=True)
    parser.add_argument("--output", "-o", help="Output zarr file")
    args = parser.parse_args()

    convert_h5ad_to_zarr(args.input)

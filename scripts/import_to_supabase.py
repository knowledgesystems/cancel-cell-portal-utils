import os
import argparse
import json

# 3rd Party imports
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Setup the Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def select_datasets():
    response = (
        supabase.table("datasets")
        .select("*")
        .execute()
    )
    print(response)


def main(args):
    # Read the records file
    with open(args.input_file) as fh:
        data = json.load(fh)
        print(data)

    # INSERT SUPABASE
    if args.dry_run:
        print(f"{len(data)} Records to insert")
    else:
        response = (
            supabase.table("datasets")
            .insert(data)
            .execute()
        )
        print(response)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--input-file", "-i", required=True, 
        help="Datasets metadata records to insert into the datasets table")
    parser.add_argument("--dry-run", help="Skip database insert")
    args = parser.parse_args()

    main(args)


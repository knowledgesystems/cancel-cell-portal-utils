"""
Goal: We want to view the cell_types across all of the h5ad datasets we have.
It would be useful to create a "heatmap"/table, which can distinguish datasets
at a glance.

Problems:
    ** Metadata harmonization **
    - Unknown/First-time seen datasets may not contain an annotation for 
    `cell_type`
    - CellxGene requires a `cell_type` annotation for each cell_id. This is part
    of their data upload & curation process and can be found in their schema.
        * `cell_type` and `cell_type_ontology_id` are both useful for dataset
        integration

So, we can do this for CellxGene datasets. Since `cell_type` is well defined.
1. btc-gbm datasets do not have any `cell_type` annotations
2. msk-spectrum and HTAN datasets have `cell_type` annotations because it was published and made available on CellxGene
3. msk-scope likely does not have human-curated `cell_type` annotations, instead
may likely have computed `cell_type` via `cell_type_L1/L2/L3`

MEANING?
So what does this mean for the frontend? It needs a cell_type so we can create
a heatmap/table for all datasets

For datasets that have a cell_type annotation, expose the cell_type proportions
as-is to the database record upload.
For datasets without a cell_type annotation...it won't have any cell_types to
make available.

For the final table in the frontend, we should add together 
all unique cell_types along the Y-axis

# pseudo-code
1. Iterate over all datasets
For each dataset
    Grab the cell_types + cell_type proportions for this dataset
    Add the current cell_types to an all_cell_types list

"""
import os
import argparse
import anndata as ad
import json
from pathlib import Path
from collections import defaultdict
from typing import List, TypeAlias

from dotenv import load_dotenv
from sqlalchemy import create_engine
from pydantic import BaseModel, TypeAdapter
import pandas as pd


from scripts.utils import get_files

load_dotenv()
        
# Setup sqlalchemy connection
engine: str = create_engine(os.environ.get('SUPABASE_URI'))
print(engine)

class CellProportion(BaseModel):
    file: Path
    cell_types: dict = {}

CellProportionList: TypeAlias = list[CellProportion]
CellProportionListModel = TypeAdapter(CellProportionList)


def sum_cell_types(cell_proportions: List[CellProportion]) -> dict:
    # Compile total
    all_cell_types = defaultdict(int)
    for c in cell_proportions:
        for cell_type, count in c.cell_types.items():
            all_cell_types[cell_type] += count
    return all_cell_types


def process_files(files):
    cell_proportions = []
    for f in files:
        adata = ad.read_h5ad(f, backed=True)
        try:
            cell_types = adata.obs['cell_type'].value_counts().to_dict()
            c = CellProportion(file=f, cell_types=cell_types) 
            print(c)
        except KeyError as e:
            print(f"Dataset: {f}")
            print(f"Caught KeyError: {e}")
            c = CellProportion(file=f)
        finally:
            cell_proportions.append(c)


    # Sum all cell_types
    # Dump cell_type totals
    all_cell_types = sum_cell_types(cell_proportions)
    with open('cell_types.json', 'w') as f:
        print(all_cell_types)
        json.dump(all_cell_types, f)


    # Dump cell_proportions to a json file
    with open("cell_proportions.json", 'wb') as f:
        f.write(CellProportionListModel.dump_json(cell_proportions))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--input", "-i", help="input files")
    parser.add_argument("--transform", "-t", action="store_true", help="input files")
    args = parser.parse_args()

    if args.transform:
        # Skip processing, just read in cell_types.json & cell_proportions.json
        with open('cell_types.json', 'r') as f:
            cell_types = json.load(f)

        with open('cell_proportions.json', 'r') as f:
            cell_proportions: List[CellProportion] = CellProportionListModel.validate_python(json.load(f))
        
        datasets = [dataset.file.stem for dataset in cell_proportions]
        cell_type_dataset_array = defaultdict(list)
        for cell_type, count in cell_types.items():
            # print(f"{cell_type} => {count}")
            for dataset in cell_proportions:
                cell_type_count = dataset.cell_types.get(cell_type, 0)
                cell_type_dataset_array[cell_type].append(cell_type_count)

        for k, v in cell_type_dataset_array.items():
            print(f"{k} => {v}")
            print(len(v))



        # Create a pandas dataframe
        data = cell_type_dataset_array.values()
        df = pd.DataFrame(data, index=cell_type_dataset_array.keys(), columns=datasets)
        print(df)
        print(df.to_sql(name='cell_type_counts', con=engine, if_exists='replace'))


    else:
        files = get_files(args.input, ('*.h5ad',))
        process_files(files)


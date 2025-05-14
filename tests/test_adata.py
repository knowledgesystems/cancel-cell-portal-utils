import os
from pathlib import Path

import pytest

import anndata as ad
from anndata.typing import ArrayDataStructureType

from src.adata import adata, extract_layers


"""
import h5py
store = h5py.File("for-ondisk-docs/cart-164k-processed.h5ad", mode="r")
list(store.keys())
['X', 'layers', 'obs', 'obsm', 'obsp', 'uns', 'var', 'varm', 'varp']

1. A h5ad validation class that represents the h5ad closely, contains raw data
matrices/DF
2. A transformation function where we take the saved errors (validation instance) -> (Web Ready Instance + Extras, +Validation Errors)

.h5ad -> (extract_layers) -> (load_layers_onto_validation_class)
"""

fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures')

@pytest.mark.filterwarnings("ignore")  # Ignore anndata OldFormatWarning
def test_extract_h5ad_layers():
    test_file = "pbmc3k.h5ad"
    fpath = Path(fixture_path) / test_file
    a = ad.read_h5ad(fpath, backed=False)

    assert isinstance(a, ad.AnnData)
    assert isinstance(a.X, ad.typing.ArrayDataStructureType)
    print(a.__dict__.keys())
    # assert a.__dict__.keys() == ['_layers']
    # metadata = extract_layers(ad)


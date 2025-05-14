import os
import datetime
import pathlib
import pytest

import anndata as ad

from scripts.extract_adata_metadata import (
    AnndataMetadata,
    extract_h5ad_metadata,
    get_files
)
from scripts.utils import size_convert, time_convert

fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.fixture
def fake_filesystem(fs):
    fs.create_dir("/data/web")
    fs.create_file("/data/example1.h5ad")
    fs.create_file("/data/example2.json")
    fs.create_file("/data/example3.txt")
    fs.add_real_directory(fixture_path)
    yield fs


@pytest.mark.usefixtures("fake_filesystem")
def test_get_files():
    # Unable to parametrize a pathlib.PosixPath because pathlib is not
    # mocked in pytest.mark.parametrize decorator
    test_path = "/data"
    expected_files = [
        pathlib.PosixPath("/data/example1.h5ad"),
        pathlib.PosixPath("/data/example2.json"),
    ]
    assert get_files(test_path, ('*.h5ad',)) == expected_files[:1]
    assert get_files(test_path, ('*.h5ad', '*.json')) == expected_files


@pytest.mark.skip(reason="NotImplemented Yet")
def test_get_files_with_symlinks():
    raise NotImplementedError


@pytest.mark.skip(reason="NotImplemented Yet")
def test_get_files_s3_interface():
    raise NotImplementedError


@pytest.mark.skip(reason="NotImplemented Yet")
def test_get_files_s3_interface_with_prefix():
    raise NotImplementedError


@pytest.mark.filterwarnings("ignore")  # Ignore anndata OldFormatWarning
@pytest.mark.usefixtures("fake_filesystem")
def test_extract_h5ad_metadata():
    test_file = "pbmc3k.h5ad"
    myfile = pathlib.Path(fixture_path) / test_file
    metadata = extract_h5ad_metadata(myfile)
    assert isinstance(metadata, AnndataMetadata)
    assert metadata.shape == (2638, 1838)
    assert metadata.obsm == ['X_pca', 'X_tsne', 'X_umap', 'X_draw_graph_fr']


@pytest.mark.skip(reason="WIP")
@pytest.mark.filterwarnings("ignore")  # Ignore anndata OldFormatWarning
@pytest.mark.usefixtures("fake_filesystem")
def test_pydantic_metadata_validate():
    test_file = "pbmc3k.h5ad"
    myfile = pathlib.Path(fixture_path) / test_file
    data = ad.read_h5ad(myfile, backed=False)

    fields = {
        "n_obs": data.n_obs,
        "n_vars": data.n_vars,
    }
    AnndataMetadata.model_validate(fields)





# Mark for deprecation, model autoconverts ByteSize
@pytest.mark.parametrize("a,expected", [
    (1073741824, '1.000GiB'),
    (8454592957, '7.874GiB'),
])
def test_size_convert(a, expected):
    assert size_convert(a) == expected


# Mark for deprecation, model autoconverts datetime
def test_time_convert():
    test_input = 1744107595
    expected = datetime.date(2025, 4, 8)
    assert time_convert(test_input) == expected

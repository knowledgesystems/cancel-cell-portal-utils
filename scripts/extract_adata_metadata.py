"""
Given a directory/s3bucket of scrnaseq anndata objects.
Extract relevant metadata to be stored in a json file.

Important scrnaseq anndata slots
* X
* n_obs x n_var
* obs - observation level, cell metadata
* var - variable level
* obsm - observation-level matrices, embedding layer
    - X_umap
    - X_pca
    - X_some_embedding
* varm - variable level matrices
* uns - unstructured metadata
* layers

Cellxgene requirements:
* A unique identifier is required for each cell, which by default will
be pulled from the obs DataFrame index. If the index is not unique or
does not contain the cell ID, an alternative column can be specified
with --obs-names
* A unique identifier is required for each gene, which by default will
be pulled from the var DataFrame index. If the index is not unique or
does not contain the gene ID, an alternative column can be specified
with --var-names
"""
import argparse
import logging
import warnings
from datetime import datetime
from pathlib import Path
from typing import List, TypeAlias

# 3rd party imports
import anndata as ad
from typing import Annotated
from pydantic import (
    BaseModel,
    Field,
    computed_field,
    ByteSize,
    FilePath,
    TypeAdapter,
    ValidationError,
    PositiveInt,
    AfterValidator,
    validator
)
from pydantic_core import ErrorDetails

from scripts.utils import get_files

# Ignore all warnings from anndata
warnings.filterwarnings('ignore', module='anndata')

# Configure logger
levels = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warn': logging.WARNING,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG,
}

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
ConsoleOutputHandler = logging.StreamHandler()
ConsoleOutputHandler.setFormatter(formatter)
logger.addHandler(ConsoleOutputHandler)


# Models
class S3File(BaseModel):
    name:  str
    filepath: Annotated[str, "s3 uri"]
    size: ByteSize
    created: datetime
    modified: datetime
    last_access: datetime


class File(BaseModel):
    name: str = ''
    filepath: FilePath = Path()
    group: str | None = None
    size: int = 0
    created: float = 0
    modified: float = 0
    last_access: float = 0


class AnndataMetadata(BaseModel):
    is_backed: bool = False
    n_obs: Annotated[PositiveInt, '# of cells'] = 0
    n_vars: Annotated[PositiveInt, "WIP"] = 0
    shape: Annotated[tuple, "Data shape of n_obs x n_vars"] = (0, 0)
    obs: Annotated[List[str], "Cell metadata"] = []
    obsm: Annotated[List[str], "List of embeddings"] = []
    var: Annotated[List[str], "Gene metadata"] = []
    uns: List = []
    layers: List[str] = []

    # @validator()
    # def obs_must_not_contain_batman(cls, v: str) -> str:
    #     word = "batman"
    #     if word == v:
    #         raise ValueError(f"{word} is restricted, please remove")
    #     return v


# Marked for removal, or could keep as utility
AnndataMetadataList: TypeAlias = list[AnndataMetadata]
AnndataMetadataListModel = TypeAdapter(AnndataMetadataList)


class CombinedData(BaseModel):
    """
    High-level model containing file metadata, data metadata, and errors
    To be used to construct a json response or database record
    """
    file: File = File()

    # Computed fields from File
    @computed_field
    @property
    def dataset(self) -> str:
        return self.file.name

    @computed_field
    @property
    def group(self) -> str | None:
        return self.file.group


    metadata: Annotated[AnndataMetadata, "Defaults to Empty AnndataMetadata"] = AnndataMetadata()
    errors: Annotated[List[ErrorDetails], "Pydantic List of Errors"] = []
    extras: Annotated[List, "Externally provided metadata"] = []


CombinedDataList: TypeAlias = list[CombinedData]
CombinedDataListModel = TypeAdapter(CombinedDataList)


EXTENSIONS = (
    '*.h5ad',
    # '*.zarr'
)


def extract_file_metadata(f: Path) -> File:
    stats = f.stat()
    file = File(
        filepath=f,
        name=f.name,
        group=f.parent.name,
        size=stats.st_size,
        created=stats.st_ctime,
        modified=stats.st_mtime,
        last_access=stats.st_atime
    )
    logger.debug(file.model_dump_json())
    return file


def extract_h5ad_metadata(f: Path, group: bool = False, backed: bool = False) -> AnndataMetadata:
    """
    Given: a File in a Path like object
    Return: AnndataMetadata instance

    Note:
    If there are validation errors during the instantiation step
    then ValidationError will be raised and the pydantic model
    will not be instantiated.

    """
    # Log, Applying & Validating Against Model
    data = ad.read_h5ad(f, backed=backed)
    # print(data)
    # print(data.obs_keys())
    # print(data.obs['tissue'])
    # print(data.obs['tissue'].unique())
    # print(data.obs['tissue_type'].unique())
    try:
        return AnndataMetadata(
            is_backed=data.isbacked,
            n_obs=data.n_obs,
            n_vars=data.n_vars,
            shape=data.shape,
            obs=data.obs_keys(),
            obsm=data.obsm_keys(),
            var=data.var_keys(),
            uns=data.uns_keys(),
            layers=data.layers.keys()
        )
    except ValidationError as exc:
        raise exc


# Marked for utils


def process_files(files: List[Path]) -> List[CombinedData]:
    """
    1. Extract file metadata
    2. Extract anndata metadata
        If ValidationErrors,
          return empty initialized AnndataMetadata
          and populated list of errors
        If no ValidationErrors,
          return the populated AnndataMetadata
          and empty list of errors
    """
    all_metadata = []
    for f in files:
        logger.info(f"Extracting metadata: {f}")
        combined = CombinedData(file=extract_file_metadata(f))
        try:
            combined.metadata = extract_h5ad_metadata(f, group=args.group, backed=True)
        except ValidationError as exc:
            combined.errors = exc.errors()
        all_metadata.append(combined)
    return all_metadata


def add_invalid_example_model(all_metadata: List[CombinedData]):
    # Create empty model
    empty_model = CombinedData(file=File(name='example_empty.txt'))
    invalid_data = {
        'n_obs': "cats",
        'n_vars': "dogs",
        'obs': ["batman"]
    }
    try:
        empty_anndata = AnndataMetadata(**invalid_data)
        empty_model.metadata = empty_anndata
    except ValidationError as exc:
        # Intentionally add errors to populate this attribute
        empty_model.errors = exc.errors()

    all_metadata.append(empty_model)


def process_extras_metadata_file(f: Path):
    raise NotImplementedError


def main(args):
    # Gather files
    files = get_files(path=args.input, extensions=EXTENSIONS)
    logger.info(f"Collected {len(files)} files")

    # Process Files
    # all_metadata = process_files(files[0:1])
    all_metadata = process_files(files)

    # Example empty/default initialized AnndataMetadata
    if args.add_invalid_data_example:
        add_invalid_example_model(all_metadata)

    # Process extra metadata
    if args.extra_metadata:
        process_extras_metadata_file(Path(args.extra_metadata))
        # Add extra metadata to each model instance

    # Dump metadata collection to a json file
    with open(args.output, 'wb') as fh:
        logger.debug(CombinedDataListModel.dump_json(all_metadata))
        fh.write(CombinedDataListModel.dump_json(all_metadata))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--input", "-i", required=True,
                        help="Location of h5ad files")
    parser.add_argument("--output", "-o", default='output.json')
    parser.add_argument("--extra-metadata", "-em",
                        help="Provide a file containing extra metadata for the dataset. WIP")
    parser.add_argument("--group", "-g", action="store_true",
                        help="Group h5ad files by directory")
    parser.add_argument("--add-invalid-data-example", action="store_true",
                        help="Adds an example containing an error list")
    parser.add_argument("--log-level", "-log",
                        default='info',
                        choices=['debug', 'info', 'warning'],
                        help="Provide the log level")
    args = parser.parse_args()
    logger.setLevel(levels.get(args.log_level, logging.INFO))

    main(args)

    """
    Supabase record to insert
        dataset:
            If metadata is valid or invalid, we should always populate a
            db record with the dataset name that we're looking into.
        data: The metadata extracted from the file
            If valid data, then it will be populated normaly
            If invalid data, then we will provide a dummy zeroed/NA data record
        errors:
            If there are errors, we'll include the errors as a json list
            If no errors, this will be an empty json list
    Notes:
        This should this be 3 separate fields in the supabase datasets table
        We should have a record in the database even if the metadata is invalid
    """

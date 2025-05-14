from anndata import AnnData, read_h5ad
from pydantic import BaseModel


def extract_layers(ad: AnnData):
    """
    Take an anndata object, take all the layers and apply to the adata_class
    """
    
    pass


class adata(BaseModel):
    """
    This is meant to 

    AnnData specification (v0.1.0)
    An AnnData object MUST be a group.

    The group’s metadata MUST include entries: 
    "encoding-type": "anndata", "encoding-version": "0.1.0".

    An AnnData group MUST contain entries "obs" and "var", 
    which MUST be dataframes (though this may only have an index with no columns).

    The group MAY contain an entry X, which MUST be either a 
    dense or sparse array and whose shape MUST be (n_obs, n_var)

    The group MAY contain a mapping layers. 
    Entries in layers MUST be dense or sparse arrays which have 
    shapes (n_obs, n_var)

    The group MAY contain a mapping obsm. 
    Entries in obsm MUST be sparse arrays, dense arrays, or dataframes. 
    These entries MUST have a first dimension of size n_obs

    The group MAY contain a mapping varm. 
    Entries in varm MUST be sparse arrays, dense arrays, or dataframes. 
    These entries MUST have a first dimension of size n_var

    The group MAY contain a mapping obsp. 
    Entries in obsp MUST be sparse or dense arrays. 
    The entries first two dimensions MUST be of size n_obs

    The group MAY contain a mapping varp. 
    Entries in varp MUST be sparse or dense arrays. 
    The entries first two dimensions MUST be of size n_var

    The group MAY contain a mapping uns. 
    Entries in uns MUST be an anndata encoded type.
    """
    # ['X', 'layers', 'obs', 'obsm', 'obsp', 'uns', 'var', 'varm', 'varp']
    X: str

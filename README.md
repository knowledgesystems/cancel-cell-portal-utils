This collection of single cell rnaseq utilites uses `uv` to
manage package dependencies.

Environment Variables

Used for  Supabase Python SDK
`SUPABASE_KEY`
`SUPABASE_URL`

Used for Direct SQLAlchemy connection (for pandas)
`SUPABASE_URI`

Background
Utilities
Data
Relation to Cancer Cell Portal
```sh
# Write initialization steps
uv init
uv install
```

```sh
python extract_adata_metadata.py -i ./data/web
or
uv run extract_adata_metadata.py -i ./data/web
```


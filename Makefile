start-notebook:
	uv run jupyter notebook
test:
	uv run pytest -s -vvv -f -n 2 --color=yes --code-highlight=yes

extractMetadata:
	# Produces #output.json
	uv run scripts/extract_adata_metadata.py -i ./data/web 
uploadMetadata:
	uv run python scripts/import_metadata_to_supabase.py -i output.json

calculateCellTypeProportions:
	# Produces cell_types.json & cell_proportions.json
	uv run scripts/celltype_proportions.py -i ./data/web -g groups.txt
uploadCellTypeProportions:
	# Reads in cell_types.json & cell_proportions.json
	uv run scripts/celltype_proportions.py -t


from pydantic import BaseModel, ValidationError
from scripts.extract_adata_metadata import AnndataMetadata, File


class MyModel(BaseModel):
    x: int
    # y: str


"""
If there are pydantic validation errors during the instantiation step,
then the pydantic model will not be returned. Even for the correct fields.


1. Grab the file name
2. Response data record to sql db insert will be...
    Filename/DatasetName + DatasetMetadata json
    OR
    Filename/DatasetName + ValidationErrors Encountered

Outputs:
    1. A json file containing ALL models dumped
    2. A file with each line containing the CORRECT models + INCORRECT models
        - with validation errors populated

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

try:
    m = MyModel.model_validate({'x': 'testsring'})
    # m = MyModel.model_validate({'x': '1'})
    print(m.model_dump_json())
    
except ValidationError as exc:
    print(exc.json())
    # print(repr(e.errors()[0]['type']))


file_data = {
    "name": "example_file.txt",
    "filepath": "/path/to/my/example_file.txt",
}

# Using model_validate method
# print("Using model_validate")
#try:
#    myfile = File.model_validate(file_data)
#    # print(myfile)
#except ValidationError as exc:
#    print(str(exc))
    # print(exc.errors())
    # print(exc.json())

# Using direct assignment
# print()
# print("Using direct assignment")
# try:
#     myfile = File(**file_data)
#     print(myfile)
#     print(myfile.model_dump_json())
# except ValidationError as exc:
#     # print(exc.errors())
#     pass


    # print(repr(e.errors()[0]['type']))

data = {
    "n_obs": 1234,
    "n_var": 9999,
    "layers": []
}

# try:
#     record = AnndataMetadata.model_validate(data)
#     print(record)
# except ValidationError as e:
#     print(e)
#     


# AnndataMetadata(file=, n_obs="123")

invalid_data = {
    "n_obs": 1234,
    "n_var": 9999
}

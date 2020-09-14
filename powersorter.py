import json

# load config file
with open('test.json') as f:
    config = json.load(f)

collection = config.get('collection', None)
print(collection)
files = config.get('files', None)
print(files)
file_types = config.get('file_types', None)
for file_type, value in file_types.items():
    regex = value.get('regex', None)
    destination_path = value.get('destination_path', None)
    print(regex)
    print(destination_path)

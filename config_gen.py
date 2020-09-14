import json

# boilerplate
config = {}
collection = config['collection']={}
collection['name'] = 'BRIT'
collection['prefix'] = 'BRIT'
files = config['files']={}
files['folder_increment'] = 1000
files['number_pad'] = 7
files['base_output_path'] = '/test/out/'
files['input_path'] = '/test/in/'

# file_types
file_types = config['file_types'] = {}
# TODO create a pattern class to generate each patterns
# TODO use regex to test compile the pattern, maybe to test?
web_jpg = file_types['web_jpg'] = {}
web_jpg['regex'] = '(?<prefix>BRIT)(?<numerical>\d+)(\.)(?i)(?<ext>jpg|jpeg)'
web_jpg['destination_path'] = 'web/'

web_derivs = file_types['web_derivs'] = {}
web_derivs['regex'] = '(?<prefix>BRIT)(?<numerical>\d+)(?<delimiter>_)(?<size>med|thumb)(\.)(?<ext>.+)'
web_derivs['destination_path'] = 'web/'

archive_dng = file_types['archive_dng'] = {}
archive_dng['regex'] = '(?<prefix>BRIT)(?<numerical>\d+)(\.)(?i)(?<ext>DNG)'
archive_dng['destination_path'] = 'archive/'

#print(config)
print(json.dumps(config))
"""
for pattern in config['patterns']:
    print(pattern, config['patterns'][pattern])

"""
"""
Sample file strings
BRIT1000.jpg
BRIT1000_med.jpg
BRIT1000_thumb.jpg
BRIT1000.DNG
BRIT1000_ocr.txt
BRIT1000_ocr.json
"""

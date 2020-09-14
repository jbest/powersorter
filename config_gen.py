import json

# boilerplate
config = {}
collection = config['collection'] = {}
collection['name'] = 'BRIT'
collection['prefix'] = 'BRIT'
files = config['files'] = {}
files['folder_increment'] = 1000
files['number_pad'] = 7
files['output_base_path'] = '/test/out/'
files['input_path'] = '/test/in/'

# file_types
file_types = config['file_types'] = {}
# TODO create a pattern class to generate each patterns
# TODO use regex to test compile the pattern, maybe to test?
web_jpg = file_types['web_jpg'] = {}
web_jpg['regex'] = '(?P<prefix>BRIT)(?P<numerical>\d+)(\.)(?i)(?P<ext>jpg|jpeg)'
web_jpg['output_sub_path'] = 'web/'

web_derivs = file_types['web_derivs'] = {}
web_derivs['regex'] = '(?P<prefix>BRIT)(?P<numerical>\d+)(?P<delimiter>_)(?P<size>med|thumb)(\.)(?P<ext>.+)'
web_derivs['output_sub_path'] = 'web/'

archive_dng = file_types['archive_dng'] = {}
archive_dng['regex'] = '(?P<prefix>BRIT)(?P<numerical>\d+)(\.)(?i)(?P<ext>DNG)'
archive_dng['output_sub_path'] = 'archive/'

ocr = file_types['ocr'] = {}
ocr['regex'] = '(?P<prefix>BRIT)(?P<numerical>\d+)(?P<delimiter>_)(?P<ocr>ocr)(\.)(?P<ext>.+)'
ocr['output_sub_path'] = 'web/'

print(json.dumps(config))

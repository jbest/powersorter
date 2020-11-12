import json

# boilerplate
config = {}
collection = config['collection'] = {}
collection['name'] = 'TEST'
collection['prefix'] = 'TEST'
files = config['files'] = {}
files['folder_increment'] = 1000
files['number_pad'] = 7
files['log_directory_path'] = '/corral-repl/projects/TORCH/archive/TEST/logs/'
files['output_base_path'] = '/corral-repl/projects/TORCH/'
files['input_path'] = '/corral-repl/projects/TORCH/TEST/'

# file_types
file_types = config['file_types'] = {}
# TODO create a pattern class to generate each pattern
# TODO use regex to test compile the pattern, maybe to test?
# NB - file_types key names are used by urlgen.py to determine which files have a URL generated.
web_jpg = file_types['web_jpg'] = {}
web_jpg['regex'] = r'(?P<prefix>BRIT)(?P<numerical>\d+)(\.)(?i)(?P<ext>jpg|jpeg)'
web_jpg['output_sub_path'] = 'web/TEST/'

# TORCH config version 1.0
"""
web_derivs = file_types['web_derivs'] = {}
web_derivs['regex'] = r'(?P<prefix>BRIT)(?P<numerical>\d+)(?P<delimiter>_)(?P<size>med|thumb)(\.)(?P<ext>.+)'
web_derivs['output_sub_path'] = 'test/web/BRIT/'
"""
# TORCH config version 2.0
web_jpg_med = file_types['web_jpg_med'] = {}
web_jpg_med['regex'] = r'(?P<catalog_number>(?P<prefix>BRIT)(?P<numerical>\d+))(?P<delimiter>_)(?P<size>med)(\.)(?P<ext>.+)'
web_jpg_med['output_sub_path'] = 'web/TEST/'

web_jpg_thumb = file_types['web_jpg_thumb'] = {}
web_jpg_thumb['regex'] = r'(?P<catalog_number>(?P<prefix>BRIT)(?P<numerical>\d+))(?P<delimiter>_)(?P<size>thumb)(\.)(?P<ext>.+)'
web_jpg_thumb['output_sub_path'] = 'web/TEST/'

archive_dng = file_types['archive_dng'] = {}
archive_dng['regex'] = r'(?P<prefix>BRIT)(?P<numerical>\d+)(\.)(?i)(?P<ext>DNG)'
archive_dng['output_sub_path'] = 'archive/TEST/'

ocr = file_types['ocr'] = {}
ocr['regex'] = r'(?P<prefix>BRIT)(?P<numerical>\d+)(?P<delimiter>_)(?P<ocr>ocr)(\.)(?P<ext>.+)'
ocr['output_sub_path'] = 'web/TEST/'

print(json.dumps(config, indent=4))

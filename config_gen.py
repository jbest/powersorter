import json

# boilerplate
config = {}
collection = config['collection'] = {}
collection['name'] = 'BRIT'
collection['prefix'] = 'BRIT'
files = config['files'] = {}
files['folder_increment'] = 1000
files['number_pad'] = 7
files['log_directory_path'] = '/Users/jbest/Documents/brit-svn/git/powersorter/'
files['output_base_path'] = '/Users/jbest/Documents/brit-svn/git/powersorter/'
files['input_path'] = '/Users/jbest/Documents/brit-svn/git/powersorter/input_dir/'

# file_types
file_types = config['file_types'] = {}
# TODO create a pattern class to generate each pattern
# TODO use regex to test compile the pattern, maybe to test?
# NB - file_types key names are used by urlgen.py to determine which files have a URL generated.
web_jpg = file_types['web_jpg'] = {}
web_jpg['regex'] = r'(?P<prefix>BRIT)(?P<numerical>\d+)(\.)(?i)(?P<ext>jpg|jpeg)'
web_jpg['output_sub_path'] = 'web/'

web_derivs = file_types['web_derivs'] = {}
web_derivs['regex'] = r'(?P<prefix>BRIT)(?P<numerical>\d+)(?P<delimiter>_)(?P<size>med|thumb)(\.)(?P<ext>.+)'
web_derivs['output_sub_path'] = 'web/'

archive_dng = file_types['archive_dng'] = {}
archive_dng['regex'] = r'(?P<prefix>BRIT)(?P<numerical>\d+)(\.)(?i)(?P<ext>DNG)'
archive_dng['output_sub_path'] = 'archive/'

ocr = file_types['ocr'] = {}
ocr['regex'] = r'(?P<prefix>BRIT)(?P<numerical>\d+)(?P<delimiter>_)(?P<ocr>ocr)(\.)(?P<ext>.+)'
ocr['output_sub_path'] = 'web/'

print(json.dumps(config, indent=4))

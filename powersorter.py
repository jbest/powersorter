import json
import re
import os


def scan_files(path=None, pattern=None):
    """
    Scan the directory for files matching the provided pattern.
    Extract relevant parts from file for organization and sorting
    Return a list of matching files
    """
    #print(path)
    # TODO use Path Lib to split path and file name

    # Test file names
    #test_files = ['BRIT1000.jpg', 'BRIT1000.JPG', 'BRIT1000.JPEG', 'BRIT1000_med.jpg', 'BRIT1000_thumb.jpg', 'BRIT1000.DNG', 'BRIT1000.cr2', 'BRIT1000.nef', 'BRIT1000_ocr.txt', 'BRIT1000_ocr.json' ]
    #print('test_files:', test_files)

    matches = []
    print(pattern)
    file_pattern = re.compile(pattern)
    for root, dirs, files in os.walk(path):
        for file in files:
            #print(os.path.join(root, file))
            m = file_pattern.match(file)
            if m:
                print('file:', file)
                print(m.groups())
                file_dict = m.groupdict()
                print('prefix:', file_dict.get('prefix'))
                print('numerical:', file_dict.get('numerical'))
                print('delimiter:', file_dict.get('delimiter'))
                print('size:', file_dict.get('size'))
                print('ext:', file_dict.get('ext'))
                file_path = os.path.join(root, file)
                file_dict['file_path'] = file_path
                matches.append(file_dict)
    return matches

#def sort_files(path_matches=None, output_path=None):


# load config file
with open('test.json') as f:
    config = json.load(f)

collection = config.get('collection', None)
print(collection)
files = config.get('files', None)
input_path = files['input_path']
print('input_path:', input_path)
# TODO confirm input_path exists and is readable

file_types = config.get('file_types', None)
for file_type, value in file_types.items():
    regex = value.get('regex', None)
    destination_path = value.get('destination_path', None)
    # test input_path
    input_path = './input_dir/'
    file_matches = scan_files(path=input_path, pattern=regex)
    print(file_matches)

    # TODO confirm destination_path exists and is writable


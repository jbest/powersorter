import json
import re
import os
from pathlib import Path
import shutil


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
    print('pattern:', pattern)
    file_pattern = re.compile(pattern)
    for root, dirs, files in os.walk(path):
        for file in files:
            #print(os.path.join(root, file))
            m = file_pattern.match(file)
            if m:
                file_dict = m.groupdict()
                """
                print('prefix:', file_dict.get('prefix'))
                print('numerical:', file_dict.get('numerical'))
                print('delimiter:', file_dict.get('delimiter'))
                print('size:', file_dict.get('size'))
                print('ext:', file_dict.get('ext'))
                """
                file_path = os.path.join(root, file)
                file_dict['file_path'] = file_path
                matches.append(file_dict)
    return matches

def sort_files(files=None, output_path=None):
    for file in files:
        file_path = file['file_path']
        print(f'File {file_path} will be sorted to {output_path}')
        accession_number = int(file['numerical'])
        # Determine what folder number the files should be moved to
        folder_number = int(accession_number//folder_increment*folder_increment)
        padded_folder_number = str(folder_number).zfill(number_pad)
        destination_folder_name = collection_prefix + padded_folder_number
        destination_path = Path(output_path).joinpath(destination_folder_name)
        print(destination_path)


# load config file
with open('test.json') as f:
    config = json.load(f)

collection = config.get('collection', None)
collection_prefix = collection.get('prefix', None)
print('collection_prefix:', collection_prefix)
files = config.get('files', None)
folder_increment = int(files.get('folder_increment', 1000))
number_pad = int(files.get('number_pad', 7))
output_base_path = Path(files.get('output_base_path', None))
input_path = Path(files.get('input_path', None))
print('input_path:', input_path)
# TODO confirm input_path exists and is readable

# Check existence of input path
if input_path:
    # test to ensure input directory exists
    if input_path.is_dir():
        print('input_path:', input_path)
    else:
        print(f'ERROR: directory {input_path} does not exist.')
        print('Terminating script.')
        quit()

file_types = config.get('file_types', None)

# TODO check ALL output directories before scanning for files
"""
# Check ability to write to X directory
if not os.access(output_path, os.W_OK | os.X_OK):
    print(f'Unable to write to directory: {output_path}')
    quit()
"""

# scan, sort, and move each file type
for file_type, value in file_types.items():
    regex = value.get('regex', None)
    output_sub_path = value.get('output_sub_path', None)
    # TODO confirm destination_path exists and is writable
    print('output_sub_path:', output_sub_path)
    output_path = output_base_path.joinpath(output_sub_path)
    # Check ability to write to X directory
    if not os.access(output_path, os.W_OK | os.X_OK):
        print(f'Unable to write to directory: {output_path}')
    else:
        file_matches = scan_files(path=input_path, pattern=regex)
        sort_files(files=file_matches, output_path=output_path)

    


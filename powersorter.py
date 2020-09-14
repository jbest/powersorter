import json
import re


def scan_files(path=None, pattern=None):
    """
    Scan the directory for files matching the provided pattern.
    """
    #print(path)

    # Test file names
    test_files = ['BRIT1000.jpg', 'BRIT1000.JPG', 'BRIT1000.JPEG', 'BRIT1000_med.jpg', 'BRIT1000_thumb.jpg', 'BRIT1000.DNG', 'BRIT1000.cr2', 'BRIT1000.nef', 'BRIT1000_ocr.txt', 'BRIT1000_ocr.json' ]
    print(pattern)
    #print('test_files:', test_files)
    file_pattern = re.compile(pattern)
    for file in test_files:
        m = file_pattern.match(file)
        if m:
            print('file:', file)
            print(m.groups())
            print('prefix:', m.group('prefix'))
            print(m.group('numerical'))
            #print(m.group('delimiter'))
            #print(m.group('size'))
            print(m.group('ext'))

    """
    match_list = []
    for key, extension in extensions:
        ext_pattern = '*.' + extension
        # Scan for files
        print('Scanning directory:', source_directory_path, 'for files matching', ext_pattern)
        if recurse_subdirectories:
            # Using rglob
            path_matches = source_directory_path.rglob(ext_pattern)
        else:
            # Using glob
            path_matches = source_directory_path.glob(ext_pattern)
        match_list.append(path_matches)

    all_matches = itertools.chain(*match_list)
    return all_matches
    """


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
    scan_files(path=input_path, pattern=regex)
    # test pattern
    #scan_files(path=input_path, pattern='(?P<prefix>BRIT)(\d+)(\.)(JPG|jpeg)')
    # TODO confirm destination_path exists and is writable


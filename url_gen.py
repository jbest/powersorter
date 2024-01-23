
"""
urlgen (v3) takes an output log of powersorter.py (v3) and extracts all the web image paths
and converts the paths into a web URL and an export file appropriate for 
import into Symbiota using the URL Mapping profile.

This v3 script has been adapted to work with the output from other v3 scripts.
urlgen v3 now requires a config file (which provides the file base path, url base path and collection prefix)

"""

import csv
import argparse
import re
import os.path
from urllib.parse import urljoin
from pathlib import Path
import json

#FILE_BASE_PATH = '/corral-repl/projects/TORCH/web/'
#URL_BASE = 'https://web.corral.tacc.utexas.edu/torch/'
DEFAULT_THUMB_EXT = '_thumb'
DEFAULT_MEDIUM_EXT = '_med'

# set up argument parser
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True, \
    help="Path to the input log file generated by powersort.py.")
ap.add_argument("-c", "--config", required=True, \
    help="Configuration file path with required parameters.")
ap.add_argument("-m", "--med_tag", required=False, \
    help="Tag used to indicate a medium image (e.g. _med)")
ap.add_argument("-t", "--thumb_tag", required=False, \
    help="Tag used to indicate a thumbnail image (e.g. _thumb)")
ap.add_argument("-v", "--verbose", action="store_true", \
    help="Detailed output.")
args = vars(ap.parse_args())

input_file = args['input']
config_file = args['config']
verbose = args['verbose']
#file_prefix = args["prefix"]
# v3, v2, and v1 file types
# once regex is exclusivly used, these file type will not be needed
web_file_types = ['web', 'web_derivs', 'web_jpg_med', 'web_jpg_thumb', 'web_jpg'] # file types that will have url generated
if args["thumb_tag"]:
    thumb_ext = args["thumb_tag"]
else:
    thumb_ext = DEFAULT_THUMB_EXT

if args["med_tag"]:
    medium_ext = args["med_tag"]
else:
    medium_ext = DEFAULT_MEDIUM_EXT

class Settings():
    def __init__(self, verbose=False):
        #self.prefix = prefix
        #self.dry_run = dry_run
        self.verbose = verbose
        #self.force_overwrite = force_overwrite

    def load_config(self, config_file=None):
        # load config file
        if config_file:
            with open(config_file) as f:
                config = json.load(f)
                #print(config)
                self.versions = config.get('versions', None)
                self.config_format = self.versions.get('config_format')
                self.collection = config.get('collection', None)
                self.collection_prefix = self.collection.get('prefix', None)
                self.catalog_number_regex = self.collection.get('catalog_number_regex', None)
                self.web_base = self.collection.get('web_base', None) # path of directory available via HTTP/S
                self.url_base = self.collection.get('url_base', None) # URL of directory served via HTTP/S
                self.file_types = config.get('file_types', None)
                self.web_jpg_regex = self.file_types.get('web_jpg', None).get('file_regex', None)
                self.web_jpg_med_regex = self.file_types.get('web_jpg_med', None).get('file_regex', None)
                self.web_jpg_thumb_regex = self.file_types.get('web_jpg_thumb', None).get('file_regex', None)
                #self.catalog_number_regex = self.collection.get('catalog_number_regex', None)
                #self.files = config.get('files', None)
                #self.folder_increment = int(self.files.get('folder_increment', 1000))
                #self.log_directory_path = Path(self.files.get('log_directory_path', None))
                #self.number_pad = int(self.files.get('number_pad', 7))
                #self.output_base_path = Path(self.files.get('output_base_path', None))
                # Get the type of files and patterns that will be scanned and sorted
                #self.file_types = config.get('file_types', None)

def generate_url(file_base_path=None, file_path=None, url_base=None):
    """
    Generate a URL using the file paths and URL base path.
    """
    #print(file_base_path, file_path, url_base)
    common_path = os.path.commonpath([file_base_path, file_path])
    #web_base_path = os.path.realpath(file_base_path)
    web_base_parent_path, common_dirname = os.path.split(common_path)
    #relative_path = os.path.relpath(file_path, start=common_path)
    relative_path = os.path.relpath(file_path, start=web_base_parent_path)
    image_url = urljoin(url_base, relative_path)
    """
    print('file_path', file_path)
    print('common_path', common_path)
    print('common_dirname', common_dirname)
    print('web_base_path', web_base_path)
    print('relative_path', relative_path)
    print('image_url',image_url)
    """
    return image_url

def generate_url_records(file_base_path=None, url_base=None):
    """
    This method does not account for suffixes. They will overwrite or be 
    overwritten when a file without a suffix is in the record.
    This method does not use regex to determine the filetype, instead
    relies on the powersort input field 'filetype'.
    """
    occurrence_set = {}
    with open(input_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            file_path = row['destination']
            file_type = row['filetype']
            result_status = row['result']
            # check if file successfully moved
            if result_status == 'success':
                if file_type in web_file_types:
                    # get filename parts
                    file_path_obj = Path(file_path)
                    basename = file_path_obj.name
                    file_name = file_path_obj.stem
                    file_extension = file_path_obj.suffix
                    try:
                        catalog_number = catalog_number_pattern.match(file_name).group(0)
                        # Create catalog number record if it doesn't exist
                        if catalog_number not in occurrence_set:
                            occurrence_set[catalog_number]={'catalog_number': catalog_number}
                        # Determine if thumbnail, original, or web size
                        if file_name.endswith(thumb_ext):
                            occurrence_set[catalog_number]['thumbnail'] = generate_url(file_path=file_path, file_base_path=file_base_path, url_base=url_base)
                        elif file_name.endswith(medium_ext):
                            occurrence_set[catalog_number]['web'] = generate_url(file_path=file_path, file_base_path=file_base_path, url_base=url_base)
                        else:
                            occurrence_set[catalog_number]['large'] = generate_url(file_path=file_path, file_base_path=file_base_path, url_base=url_base)
                    except AttributeError:
                        print(f'No match for file_name {file_name} with prefix {file_prefix}')
    return occurrence_set

def match_pattern(text=None, settings=None):
    web_jpg_pattern = re.compile(settings.catalog_number_regex + settings.web_jpg_regex)
    web_jpg_med_pattern = re.compile(settings.catalog_number_regex + settings.web_jpg_med_regex)
    web_jpg_thumb_pattern = re.compile(settings.catalog_number_regex + settings.web_jpg_thumb_regex)

    # test image patterns
    match = None
    match_dict = None
    full = web_jpg_pattern.match(text)
    medium = web_jpg_med_pattern.match(text)
    thumb = web_jpg_thumb_pattern.match(text)

    if full:
        match = full
    elif medium:
        match = medium
    elif thumb:
        match = thumb
    if match:
        match_dict = match.groupdict()
    return match_dict


def generate_url_records_suffixes(settings=None):
    """
    This method accounts for suffixes. They will be grouped into a 
    distinct record set with the catalog number.
    This method uses regex to determine the filetype, and 
    ignores the powersort input field 'filetype'.

    """
    occurrence_set = {}
    with open(input_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            file_path = row['destination']
            file_type = row['filetype']
            result_status = row['result']
            # check if file successfully moved
            if result_status == 'success':
                # get filename parts
                file_path_obj = Path(file_path)
                basename = file_path_obj.name
                file_name = file_path_obj.stem
                file_extension = file_path_obj.suffix

                # Determine if thumbnail, original, or web size
                result = match_pattern(text=basename, settings=settings)

                if result:
                    #print(result)
                    catalog_number = result['catNum']
                    suffix = result.get('suffix', None)
                    size = result.get('size', 'large')
                    if suffix:
                        image_set = catalog_number + '_' + suffix
                    else:
                        image_set = catalog_number
                    # Create image_set record if it doesn't exist
                    if image_set not in occurrence_set:
                        occurrence_set[image_set]={'catalog_number': catalog_number}
                        #print(catalog_number)
                    if size == 'thumb':
                        occurrence_set[image_set]['thumbnail'] = generate_url(url_base=settings.url_base, file_base_path=settings.web_base, file_path=file_path)
                    if size == 'med':
                        occurrence_set[image_set]['web'] = generate_url(url_base=settings.url_base, file_base_path=settings.web_base, file_path=file_path)
                    if size == 'large':
                        occurrence_set[image_set]['large'] = generate_url(url_base=settings.url_base, file_base_path=settings.web_base, file_path=file_path)
                else:
                    if settings.verbose:
                        print('No match:', basename)

    return occurrence_set

if __name__ == '__main__':
    global settings
    settings = Settings(verbose=verbose)
    #Load settings from config
    settings.load_config(config_file=config_file)
    file_prefix = settings.collection_prefix
    #file_base_path = settings.web_base
    url_base = settings.url_base
    web_base = settings.web_base

    pattern_string = settings.catalog_number_regex
    catalog_number_pattern = re.compile(pattern_string)
    if settings.verbose:
        print('settings:')
        #print('file_base_path', file_base_path)
        print('url_base', url_base)
        print('pattern_string', pattern_string)
        print('catalog_number_pattern', catalog_number_pattern)
        print('web_base', web_base)

    #occurrence_set = generate_url_records(file_base_path=file_base_path, url_base=url_base)
    occurrence_set = generate_url_records_suffixes(settings=settings)
    #print(occurrence_set)
    # Get input file name
    input_file_name_stem = Path(input_file).stem
    output_file_name = input_file_name_stem + '_urls.csv'
    print('Writing urls to:', output_file_name)

    with open(output_file_name, 'w', newline='') as csvfile:
        fieldnames=['catalog_number', 'large', 'web', 'thumbnail']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for key, image_set in occurrence_set.items():
            writer.writerow(image_set)


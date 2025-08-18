import csv
import argparse
import datetime
import sys
import os
from pathlib import Path
from PIL import Image
import pwd

import powersorter as ps
import url_gen
#import image_resizer as derivs

CONFIG_FORMAT_REQUIRED = '3.0'

# Image Configuration
MEDIUM_SIZE = (800, 600)  # Medium image dimensions
THUMBNAIL_SIZE = (150, 150)  # Thumbnail dimensions
QUALITY = 85  # JPEG quality (1-100)

def arg_setup():
    # set up argument parser
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--config", required=True, \
        help="Path to the configuration file to be used for processing images.")
    ap.add_argument("-i", "--input_path", required=False, \
        help="Input directory path - overrides input_path in config file")
    ap.add_argument("-s", "--sort_only", action="store_true", \
        help="Sort only, skip derivative creation.")
    ap.add_argument("-v", "--verbose", action="store_true", \
        help="Detailed output.")
    ap.add_argument("-d", "--debug", action="store_true", \
        help="Detailed debug output, very verbose.")
    ap.add_argument("-n", "--dry_run", action="store_true", \
        help="Simulate the sort process without moving files or creating directories.")
    ap.add_argument("-f", "--force", action="store_true", \
        help="Force overwrite of existing files.")
    args = vars(ap.parse_args())
    return args

# gather args and settings
def initialize_settings():
    args = arg_setup()
    #print(args)
    config_file = args['config']
    dry_run = args['dry_run']
    verbose = args['verbose']
    debug = args['debug']
    force_overwrite = args['force']
    input_path_override = args['input_path']
    #generate_derivatives = args['derivatives'] # not in settings class, not needed by powersorter

    # use input_path arg to override input_path in config file
    if input_path_override:
        input_path = Path(input_path_override)
    else:
        input_path = None

    #Confirm force overwrite
    force_overwrite_confirmed = False
    if force_overwrite:
        print('Files with identical names will be overwritten if you proceed.')
        response = input('Type \'overwrite\' and [RETURN/ENTER] to confirm desire to overwrite files: ')
        if response == 'overwrite':
            print('Will overwrite duplicate file names...')
            force_overwrite_confirmed = True
        else:
            print('Overwrite not confirmed. Exiting...')
            force_overwrite_confirmed = False
            sys.exit()

    #TODO implement input_path override
    settings = ps.Settings(dry_run=dry_run, verbose=verbose, force_overwrite=force_overwrite_confirmed, debug=debug)
    #Load settings from config
    settings.load_config(config_file=config_file)

    # Check required config_file version
    if not str(settings.config_format) == CONFIG_FORMAT_REQUIRED:
        print('Wrong config format version:', settings.config_format, 'Required:', CONFIG_FORMAT_REQUIRED)
        sys.exit()
    return(settings, args)

def resize_image(input_path, output_path, size, maintain_aspect=True, force_overwrite=False):
    """
    Resize an image to the specified size and save to path.
    
    Args:
        input_path: Path to the input image
        output_path: Path where resized image will be saved
        size: Tuple of (width, height) for the new size
        maintain_aspect: Whether to maintain aspect ratio
    """

    if not force_overwrite:
        # Check if output file already exists
        if os.path.exists(output_path): # and not force_overwrite:
            
            #print(f'\rProcessing item {i+1}/10', end='', flush=True)
            print(f"\rSkipping {output_path} - file already exists (use -force parameter to overwrite)", end='', flush=True)
            return False

    try:
        with Image.open(input_path) as img:
            if maintain_aspect:
                # Use thumbnail method to maintain aspect ratio
                img.thumbnail(size, Image.Resampling.LANCZOS)
            else:
                # Resize to exact dimensions (may distort image)
                img = img.resize(size, Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary (handles RGBA, P mode images)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Save the resized image
            img.save(output_path, 'JPEG', quality=QUALITY, optimize=True)
            return True
            
    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}")
        return False

if __name__ == '__main__':
    # initialize settings from args and config file
    settings, args = initialize_settings()
    """
    Most args are incorporated into the Settings class for powersorter
    derivatives are not relevant to powersorter so args are retured
    to get the sort_only param
    """
    #generate_derivatives = args['derivatives']
    sort_only = args['sort_only']


    #show settings for debug
    if settings.debug:
        attrs = vars(settings)
        print('Settings:')
        print('\n'.join("%s: %s" % item for item in attrs.items()))

    # generate derivs
    #TODO pass values for resize based on config params
    if sort_only:
        print('Derivatives will not be generated, only sorting files (-s parameter)')
    else:
        print('Generating derivative JPG files...')
        med_count = 0
        thumb_count = 0
        for file_type, value in settings.file_types.items():
            # only process web_jpg for derivative generation (skip med and thumb that already exist)
            if file_type=='web_jpg':
                # get the file regex for this particular file type
                file_regex = value.get('file_regex', None)
                # Adding regex i flag here to make case-insensitive rather than in config files
                regex = '(?i)' + settings.catalog_number_regex + file_regex
                #testing
                if settings.debug:
                    print('DEBUG')
                    print('file regex:', file_regex)
                    print('full regex:', regex)
                output_sub_path = value.get('output_sub_path', None)
                output_path = settings.output_base_path.joinpath(output_sub_path)
                # Check ability to write to directory
                if not os.access(output_path, os.W_OK | os.X_OK):
                    #TODO log fail
                    print(f'Unable to write to directory: {output_path}')
                else:
                    file_matches = ps.scan_files(path=settings.input_path, pattern=regex, file_type=file_type)
                    #testing
                    #print('file_matches:',file_matches)

                    for match in file_matches:
                        #if match.file_path:
                        jpg_file = Path(match['file_path'])
                        # testing
                        #print('Matched pattern:', match['file_path'])
                        base_name = jpg_file.stem
            
                        # Create output paths in the same directory
                        medium_path = jpg_file.parent / f"{base_name}_med.jpg"
                        thumbnail_path = jpg_file.parent / f"{base_name}_thumb.jpg"
                        
                        # Create medium version
                        if settings.verbose:
                            print(medium_path)
                        med_result = resize_image(jpg_file, medium_path, MEDIUM_SIZE, force_overwrite=settings.force_overwrite)
                        if med_result:
                            med_count +=1
                        
                        # Create thumbnail version
                        if settings.verbose:
                            print(thumbnail_path)
                        thumb_result = resize_image(jpg_file, thumbnail_path, THUMBNAIL_SIZE, force_overwrite=settings.force_overwrite)
                        if thumb_result:
                            thumb_count += 1
        
        #TODO print the count of files skipped/existing
        print() #newline after verbose results
        print(f'Generated {med_count} medium derivatives, {thumb_count} thumbnail derivatives.')


    #staging
    #TODO in powersorter.py - convert permissions/dir existance checks etc in main to functions that can be called here
    
    # sort
    now = datetime.datetime.now()
    log_filename = '_'.join([settings.collection_prefix, Path(settings.input_path).stem, str(now.strftime('%Y-%m-%dT%H%M%S'))])
    if settings.dry_run:
        log_filename = log_filename + '_DRY-RUN'
    log_filename = log_filename + '.csv'
    log_file_path = settings.log_directory_path.joinpath(log_filename)

    # intiate sort logger
    sort_logger=ps.SortLogger(filename=log_file_path)

    # get current username
    try:
        username = pwd.getpwuid(os.getuid()).pw_name
    except:
        print('ERROR - Unable to retrive username.')
        username = 'unknown'

    # start sorting
    sort_results = ps.sort(input_path=settings.input_path, \
        number_pad=settings.number_pad, \
        folder_increment=settings.folder_increment, \
        catalog_number_regex=settings.catalog_number_regex,\
        collection_prefix=settings.collection_prefix, \
        file_types=settings.file_types, \
        destination_base_path=settings.output_base_path,
        sort_logger=sort_logger,
        username=username,
        dry_run=settings.dry_run)

    print('sort_results:', sort_results)

    # generate urls
    print('Generating media URLs from log file:', sort_logger.filename)
    # Create output file name
    input_file_name_stem = Path(sort_logger.filename).stem
    output_file_name = input_file_name_stem + '_urls.csv'
    url_gen.write_url_file(input_file=sort_logger.filename, output_file_name=output_file_name, settings=settings)
    #TODO write copy of URLs to web-accessible path
    print('URLS written to:', output_file_name)
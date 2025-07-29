import csv
import argparse
import datetime
import sys
import os

import powersorter as ps
import image_resizer as derivs

CONFIG_FORMAT_REQUIRED = '3.0'

def arg_setup():
    # set up argument parser
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--config", required=True, \
        help="Path to the configuration file to be used for processing images.")
    ap.add_argument("-i", "--input_path", required=False, \
        help="Input directory path - overrides input_path in config file")
    ap.add_argument("-v", "--verbose", action="store_true", \
        help="Detailed output.")
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
    force_overwrite = args['force']
    input_path_override = args['input_path']

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

    settings = ps.Settings(dry_run=dry_run, verbose=verbose, force_overwrite=force_overwrite_confirmed)
    #Load settings from config
    settings.load_config(config_file=config_file)

    # Check required config_file version
    if not str(settings.config_format) == CONFIG_FORMAT_REQUIRED:
        print('Wrong config format version:', settings.config_format, 'Required:', CONFIG_FORMAT_REQUIRED)
        sys.exit()
    return(settings)



if __name__ == '__main__':
    # initialize settings from args and config file
    settings = initialize_settings()

    #show settings for testing
    attrs = vars(settings)
    print('Settings:')
    print('\n'.join("%s: %s" % item for item in attrs.items()))

    # generate derivs
    #TODO add arg to generate derivs
    # use input path
    print('Will generate derivs for files at:')
    print(settings.input_path)
    # process input_path
    #TODO provide extensions to process (currently hard coded in image_resizer.py)
    #TODO pass values for rezie based on cofig params
    #TODO make image_resizer silent/not verbose
    #TODO make image_resizer process files that match regex, not whole directory

    for file_type, value in settings.file_types.items():
        #print('file_type', file_type, 'value', value)
        #regex = value.get('regex', None)
        file_regex = value.get('file_regex', None)
        # Adding regex i flag here to make case-insensitive rather than in config files
        regex = '(?i)' + settings.catalog_number_regex + file_regex
        output_sub_path = value.get('output_sub_path', None)
        output_path = settings.output_base_path.joinpath(output_sub_path)
        # Check ability to write to directory
        if not os.access(output_path, os.W_OK | os.X_OK):
            #TODO log fail
            print(f'Unable to write to directory: {output_path}')
        else:
            # TEMP
            print(f'Will scan files, input_path:{settings.input_path}, pattern:{regex}, file_type:{file_type}')
            file_matches = ps.scan_files(path=settings.input_path, pattern=regex, file_type=file_type)
            """
            sort_result = sort_files(files=file_matches, \
                number_pad=number_pad, \
                folder_increment=folder_increment, \
                collection_prefix=collection_prefix, \
                output_path=output_path)
            sorted_file_count += sort_result.get('sorted_file_count', 0)
            unmoved_file_count += sort_result.get('unmoved_file_count', 0)
            """
            print(file_matches)

    #file_matches = ps.scan_files(path=settings.input_path, pattern=settings.regex, file_type=settings.file_types)
    #derivs.process_folder(settings.input_path)
    #print(file_matches)

    # sort

    # generate urls
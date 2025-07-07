import powersorter as ps
import image_resizer

import csv
import argparse
import datetime

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

# gather args


# create config


# generate derivs

# sort


# generate urls

if __name__ == '__main__':
    # initialize settings
    # set up argparse
    args = arg_setup()
        #print(args)
    config_file = args['config']
    dry_run = args['dry_run']
    verbose = args['verbose']
    force_overwrite = args['force']
    input_path_override = args['input_path']
    #TODO implement prompt to confirm force_overwrite
    force_overwrite_confirmed = False

    # create settings based on args and config file
    settings = ps.Settings(dry_run=dry_run, verbose=verbose, force_overwrite=force_overwrite_confirmed)
    #Load settings from config
    settings.load_config(config_file=config_file)

    #show settings for testing
    attrs = vars(settings)
    # {'kids': 0, 'name': 'Dog', 'color': 'Spotted', 'age': 10, 'legs': 2, 'smell': 'Alot'}
    # now dump this in some way or another
    print(', '.join("%s: %s" % item for item in attrs.items()))
    #print(vars(settings))
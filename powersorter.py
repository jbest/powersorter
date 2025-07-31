import json
import re
import os
from pathlib import Path
import shutil
import datetime
import csv
import pwd
import argparse
import datetime
import sys
import threading

CONFIG_FORMAT_REQUIRED = '3.0'
sorted_file_count = 0
unmoved_file_count = 0

class SortLogger():
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, filename='test_powersorter.csv'):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, filename='test_powersorter.csv'):
        if self._initialized:
            return
        
        self.filename = Path(filename)
        #self.fieldnames = ['timestamp', 'module', 'level', 'message']
        self.fieldnames = ['timestamp', 'username', 'action', 'result', 'details', 'filetype', 'source', 'destination']
        self._file_lock = threading.Lock()
        
        # Create file with headers if it doesn't exist
        if not self.filename.exists():
            self._write_headers()
        
        self._initialized = True
    
    def _write_headers(self):
        with open(self.filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()
    
    def log(self, username=None, action=None, result=None, details=None, filetype=None, source=None, destination=None):
        with self._file_lock:
            with open(self.filename, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                writer.writerow({
                    'timestamp': datetime.now().isoformat(),
                    'username': username,
                    'action': action,
                    'result': result,
                    'details': details,
                    'filetype': filetype,
                    'source': source,
                    'destination': destination
                })

def scan_files(path=None, pattern=None, file_type=None):
    """
    Scan the directory for files matching the provided pattern.
    Extract relevant parts from file for organization and sorting
    Return a list of matching files
    """
    matches = []
    #print('pattern:', pattern)
    file_pattern = re.compile(pattern)
    for root, dirs, files in os.walk(path):
        for file in files:
            #print(os.path.join(root, file))
            m = file_pattern.match(file)
            if m:
                file_dict = m.groupdict()
                file_path = os.path.join(root, file)
                file_dict['file_path'] = file_path
                file_dict['file_type'] = file_type
                matches.append(file_dict)
    return matches

def sort_files(files=None, folder_increment=None, number_pad=None, collection_prefix=None, output_path=None, sort_logger=None):
    """
    Sort and move files into correct directory based on
    file pattern and directory name increments
    """
    sorted_file_count = 0
    unmoved_file_count = 0    
    for file in files:
        file_path = Path(file['file_path'])
        file_type = file['file_type']
        basename = file_path.name
        #print(f'File {file_path} will be sorted to {output_path}')
        numerical = int(file['numerical'])
        # Determine what folder number the files should be moved to
        folder_number = int(numerical//folder_increment*folder_increment)
        padded_folder_number = str(folder_number).zfill(number_pad)
        destination_folder_name = collection_prefix + padded_folder_number
        destination_path = Path(output_path).joinpath(destination_folder_name)
        #move_result = move_file(source=file_path, \
        move_result = move_file(source=file_path, \
            destination_directory=destination_path, \
            filename=basename, \
            filetype=file_type, \
            force_overwrite=settings.force_overwrite,
            sort_logger=sort_logger
            )
        if move_result['move_success']:
            sorted_file_count +=1
        else:
            unmoved_file_count +=1
    return {
        'sorted_file_count': sorted_file_count, \
        'unmoved_file_count': unmoved_file_count, \
        }

def move_file(source=None, destination_directory=None, filename=None, filetype=None, force_overwrite=False, sort_logger=None):
    """
    Move files from the source to the destination directory.
    Creates destination directory if it does not exist.
    Will overwrite existing files if force_overwrite_confirmed = True.
    """
    destination = destination_directory.joinpath(filename)
    if settings.dry_run:
        if destination.exists():
            now = datetime.datetime.now()
            move_success = False
            status = 'DRY-RUN - simulated move'
            writer.writerow({'timestamp': now, 'username': username, 'action': 'DRY_RUN-move', 'result': 'fail', \
                'filetype': filetype, 'source': source, 'destination': destination})

        else:
            print('DRY-RUN: Moved:', destination)
            status = 'DRY-RUN - simulated move'
            move_success = True
            now = datetime.datetime.now()
            writer.writerow({'timestamp': now, 'username': username, 'action': 'DRY_RUN-move', 'result': 'success', \
                'filetype': filetype, 'source': source, 'destination': destination})
    else:
        # Create directory path if it doesn't exist
        destination_directory.mkdir(parents=True, exist_ok=True)
        #TODO Log creation of directory? If so, will need to force exception and only log when no exception
        if destination.exists() and force_overwrite == False:
            if verbose:
                print('Filename exists, cannot move:', destination)
            #TODO change to exception
            move_success = False
            status = 'fail'
            details = 'filename exists'
            now = datetime.datetime.now()
            writer.writerow({'timestamp': now, 'username': username, 'action': 'move', 'result': status, 'details': details,\
                'filetype': filetype, 'source': source, 'destination': destination})
        else:
            try:
                if destination.exists():
                    details = 'duplicate file name - overwritten'
                    if verbose:
                        print('Overwritting:', destination)  
                else:
                    details = 'destination.exists = FALSE'
                shutil.move(source, destination)
                status = 'success'
                move_success = True
            except PermissionError:
                status = 'fail'
                details = 'PermissionError'
                move_success = False
            except Exception as e:
                status = 'fail'
                details = str(e)
                move_success = False
            now = datetime.datetime.now()
            writer.writerow({'timestamp': now, 'username': username, \
                'action': 'move', 'result': status, 'details': details, \
                'filetype': filetype, 'source': source, 'destination': destination})
            if verbose:
                print('Move:', destination, status)    
    return {'move_success': move_success, 'status': status}

# TODO Make dry run more useful - make it test destination perms and perms for each file to be moved

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

def sort(input_path=None, number_pad=None, folder_increment=None, catalog_number_regex=None,\
    collection_prefix=None, file_types=None, destination_base_path=None, sort_logger=None):
    # TODO check ALL output directories before scanning for files
    # scan, sort, and move each file type
    global sorted_file_count
    global unmoved_file_count # files matching pattern, but not moved/sorted
    
    #testing new sort logger
    if sort_logger:
        print('TEST-sort_logger', sort_logger)
    else:
        print('FAIL no sort logger')
        return

    for file_type, value in file_types.items():
        #print('file_type', file_type, 'value', value)
        #regex = value.get('regex', None)
        file_regex = value.get('file_regex', None)
	# Adding regex i flag here to make case-insensitive rather than in config files
        regex = '(?i)' + catalog_number_regex + file_regex
        output_sub_path = value.get('output_sub_path', None)
        output_path = destination_base_path.joinpath(output_sub_path)
        # Check ability to write to directory
        if not os.access(output_path, os.W_OK | os.X_OK):
            #TODO log fail
            print(f'Unable to write to directory: {output_path}')
        else:
            file_matches = scan_files(path=input_path, pattern=regex, file_type=file_type)
            sort_result = sort_files(files=file_matches, \
                number_pad=number_pad, \
                folder_increment=folder_increment, \
                collection_prefix=collection_prefix, \
                output_path=output_path,
                sort_logger=sort_logger)
            sorted_file_count += sort_result.get('sorted_file_count', 0)
            unmoved_file_count += sort_result.get('unmoved_file_count', 0)

class Settings():
    def __init__(self, prefix=None, dry_run=None, verbose=None, force_overwrite=None):
        self.prefix = prefix
        self.dry_run = dry_run
        self.verbose = verbose
        self.force_overwrite = force_overwrite

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
                self.files = config.get('files', None)
                self.input_path = self.files.get('input_path', None)
                self.folder_increment = int(self.files.get('folder_increment', 1000))
                self.log_directory_path = Path(self.files.get('log_directory_path', None))
                self.number_pad = int(self.files.get('number_pad', 7))
                self.output_base_path = Path(self.files.get('output_base_path', None))
                # Get the type of files and patterns that will be scanned and sorted
                self.file_types = config.get('file_types', None)
    
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

    settings = Settings(dry_run=dry_run, verbose=verbose, force_overwrite=force_overwrite_confirmed)
    #Load settings from config
    settings.load_config(config_file=config_file)

    # Check required config_file version
    if not str(settings.config_format) == CONFIG_FORMAT_REQUIRED:
        print('Wrong config format version:', settings.config_format, 'Required:', CONFIG_FORMAT_REQUIRED)
        sys.exit()

    # Generate log file name and path
    now = datetime.datetime.now()
    # use input_path arg or load from config settings
    if not input_path:
        input_path = Path(settings.input_path)

    # Check existence of input path
    if input_path:
        # test to ensure input directory exists
        if input_path.is_dir():
            print('Sorting files from input_path:', input_path)
        else:
            print(f'ERROR: directory {input_path} does not exist.')
            print('Terminating script.')
            quit()

    log_filename = '_'.join([settings.collection_prefix, input_path.stem, str(now.strftime('%Y-%m-%dT%H%M%S'))])
    if settings.dry_run:
        log_filename = log_filename + '_DRY-RUN'
    log_filename = log_filename + '.csv'
    log_file_path = settings.log_directory_path.joinpath(log_filename)

    # get current username
    try:
        username = pwd.getpwuid(os.getuid()).pw_name
    except:
        print('ERROR - Unable to retrive username.')
        username = None

    #original method
    csvfile = open(log_file_path, 'w', newline='')
    fieldnames = ['timestamp', 'username', 'action', 'result', 'details', 'filetype', 'source', 'destination']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    #Testing new CSV logger class
    test_log_filename = log_filename + '_TEST.csv'
    test_log_file_path = settings.log_directory_path.joinpath(test_log_filename)
    sort_logger=SortLogger(filename=test_log_file_path)
    print(sort_logger)

    #input_path = Path(settings.files.get('input_path', None))
    #print(settings.catalog_number_regex)
    # start sorting
    sort(input_path=input_path, \
        number_pad=settings.number_pad, \
        folder_increment=settings.folder_increment, \
        catalog_number_regex=settings.catalog_number_regex,\
        collection_prefix=settings.collection_prefix, \
        file_types=settings.file_types, \
        destination_base_path=settings.output_base_path,
        sort_logger=sort_logger)
    csvfile.close()
    # Summary report
    print('SORT COMPLETE')
    if verbose:
        print('sorted_file_count', sorted_file_count)
        print('unmoved_file_count', unmoved_file_count)
    print('Log file written to:', log_file_path)

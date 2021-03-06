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

def scan_files(path=None, pattern=None, file_type=None):
    """
    Scan the directory for files matching the provided pattern.
    Extract relevant parts from file for organization and sorting
    Return a list of matching files
    """
    # TODO use pathlib.Path.rglob to improve speed to
    # TODO first return relevant extensions
    # TODO then filter with regex

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

def sort_files(files=None, output_path=None):
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
        accession_number = int(file['numerical'])
        # Determine what folder number the files should be moved to
        folder_number = int(accession_number//folder_increment*folder_increment)
        padded_folder_number = str(folder_number).zfill(number_pad)
        destination_folder_name = collection_prefix + padded_folder_number
        destination_path = Path(output_path).joinpath(destination_folder_name)
        move_result = move_file(source=file_path, \
            destination_directory=destination_path, \
            filename=basename, \
            filetype=file_type, \
            )
        if move_result['move_success']:
            sorted_file_count +=1
        else:
            unmoved_file_count +=1
    return {
        'sorted_file_count': sorted_file_count, \
        'unmoved_file_count': unmoved_file_count, \
        }


def move_file(source=None, destination_directory=None, filename=None, filetype=None):
    """
    Move files from the source to the destination directory.
    Creates destination directory if it does not exist.
    Will not overwrite existing files.
    """
    destination = destination_directory.joinpath(filename)
    if destination.exists():
        if dry_run:
            now = datetime.datetime.now()
            writer.writerow({'timestamp': now, 'username': username, 'action': 'DRY_RUN-move', 'result': 'fail', \
                'filetype': filetype, 'source': source, 'destination': destination})
        if verbose:
            print('Filename exists, cannot move:', destination)
        #TODO change to exception
        move_success = False
        status = 'fail'
        details = 'filename exists'
        now = datetime.datetime.now()
        writer.writerow({'timestamp': now, 'username': username, 'action': 'move', 'result': status, 'details': details,\
            'filetype': filetype, 'source': source, 'destination': destination})
        return {'move_success': move_success, 'status': status}
    else:
        if dry_run:
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
            try:
                shutil.move(source, destination)
                status = 'success'
                details = None
                move_success = True
            except PermissionError:
                status = 'fail'
                details = 'PermissionError'
                move_success = False
            now = datetime.datetime.now()
            writer.writerow({'timestamp': now, 'username': username, \
                'action': 'move', 'result': status, 'details': details, \
                'filetype': filetype, 'source': source, 'destination': destination})
            if verbose:
                print('Move:', destination, status)
               
        return {'move_success': move_success, 'status': status}


# TODO Make dry run more useful - make it test destination perms and perms for each file to be moved

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
args = vars(ap.parse_args())

#print(args)

config_file = args['config']
dry_run = args['dry_run']
verbose = args['verbose']
input_path_override = args['input_path']

# load config file
with open(config_file) as f:
    config = json.load(f)

collection = config.get('collection', None)
collection_prefix = collection.get('prefix', None)
files = config.get('files', None)
folder_increment = int(files.get('folder_increment', 1000))
log_directory_path = Path(files.get('log_directory_path', None))
number_pad = int(files.get('number_pad', 7))
output_base_path = Path(files.get('output_base_path', None))

if input_path_override:
    input_path = Path(input_path_override)
else:
    input_path = Path(files.get('input_path', None))

# Check existence of input path
if input_path:
    # test to ensure input directory exists
    if input_path.is_dir():
        print('Sorting files from input_path:', input_path)
    else:
        print(f'ERROR: directory {input_path} does not exist.')
        print('Terminating script.')
        quit()

# Get the type of files and patterns that will be scanned and sorted
file_types = config.get('file_types', None)

# Generate log file name and path
now = datetime.datetime.now()
log_filename = collection_prefix + '_' + str(now.strftime('%Y-%m-%dT%H%M%S'))
if dry_run:
    log_filename = log_filename + '_DRY-RUN'
log_filename = log_filename + '.csv'
log_file_path = log_directory_path.joinpath(log_filename)

# get current username
try:
    username = pwd.getpwuid(os.getuid()).pw_name
except:
    print('ERROR - Unable to retrive username.')
    username = None

# TODO check ALL output directories before scanning for files

with open(log_file_path, 'w', newline='') as csvfile:
    fieldnames = ['timestamp', 'username', 'action', 'result', 'details', 'filetype', 'source', 'destination']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # scan, sort, and move each file type
    sorted_file_count = 0
    unmoved_file_count = 0 # files matching pattern, but not moved/sorted
    for file_type, value in file_types.items():
        regex = value.get('regex', None)
        output_sub_path = value.get('output_sub_path', None)
        output_path = output_base_path.joinpath(output_sub_path)
        # Check ability to write to directory
        if not os.access(output_path, os.W_OK | os.X_OK):
            print(f'Unable to write to directory: {output_path}')
        else:
            file_matches = scan_files(path=input_path, pattern=regex, file_type=file_type)
            sort_result = sort_files(files=file_matches, output_path=output_path)
            sorted_file_count += sort_result.get('sorted_file_count', 0)
            unmoved_file_count += sort_result.get('unmoved_file_count', 0)

# Summary report
print('SORT COMPLETE')
print('Log file written to:', log_file_path)
print('sorted_file_count', sorted_file_count)
print('unmoved_file_count', unmoved_file_count)

    


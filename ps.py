"""
Sample of using powersorter.py as an imported module.

"""
import datetime
import csv
from pathlib import Path

import powersorter


CONFIG_FORMAT_REQUIRED = '3.0'
sorted_file_count = 0
unmoved_file_count = 0


# initialize settings
# set up argparse and get arguments
args = powersorter.arg_setup()

config_file = args['config']
dry_run = args['dry_run']
verbose = args['verbose']
force_overwrite = args['force']
input_path_override = args['input_path']

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

settings = powersorter.Settings(dry_run=dry_run, verbose=verbose, force_overwrite=force_overwrite_confirmed)
#Load settings from config
settings.load_config(config_file=config_file)

# Check required config_file version
if not str(settings.config_format) == CONFIG_FORMAT_REQUIRED:
    print('Wrong config format version:', settings.config_format, 'Required:', CONFIG_FORMAT_REQUIRED)
    sys.exit()

# Generate log file name and path
now = datetime.datetime.now()
log_filename = settings.collection_prefix + '_' + str(now.strftime('%Y-%m-%dT%H%M%S'))
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

csvfile = open(log_file_path, 'w', newline='')
fieldnames = ['timestamp', 'username', 'action', 'result', 'details', 'filetype', 'source', 'destination']
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()

input_path = Path(settings.files.get('input_path', None))
#print(settings.catalog_number_regex)
# start sorting
powersorter.sort(input_path=input_path, \
    number_pad=settings.number_pad, \
    folder_increment=settings.folder_increment, \
    catalog_number_regex=settings.catalog_number_regex,\
    collection_prefix=settings.collection_prefix, \
    file_types=settings.file_types, \
    destination_base_path=settings.output_base_path)
csvfile.close()
# Summary report
print('SORT COMPLETE')
if verbose:
    print('sorted_file_count', sorted_file_count)
    print('unmoved_file_count', unmoved_file_count)
print('Log file written to:', log_file_path)
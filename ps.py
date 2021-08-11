"""
Sample of using powersorter.py as an imported module.

"""
import powersorter

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

#Initialize settings with arg parameters
settings = powersorter.Settings(dry_run=dry_run, verbose=verbose, force_overwrite=force_overwrite_confirmed)
#Load settings from config file
settings.load_config(config_file=config_file)

input_path = settings.input_path
# input_path setting in config file can be overridden using value passed in args input_path_override

# start sorting
print('STARTING')
sort_results = powersorter.sort(settings=settings, \
    input_path=input_path, \
    number_pad=settings.number_pad, \
    folder_increment=settings.folder_increment, \
    catalog_number_regex=settings.catalog_number_regex,\
    collection_prefix=settings.collection_prefix, \
    file_types=settings.file_types, \
    destination_base_path=settings.output_base_path)

# Summary report
print('SORT COMPLETE')
if verbose:
    print('sorted_file_count', sort_results['sorted_file_count'])
    print('unmoved_file_count', sort_results['unmoved_file_count'])
print('Log file written to:', sort_results['log_file_path'])
#! /usr/bin/env python3

# This next line will abort in any version earlier than Python 3.6:
f'This script requires Python 3.6 or newer.'

import getopt
import re
import logging
import datetime
import sys
import cdsapi

# Constants
UTILITY_NAME = 'era5_downloader'
VERSION_STRING = '0.0.1'
LOGGING_DOMAIN = UTILITY_NAME
DATASET = 'reanalysis-era5-single-levels'
PRODUCT_TYPE = 'reanalysis'
VARIABLES = [
    '10m_u_component_of_wind', '10m_v_component_of_wind', '2m_dewpoint_temperature',
    '2m_temperature', 'convective_precipitation', 'convective_snowfall',
    'large_scale_precipitation', 'large_scale_snowfall', 'mean_sea_level_pressure',
    'near_ir_albedo_for_diffuse_radiation', 'near_ir_albedo_for_direct_radiation',
    'uv_visible_albedo_for_diffuse_radiation', 'uv_visible_albedo_for_direct_radiation',
    'surface_latent_heat_flux', 'surface_sensible_heat_flux', 
    'surface_solar_radiation_downwards', 'surface_thermal_radiation_downwards',
    'surface_pressure', 'total_precipitation', 'skin_temperature',
    'eastward_turbulent_surface_stress', 'northward_turbulent_surface_stress',
    'surface_net_solar_radiation', 'surface_net_thermal_radiation'
]
FILE_FORMAT = 'netcdf'
CYCLING_INTERVAL = datetime.timedelta(seconds=3600) # 3600 = one hour
EPSILON = datetime.timedelta(seconds=5)  # epsilon for time comparison: five seconds

# Non-constant globals:
cycleset=set() # list of YYYYMMDDHH cycle strings
happy=True # False = something failed

def usage(why=None):
    print(f'''Synopsis: {UTILITY_NAME} [options] cycles [cycles [...]]

Downloads the listed cycles. Cycles can be specified as:
  2021081500 = specify one cycle: August 15, 2021 0:00 UTC
  2021081500-2021081900 = specify a range of cycles: August 15th 0 UTC to 19th 0 UTC, 2021
  2018 = specify an entire year (2018)

Options:
  -q | --quiet = log only warnings and errors
  -v | --verbose = log all messages
  --version = print {UTILITY_NAME} {VERSION_STRING}
  --help = this message
''')
    if why:
        sys.stderr.write(f'SCRIPT IS ABORTING BECAUSE: {why}\n')
        return 1
    return 0

# Function that makes the singleton for cdsapi client:
_client = None
def client():
    global _client
    if not _client:
        logging.info('creating cdsapi client')
        _client=cdsapi.Client()
    return _client

# The meat of the program: retrieve a file
def request(when):
    logging.info('Retrieve '+str(when)+'...')
    client().retrieve(DATASET,{
        'product_type': PRODUCT_TYPE,
        'variable': VARIABLES,
        'year': '%04d'%int(when.year),
        'month': [ '%02d'%int(when.month) ],
        'day': [ '%02d'%int(when.day) ],
        'time': [ '%02d:00'%int(when.hour) ],
        'format': FILE_FORMAT,
    }, 'era5_%04d%02d%02d%02d.nc'%( when.year, when.month, when.day, when.hour ))

# Parse arguments and initialize logging:
log_level = logging.INFO
optlist,args = getopt.getopt(sys.argv[1:],'qv',['version','help','verbose','quiet'])
if len(args)<1:
    exit(usage("No arguments provided!"))
for optarg in optlist:
    if optarg[0] in ['-q', '--quiet']:
        log_level = logging.WARNING
    elif optarg[0] in ['-v', '--verbose']:
        log_level = logging.DEBUG
    elif optarg[0]=='--help':
        exit(usage())
    elif optarg[0]=='--version':
        print(UTILITY_NAME+' '+VERSION_STRING)
        exit(0)
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=log_level)
logger = logging.getLogger(LOGGING_DOMAIN)

# Parse the cycles. This loop was modified from run_hafs.py:
for arg in args:
    if re.match('\A\d{10}\Z',arg):
        logger.info('single date/time')
        # Single date/time
        cycleset.add(arg)
    elif re.match('\A\d{4}\Z',arg):
        logger.info('year')
        # Year
        start=datetime.datetime(int(arg,10),1,1,0,0,0)
        end=datetime.datetime(int(arg,10),12,31,23,59,0)
        now=start
        while now<end+EPSILON:
            cycleset.add(now.strftime('%Y%m%d%H'))
            now+=CYCLING_INTERVAL
    elif re.match('\A\d{10}-\d{10}\Z',arg):
        logger.info('range of cycles')
        # Range of date/times
        start=datetime.datetime.strptime(arg[0:10],'%Y%m%d%H')
        end=datetime.datetime.strptime(arg[11:],'%Y%m%d%H')
        now=start
        while now<end+EPSILON:
            cycleset.add(now.strftime('%Y%m%d%H'))
            now+=CYCLING_INTERVAL
    else:
        logger.warning('Ignoring invalid argument "'+arg+'"')
        happy=False

# Sort the cycle list so we retrieve in order of increasing date:
cycles = list(cycleset)
cycles.sort()

if not cycles:
    logger.warning('Nothing to do! Exiting.')
    exit(1)

for cycle in cycles:
    # Turn the cycle string into a datetime.datetime:
    dcycle = None
    try:
        dcycle = datetime.datetime.strptime(cycle,'%Y%m%d%H')
    except ValueError as e:
        logger.warning(f'Ignoring invalid cycle "{cycle}"',exc_info=e)
        happy=False
        continue

    # Download the file:
    try:
        request(dcycle)
    except Exception as ex: # Unfortunately, cdsapi raises Exception
        happy = False
        logger.error(f'CDSAPI failed to download cycle {cycle}: {ex}',exc_info=e)

# Exit 0 on success, 1 on failure:
exit( 0 if happy else 1 )

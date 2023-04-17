from configparser import ConfigParser
from datetime import datetime

import logging
import urllib3
import argparse

from dates import *
from downloads import *

def validate_date_param(date: str, param_name:str):
    try:
        datetime.strptime(date, '%Y%m%d')

        config = ConfigParser()
        config.read('config.ini')
        earliest_date = config.get('searchref', 'begin_date')

        if get_date_diff(date, earliest_date) < 0:
            print(f'ERROR: {param_name} out of range. Date must be on or after {reformat_date(earliest_date)}.')
            exit()

    except ValueError:
        print(f'ERROR: Invalid {param_name} (passed \'{date}\')')
        exit()

if __name__ == "__main__":
    config = ConfigParser()
    config.read('config.ini')

    today_date = datetime.now().strftime("%Y%m%d")
    default_start_date = config.get('searchref', 'begin_date')
    default_end_date = today_date

    parser = argparse.ArgumentParser(description="SGX Data Downloader")
    parser.add_argument('--start-date', type=str, help='Specify a date in the format YYYYMMDD', default=default_start_date)
    parser.add_argument('--end-date', type=str, help='Specify a date in the format YYYYMMDD', default=default_end_date)
    parser.add_argument('--on-date', type=str, help='Download data from a single date', default=None)
    parser.add_argument('--today', action='store_true', help='Download only today\'s data')
    parser.add_argument('-o', type=str, help='Specify the filename for the output log', default=None)

    args = parser.parse_args()

    start_date = args.start_date
    end_date = args.end_date
    single_date = args.on_date
    use_today = args.today
    output_log = args.o

    validate_date_param(start_date, 'start date')
    validate_date_param(end_date, 'end date')

    if single_date is not None:
        validate_date_param(single_date, 'date')

    # setup logger
    logging.basicConfig(
        filename=output_log,
        level=logging.NOTSET,
        format='%(asctime)s - %(message)s', 
        datefmt='%d-%b-%y %H:%M:%S'
    )

    # prevent logging requests
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # prep data download
    total_days = get_business_days_diff(start_date, end_date) + 1

    if use_today:
        download_day_files(today_date)
        
    elif single_date is not None:
        download_day_files(single_date)
    
    elif total_days == 1:
        download_day_files(start_date)

    elif total_days >= 100:
        proceed = input(f"WARNING: Estimated {total_days} days of data will be downloaded. This is a large range. Proceed? (Y/N) ")
        
        if proceed == 'Y' or proceed == 'y':
            batch_download_files(start_date, end_date)

    elif total_days > 1:
        batch_download_files(start_date, end_date)

    else:
        if start_date == default_start_date: # before - today is negative
            logging.error("Error: Today's date cannot be after --end-date")
        elif end_date == default_end_date:
            logging.error("Error: --start-date cannot be after today's date")
        else:
            logging.error("Error: --start-date cannot be after --end-date")
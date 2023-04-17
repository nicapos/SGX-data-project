from configparser import ConfigParser
from datetime import datetime, timedelta

import urllib.request
import os
import ssl
import logging
import urllib3
import argparse

from dates import find_id, find_relative_id, get_business_days_diff, get_date_diff, get_date_by_id

FILENAMES = ["WEBPXTICK_DT.zip", "TickData_structure.dat", "TC.txt", "TC_structure.dat"]

def reformat_date(date_Ymd: str):
    return datetime.strptime(date_Ymd, '%Y%m%d').strftime('%Y-%m-%d')
    
def download_file(filename: str, id: int, date: str):
    # Setup output directory
    current_dir = os.getcwd()
    output_dir = os.path.join(current_dir, 'output')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Setup date directory inside output directory
    formatted_date = reformat_date(date)
    date_dir = os.path.join(output_dir, formatted_date)

    if not os.path.exists(date_dir):
        os.makedirs(date_dir)

    # Setup download url
    config = ConfigParser()
    config.read('config.ini')

    base_url = config.get('links', 'download_url')
    url = base_url + '/' + str(id) + '/' + filename

    # Disable certificate verification
    context = ssl._create_unverified_context()

    # Download file to output directory
    with urllib.request.urlopen(url, context=context) as response:
        content_disposition = response.headers.get('Content-Disposition')

        if content_disposition is None:
            raise Exception(f'Error downloading {filename}.')

        dl_filename = content_disposition.split('filename=')[1]
        file_path = os.path.join(date_dir, dl_filename)

        if os.path.exists(file_path):
            raise Exception(f"\tFile '{dl_filename}' already exists.")
        else:
            with open(file_path, 'wb') as file:
                file.write(response.read())

def download_day_files(param_date):
    date = param_date
    id = find_relative_id(date)

    logging.info(f"Preparing to download data from {reformat_date(date)}...")

    for index, filename in enumerate(FILENAMES):
        try:
            download_file(filename, id, date)
            logging.info(f'Downloaded {filename} ({index+1}/{len(FILENAMES)})...')
        except Exception as e:
            logging.error(e)

    logging.info(f"Export complete! Check ./output/{reformat_date(date)} for files")

def batch_download_files(start_date, end_date):
    start_id = find_relative_id(start_date)
    end_id = find_relative_id(end_date)

    total = end_id - start_id + 1

    logging.info(f"Preparing to download data from {reformat_date(start_date)} to {reformat_date(end_date)}...")
    
    for id in range(start_id, end_id+1):
        date = get_date_by_id(id)

        for filename in FILENAMES:
            try:
                download_file(filename, id, date)
            except Exception as e:
                logging.error(e)

        logging.info(f"Downloaded data from {reformat_date(date)} ({id-start_id+1}/{total})...")

    logging.info(f"Export complete! Check ./output/ for files")
    

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
    logging.basicConfig(
        level=logging.NOTSET,
        format='%(asctime)s - %(message)s', 
        datefmt='%d-%b-%y %H:%M:%S'
    )

    # prevent logging requests
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # setup arguments
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

    args = parser.parse_args()

    start_date = args.start_date
    end_date = args.end_date
    single_date = args.on_date
    use_today = args.today

    validate_date_param(start_date, 'start date')
    validate_date_param(end_date, 'end date')

    if single_date is not None:
        validate_date_param(single_date, 'date')

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
from datetime import datetime
from configparser import ConfigParser

import time
import schedule
import logging
import argparse

from dates import *
from downloads import *
from main import validate_date_param

backlog = []

def add_to_backlog(date, end_date=None):
    btype = "SINGLE" if end_date is None else "MULTI"
    backlog.append( (btype, date, end_date) )

def is_data_available(date):
    relative_id = find_relative_id(date)
    latest_available_date = get_date_by_id(relative_id)

    return date == latest_available_date

def download_today():
    today = datetime.now()
    today_date = today.strftime('%Y%m%d')

    is_weekday = today.weekday() < 5

    if not is_data_available(today_date) and is_weekday:
        add_to_backlog(today_date)
        logging.error("ERROR: Unable to access files for the current day. Retrying on the next scheduled run.")

    elif not is_weekday:
        logging.info("ERROR: No files to download today (not a weekday).")

    else:
        download_day_files(today_date)

def validate_time_param(time_str, param_name:str):
    try:
        hours, minutes = map(int, time_str.split(':'))
        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            raise ValueError
        
        return time_str
    except ValueError:
        print(f'ERROR: Invalid {param_name}, must be a valid 24-hour time in HH:MM format (passed \'{time_str}\')')
        exit()

if __name__ == "__main__":
    config = ConfigParser()
    config.read('config.ini')

    today_date = datetime.now().strftime('%Y%m%d')
    default_start_date = reformat_date(today_date)

    parser = argparse.ArgumentParser(description="SGX Data Downloader Job")
    parser.add_argument('--start-date', type=str, help='Specify the start date in the format YYYY-MM-DD', default=default_start_date)
    parser.add_argument('--exec-at', type=str, help='Specify the daily execution time in HH:MM format', default='17:00')
    parser.add_argument('-o', type=str, help='Specify the filename for the output log', default=None)

    args = parser.parse_args()

    start_date = validate_date_param(args.start_date, 'start date')
    exec_time = validate_time_param(args.exec_at, 'execution time')
    output_log = args.o

    if args.o is not None:
        output_log = validate_file_path(args.o)
    
    # setup logger
    logging.basicConfig(
        filename=output_log,
        level=logging.NOTSET,
        format='%(asctime)s - %(message)s', 
        datefmt='%d-%b-%y %H:%M:%S'
    )

    # download today's files + from date/s in args
    total_days = get_business_days_diff(start_date, today_date) + 1
    if total_days == 1:
        download_today()

    elif total_days > 1:
        batch_download_files(start_date, today_date)

    # setup auto download job
    def job():
        download_today()

        for job in backlog:
            download_type, date, end_date = job

            if download_type == 'SINGLE':
                is_weekday = datetime.strptime(date, '%Y%m%d').weekday() < 5
                
                if not is_data_available(date) and is_weekday:
                    add_to_backlog(date)
                    logging.error("ERROR: Unable to access files for the {date}. Retrying on the next scheduled run.")
                
                else:
                    download_day_files(date)

            elif download_type == 'MULTI':
                batch_download_files(date, end_date)

    schedule.every().day.at(exec_time).do(job)
    logging.info("Running daily job. Scheduled execution time: 15:30.")

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logging.error("Program terminated by user (KeyboardInterrupt)")
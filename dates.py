from datetime import datetime, timedelta
import numpy as np
from configparser import ConfigParser
import requests
import re
import urllib3
import logging

def find_id(date: str):
    """
    date (str): Date in the format 'YYYYMMDD'.
    Returns the ACTUAL id of the given param_date (if valid), None if no id for given date
    """
    id = get_id_by_date(date)
    actual_date = get_date_by_id(id)
    prev_dd = 0

    if actual_date is None:
        return None

    while date != actual_date and prev_dd != 0:
        date_diff = get_business_days_diff(date, actual_date)

        if prev_dd + date_diff == 0: # to prevent infinite loop in case of order mismatch
            id += 1
        else:
            id -= date_diff

        prev_dd = date_diff
        actual_date = get_date_by_id(id)

    return id

def find_relative_id(date: str):
    """
    date (str): Date in the format 'YYYYMMDD'.
    Returns the id of the given param_date (if any), else returns the id from the nearest earlier date
    """
    id = find_id(date)

    config = ConfigParser()
    config.read('config.ini')
    earliest_date = config.get('searchref', 'begin_date')


    while id is None and get_date_diff(date, earliest_date) > 0:
        day_before = datetime.strptime(date, '%Y%m%d') - timedelta(days=1)
        date = day_before.strftime("%Y%m%d")
        
        id = find_id(date)

    return id

def get_id_by_date(date: str) -> int:
    """
    date (str): Date in the format 'YYYYMMDD'.
    Returns the ESTIMATE id of the given param_date (if valid)
    """
    config = ConfigParser()
    config.read('config.ini')

    ref_id = config.getint('searchref', 'id')
    ref_date = config.get('searchref', 'date')

    start = datetime.strptime(ref_date, '%Y%m%d').date()
    end = datetime.strptime(date, '%Y%m%d').date()
    
    diff = np.busday_count(start, end) 

    return ref_id + diff

def get_date_by_id(id: int) -> datetime:
    """
    id (int): key id to search for date
    Returns the date of the given id in the format 'YYYYMMDD'.
    """
    config = ConfigParser()
    config.read('config.ini')

    download_url = config.get('links', 'download_url')
    TC_url = download_url + str(id) + "/TC.txt"

    # prevent logging requests
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    response = requests.get(TC_url)

    content_disposition = response.headers.get('Content-Disposition')

    if content_disposition is None:
        return None
    
    # Extract date from filename in URL
    date_pattern = r"\d{8}"
    date_match = re.search(date_pattern, content_disposition)

    if date_match:
        return date_match.group()

    return None

def get_date_diff(date_str1: str, date_str2: str) -> int:
    date1 = datetime.strptime(date_str1, "%Y%m%d")
    date2 = datetime.strptime(date_str2, "%Y%m%d")

    time_diff = date1 - date2
    return time_diff.days

def add_date_days(date: str, days: int) -> str:
    new_date = datetime.strptime(date, "%Y%m%d") + timedelta(days=days)
    return new_date.strftime("%Y%m%d")

def get_business_days_diff(date_str1: str, date_str2: str):
    start_date = datetime.strptime(date_str1, "%Y%m%d")
    end_date = datetime.strptime(date_str2, "%Y%m%d")

    start_date_np = np.datetime64(start_date, "[D]")
    end_date_np = np.datetime64(end_date, "[D]")

    num_business_days = np.busday_count(start_date_np, end_date_np, weekmask="Mon Tue Wed Thu Fri")
    return num_business_days
    

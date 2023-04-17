from datetime import datetime, timedelta
import numpy as np
from configparser import ConfigParser
import requests
import random

def find_id(date: str):
    """
    date (str): Date in the format 'YYYYMMDD'.
    Returns the ACTUAL id of the given param_date (if valid)
    """
    id = get_id_by_date(date)
    actual_date = get_date_by_id(id)
    prev_dd = 0

    while date != actual_date:
        date_diff = get_business_days_diff(date, actual_date)

        if prev_dd + date_diff == 0: # to prevent infinite loop in case of order mismatch
            id += 1
        else:
            id -= date_diff

        prev_dd = date_diff
        actual_date = get_date_by_id(id)

    return id

def get_id_by_date(date: str) -> int:
    """
    date (str): Date in the format 'YYYYMMDD'.
    Returns the ESTIMATE id of the given param_date (if valid)
    """
    config = ConfigParser()
    config.read('config.ini')

    ref_id = config.get('searchref', 'id')
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

    response = requests.get(TC_url)

    content_disposition = response.headers.get('Content-Disposition')
    date = content_disposition.split("_")[1].split(".")[0]

    return date

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
    

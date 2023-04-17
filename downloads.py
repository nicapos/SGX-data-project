from configparser import ConfigParser

import urllib.request
import os
import ssl
import logging

from dates import *

FILENAMES = ["WEBPXTICK_DT.zip", "TickData_structure.dat", "TC.txt", "TC_structure.dat"]

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
    
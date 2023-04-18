from configparser import ConfigParser

import urllib.request
import os
import ssl
import logging

from dates import *

FILENAMES = ["WEBPXTICK_DT.zip", "TickData_structure.dat", "TC.txt", "TC_structure.dat"]

def validate_file_path(filepath):
    parts = filepath.split('/')
    filename = parts.pop()

    # Create the directories if they do not exist
    if len(parts):
        os.makedirs(os.path.join(*parts), exist_ok=True)

    return os.path.join(*parts, filename)

def download_file(filename: str, id: int, date: str):
    # Setup directory for downloads
    formatted_date = reformat_date(date)
    date_dir = '/output/' + formatted_date

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
        file_path = validate_file_path(date_dir + '/' + dl_filename)

        if os.path.exists(file_path):
            raise Exception(f"\tFile '{dl_filename}' already exists.")
        else:
            with open(file_path, 'wb') as file:
                file.write(response.read())

def download_day_files(param_date):
    date = param_date
    id = find_relative_id(date)

    logging.info(f"Preparing to download data from {reformat_date(date)}...")

    skipped_downloads = []

    for index, filename in enumerate(FILENAMES):
        try:
            download_file(filename, id, date)
            logging.info(f'({index+1}/{len(FILENAMES)}) Downloaded {filename}')
        except Exception as e:
            if 'already exists' in str(e):
                skipped_downloads.append(filename)
            else:
                logging.error(e)

    message = 'Export complete! ' if len(skipped_downloads) < len(FILENAMES) else ''
    if len(skipped_downloads) > 0:
        message += f'Skipped downloading {len(skipped_downloads)} files (already exists). '

    logging.info(message + f"Check ./output/{reformat_date(date)} for files")

def batch_download_files(start_date, end_date):
    start_id = find_relative_id(start_date)
    end_id = find_relative_id(end_date)

    total = end_id - start_id + 1

    logging.info(f"Preparing to download data from {reformat_date(start_date)} to {reformat_date(end_date)}...")
    
    for id in range(start_id, end_id+1):
        date = get_date_by_id(id)

        skipped_downloads = []

        for filename in FILENAMES:
            try:
                download_file(filename, id, date)
            except Exception as e:
                if 'already exists' in str(e):
                    skipped_downloads.append(filename)
                else:
                    logging.error(e)

        total_downloads = len(FILENAMES) - len(skipped_downloads)
        
        message = f'Downloaded {total_downloads} files from {reformat_date(date)} '
        if len(skipped_downloads) > 0:
            message += f'(skipped {len(skipped_downloads)} already existing files)'

        logging.info(f"({id-start_id+1}/{total}) {message}")

    logging.info(f"Export complete! Check ./output/ for files")
    
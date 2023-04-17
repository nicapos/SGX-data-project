# SGX Derivatives Data Scraper

Python script to download [SGX derivatives data](https://www.sgx.com/research-education/derivatives) for a single day or a specific range of dates.

## Installation
(Optional) Create a virtual environment by running `python3 -m venv venv`. Activate the virtual environment by running `source venv/bin/activate` on Linux/Mac or `venv\Scripts\activate` on Windows. You can exit this environment anytime by running `deactivate` or `source deactivate`.

To install the dependencies for this project, run the following command:
```bash
pip install -r requirements.txt
```

## Usage
To use the program, run `main.py` with the following optional arguments:

* `--start-date`: Specify the start date for downloading data in the format YYYYMMDD.
* `--end-date`: Specify the end date for downloading data in the format YYYYMMDD.
* `--on-date`: Download data for a single date specified in the format YYYYMMDD.
* `--today`: Download data only for today's date.

#### Example usage:
```bash
python3 main.py --start-date 20230401 --end-date 20230410
```
This will download data for the range of dates from April 1, 2023, to April 10, 2023.
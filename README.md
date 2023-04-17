# SGX Derivatives Data Scraper

Python script to download [SGX derivatives data](https://www.sgx.com/research-education/derivatives) for a single day or a specific range of dates.

The following files will be downloaded for each day:
1. WEBPXTICK_DT-*.zip
2. TickData_structure.dat
3. TC_*.txt
4. TC_structure.dat

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
* `-o`: Specify the filename for the output log.

#### Example usage:
1. Download data for a specific date:
```bash
python main.py --on-date 20230410
```

2. Download data for a date range:
```bash
python3 main.py --start-date 20230401 --end-date 20230410
```

3. Download only today's data:
```bash
python main.py --today
```

4. Specify a custom filename for the output log:
```bash
python3 main.py --start-date 20230401 --end-date 20230410 -o output.log
```
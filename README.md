# SGX Derivatives Data Scraper

Python script to download [SGX derivatives data](https://www.sgx.com/research-education/derivatives) for a single day or a specific range of dates.

The following files will be downloaded for each day:
1. WEBPXTICK_DT-*.zip
2. TickData_structure.dat
3. TC_*.txt
4. TC_structure.dat

## Installation
1. Clone the repository
```bash
git clone https://github.com/nicapos/SGX-data-project.git
```

2. Navigate to the project folder
```bash
cd SGX-data-project
```

3. *(Optional)* Create a virtual environment by running the following:
```bash
python3 -m venv venv
```

Activate the virtual environment based on your operating system:
* For Linux/Mac:
```bash
source venv/bin/activate
```
* For Windows:
```bash
venv\Scripts\activate
```
You can exit this environment anytime by running `deactivate` or `source deactivate`.

4. To install the dependencies for this project, run the following command:
```bash
pip install -r requirements.txt
```

## Usage
To use the program, run [`main.py`](./main.py) with the following optional arguments:

| args | Description |
| --- | --- |
| `--start-date` | Specify the start date for downloading data in the format YYYY-MM-DD. |
| `--end-date` | Specify the end date for downloading data in the format YYYY-MM-DD. |
| `--on-date` | Download data for a single date specified in the format YYYY-MM-DD. |
| `--today` | Download data only for today's date. |
| `-o` | Specify the filename for the output log. |

#### Example usage
1. Download data for a specific date:
```bash
python3 main.py --on-date 2023-04-10
```

2. Download data for a date range:
```bash
python3 main.py --start-date 2023-04-01 --end-date 2023-04-10
```

3. Download only today's data:
```bash
python3 main.py --today
```

4. Download data for a date range and specify an output log:
```bash
python3 main.py --start-date 2023-04-01 --end-date 2023-04-10 -o logs/output.log
```
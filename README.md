# Electricity Bill Calculator

A Python-based application to calculate electricity and water bills for shared accommodations. The app distributes costs based on individual stay durations.

## Features

- Calculate electricity and water bills proportionally based on stay days.
- Support for manual or file-based input of residents and their days off.
- Save and load resident data for reuse.
- Interactive command-line interface with rich text formatting.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/nguyenguyen0/calculate_electricity_bill.git
   cd calculate_electricity_bill
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application using:
```bash
python -m app
```

### Command-Line Options

- `--electric-bill` or `-e`: Specify the total electricity bill.
- `--water-bill` or `-w`: Specify the total water bill.
- `--people` or `-p`: Provide a list of residents in the format `name=days_off` or just `name`.
- `--load-file` or `-lf`: Load resident data from a file.
- `--save-file` or `-sf`: Save resident data to a file.
- `--date-now` or `-dn`: Use the current date for calculations.
- `--month` or `-m` and `--year` or `-y`: Specify the billing month and year.

Example:
```bash
python -m app --electric-bill 500000 --water-bill 200000 --people "Alice=2" "Bob=1"
```

## File Structure

- `models.py`: Contains data models for residents and bills.
- `calculator.py`: Handles bill calculations.
- `storage.py`: Manages saving and loading resident data.
- `ui.py`: Provides a rich-text user interface.
- `app.py`: Main application logic.
- `__main__.py`: Entry point for the application.

## Requirements

- Python 3.10+
- Dependencies listed in `requirements.txt`

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

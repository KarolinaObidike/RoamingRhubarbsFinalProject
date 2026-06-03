import csv
from pathlib import Path
from typing import Optional


def extract_data(file_path):
    fieldnames = [
        'timestamp',
        'location',
        'customer name',
        'items ordered',
        'total amount',
        'payment method',
        'card number',
    ]
    data = []
    with open(file_path, mode='r', encoding='utf-8', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if not row:
                continue
            if row[0].startswith('\ufeff'):
                row[0] = row[0].lstrip('\ufeff')
            if len(row) < len(fieldnames):
                continue
            data.append(dict(zip(fieldnames, row)))
    return data


def get_data(data=None, file_path: Optional[str] = None, search_dir: Optional[str] = None):
    """
    Return extracted data.

    - If `data` is provided, return it unchanged.
    - If `file_path` is provided, load from that CSV (error if missing).
    - Otherwise search `search_dir` (or current working dir) for the most
      recently modified `*.csv` file and load it.
    """
    if data is not None:
        return data

    # If explicit file path provided use it
    if file_path:
        csv_path = Path(file_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")
    else:
        # search for CSV files in provided directory or current working dir
        search_path = Path(search_dir) if search_dir else Path.cwd()
        candidates = sorted(
            search_path.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True
        )
        if not candidates:
            raise FileNotFoundError(f"No CSV files found in {search_path}")
        csv_path = candidates[0]

    return extract_data(str(csv_path))


def print_data_table(data):
    if not data:
        print('No data to display.')
        return

    headers = [
        'timestamp',
        'location',
        'customer name',
        'items ordered',
        'total amount',
        'payment method',
        'card number',
    ]

    print(' | '.join(headers))
    print('-' * 120)
    for row in data:
        print(' | '.join(str(row.get(key, '')) for key in headers))


if __name__ == '__main__':
    data = get_data()
    print_data_table(data)

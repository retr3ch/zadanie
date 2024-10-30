import requests
import re
from datetime import datetime

import config

def fetch_logs(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Ошибка при получении данных: HTTP {response.status_code}")
        return None

def parse_log_line(log_line):
    log_pattern = re.compile(config.format)
    match = log_pattern.match(log_line)
    if match:
        return match.groups()
    else:
        return None

def insert_logs_to_db(db_cursor, log_data):
    db_cursor.execute('''
        CREATE TABLE IF NOT EXISTS apache_logs (
            host TEXT,
            identity TEXT,
            user TEXT,
            time TEXT,
            request TEXT,
            status INTEGER,
            size TEXT
        )
    ''')
    db_cursor.execute('''
        INSERT INTO apache_logs (host, identity, user, time, request, status, size)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', log_data)

def delete_table(db_cursor):
    db_cursor.execute('DROP TABLE IF EXISTS apache_logs')

def get_logs_from_db(db_cursor, table_name):
    db_cursor.execute(f"SELECT * FROM {table_name}")
    rows = db_cursor.fetchall()
    return rows

def filter_data(rows, filter_values):
    filtered_logs = []
    date_range = []
    filter_date = []

    for value in filter_values :
        try:
            date_time = datetime.strptime(value, '%d/%b/%Y:%H:%M:%S')
            date_range.append(date_time)
            filter_date.append(value)
        except ValueError:
            pass

    if len(date_range) == 2:
        date_range.sort()

    for date in filter_date:
        filter_values.remove(date)

    for row in rows:
        match = True
        log_date_str = row[3]
        log_date = datetime.strptime(log_date_str, '%d/%b/%Y:%H:%M:%S +0000')

        if len(date_range) == 2 and not (date_range[0] <= log_date <= date_range[1]):
            continue
        
        for filter_value in filter_values:
            if not any(re.search(r'\b' + re.escape(filter_value) + r'\b', str(field)) for field in row):
                match = False
                break

        if match:
            filtered_logs.append(row)

    return filtered_logs
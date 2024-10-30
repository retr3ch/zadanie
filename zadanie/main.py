import sqlite3

import config
import func

def main():
    while True:
        action = input("logwriter : ")
        if action == "parse":
            if config.logs:
                conn = sqlite3.connect(config.db_name)
                cursor = conn.cursor()
                func.delete_table(cursor)
                for log_line in config.logs.split('\n'):
                    log_data = func.parse_log_line(log_line)
                    if log_data:
                        func.insert_logs_to_db(cursor, log_data)
                conn.commit()
                conn.close()
                print("Успешно")
            else:
                print("Нет логов")
        else:
            conn = sqlite3.connect(config.db_name)
            cursor = conn.cursor()
            filters = action.split()
            all_data = func.get_logs_from_db(cursor, config.table_name)
            filtered_data = func.filter_data(all_data, filters)
            for row in filtered_data:
                print(row)
            conn.commit()
            conn.close()
    
if __name__ == "__main__":
    main()

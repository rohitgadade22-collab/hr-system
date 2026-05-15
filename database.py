import configparser
import pyodbc

def get_connection():

    config = configparser.ConfigParser()

    config.read('config.ini')

    db_host = config['database']['host']
    db_port = config['database']['port']
    db_user = config['database']['username']
    db_password = config['database']['password']
    db_name = config['database']['database']

    connection_string = f'''
    DRIVER={{ODBC Driver 17 for SQL Server}};
    SERVER={db_host},{db_port};
    DATABASE={db_name};
    UID={db_user};
    PWD={db_password};
    '''

    conn = pyodbc.connect(connection_string)

    return conn
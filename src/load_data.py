#! /usr/bin/python3

import json
import psycopg2
from config import DATABASE_CONFIG, DATASET_PATH

def connect_db():
    '''Connect to the PostgreSQL database server.'''        
    conn = None
    try:
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**DATABASE_CONFIG) 
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return conn

def load_json(file_path):
    '''Basic helper function which attempts to load data from a JSON file'''        
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    else:
        raise OSError(f'JSON file not found: {file_path}')



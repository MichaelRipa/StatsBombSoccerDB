#! /usr/bin/python3

from glob import glob
import json
import os
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

def get_file_paths(dataset_type):
    '''
    Generates file paths for a given dataset type.

    dataset_type: str - The type of dataset ("competitions", "events", "lineups", "matches", "three-sixty")

    return: iterator of file paths cooresponding to the dataset type
    '''
    base_path = os.path.join(DATASET_PATH, 'data')
    if dataset_type == 'competitions':
        # Competitions just has a single JSON file.
        return [os.path.join(base_path, 'competitions.json')]

    elif dataset_type in ['events', 'lineups', 'three-sixty']:
        # These datasets have mutliple JSON files per directory.
        path_pattern = os.path.join(base_path, dataset_type, '*.json')
        return sorted(glob(path_pattern), key=lambda path: int(os.path.basename(path).strip('.json')))
    elif dataset_type == 'matches':
        # Matches are further categorized into folders of their cooresponding competition ids
        path_pattern = os.path.join(base_path, 'matches', '*', '*.json')
        file_paths = glob(path_pattern)
        # Sort by competition id and then by match id
        return sorted(file_paths, key=lambda path: (int(os.path.split(os.path.dirname(path))[-1]), int(os.path.basename(path).strip('.json'))))
        
    else:
        raise ValueError(f'Unknown dataset type {dataset_type}')

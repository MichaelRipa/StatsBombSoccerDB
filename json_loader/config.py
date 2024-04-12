#! /usr/bin/python3
import os

DATABASE_CONFIG = {
    'dbname': 'soccerdb',
    'user': 'username',
    'password': 'password',
    'host': 'localhost',
}

# This setup assumes the data is unzipped in the parent directory of the repo.
current_dir = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(os.path.dirname(current_dir), 'open-data')

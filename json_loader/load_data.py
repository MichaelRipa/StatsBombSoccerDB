#! /usr/bin/python3

import argparse
from glob import glob
import json
import os
import psycopg
from config import DATABASE_CONFIG, DATASET_PATH

def connect_db():
    '''Connect to the PostgreSQL database server.'''        
    conn = None
    try:
        print('Connecting to the PostgreSQL database...')
        conn = psycopg.connect(**DATABASE_CONFIG) 
    except (Exception, psycopg.DatabaseError) as error:
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

def load_competitions(file_path, conn):
    '''Load competition data from a JSON file into the database.'''
    data = load_json(file_path) 

    # SQL to get country_id from country_name
    country_id_sql = "SELECT country_id FROM country WHERE country_name = %s;"

    # SQL to insert data into the competition table
    insert_sql = ''' 
    INSERT INTO competition (
        competition_id, 
        competition_name, 
        competition_gender, 
        competition_youth, 
        competition_international,
        season_id, 
        country_id,
    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (competition_id) DO NOTHING;
    '''

    with conn.cursor() as cur:
        for entry in data:
            competition_id = int(entry['competition_id'])
            season_id = int(entry['season_id'])
            country_name = entry['country_name']
            competition_name = entry['competition_name']
            competition_gender = entry['competition_gender']
            competition_youth = bool(entry['competition_youth'])
            competition_international = bool(entry['competition_international'])

            # TODO: Consider whether I need to load in these attributes or not.

            season_name = entry['season_name']
            match_updated = entry['match_updated']
            match_updated_360 = entry.get('match_updated_360')
            match_available = entry['match_available']
            match_available_360 = entry.get('match_available_360')

            # Get country_id from country_name
            cur.execute(country_id_sql, (entry['country_name'],))
            country_id = cur.fetchone()
            if country_id:
                country_id = country_id[0]

            else:
                print(f"Country name {entry['country_name']} not found in database.")
                continue  # Skip this entry

            # Execute the SQL insert statement
            cur.execute(insert_sql, (
                competition_id,
                season_id,
                country_name,
                competition_name,
                competition_gender,
                competition_youth,
                competition_international
            ))

            # Print extracted data for debugging
            print(f"Competition ID: {competition_id}, Season ID: {season_id}, Country Name: {country_name}")
            print(f"Competition Name: {competition_name}, Gender: {competition_gender}")
            print(f"Youth: {competition_youth}, International: {competition_international}")
            print(f"Season Name: {season_name}, Match Updated: {match_updated}")
            print(f"Match Updated 360: {match_updated_360}, Match Available: {match_available}")
            print(f"Match Available 360: {match_available_360}") 
            print('\n')
            
    # Commit all changes to the database
    conn.commit()

def load_events(file_path):
    '''Load event data from a JSON file into the database.'''
    data = load_json(file_path) 
    for entry in data:
        event_id = entry['id']
        index = entry['index']
        period = entry['period']
        timestamp = entry['timestamp']
        minute = entry['minute']
        second = entry['second']
        
        # Extracting data from nested 'type' dictionary
        event_type_id = entry['type']['id']
        event_type_name = entry['type']['name']
        
        possession = entry['possession']
        
        # Extracting data from nested 'possession_team' dictionary
        possession_team_id = entry['possession_team']['id']
        possession_team_name = entry['possession_team']['name']
        
        # Extracting data from nested 'play_pattern' dictionary
        play_pattern_id = entry['play_pattern']['id']
        play_pattern_name = entry['play_pattern']['name']
        
        # Extracting data from nested 'team' dictionary
        team_id = entry['team']['id']
        team_name = entry['team']['name']
        
        # Handling potentially missing 'related_events' key
        related_events = entry.get('related_events', [])
        
        # Print extracted data for debugging
        print(f"Event ID: {event_id}, Index: {index}, Period: {period}, Timestamp: {timestamp}")
        print(f"Minute: {minute}, Second: {second}, Event Type: {event_type_id} - {event_type_name}")
        print(f"Possession: {possession}, Possession Team: {possession_team_id} - {possession_team_name}")
        print(f"Play Pattern: {play_pattern_id} - {play_pattern_name}, Team: {team_id} - {team_name}")
        print(f"Related Events: {related_events}") 
        print('\n')

def load_lineups(file_path):
    '''Load lineup data from a JSON file into the database.'''

    data = load_json(file_path) 
    for entry in data:
        team_id = entry['team_id']
        team_name = entry['team_name']
        lineup = entry['lineup']
        
        for player in lineup:
            player_id = player['player_id']
            player_name = player['player_name']
            player_nickname = player['player_nickname'] if player['player_nickname'] else None
            jersey_number = player['jersey_number']
            country_id = player['country']['id']
            country_name = player['country']['name']
            
            cards = player['cards']  # List of cards if any
            positions = player['positions']
            
            for position in positions:
                position_id = position['position_id']
                position_name = position['position']
                from_time = position['from']
                to_time = position['to'] if position['to'] else None
                from_period = position['from_period']
                to_period = position['to_period'] if position['to_period'] else None
                start_reason = position['start_reason']
                end_reason = position['end_reason']

                # Print or process these details
                print(f"Team ID: {team_id}, Team Name: {team_name}")
                print(f"Player ID: {player_id}, Player Name: {player_name}, Nickname: {player_nickname}, Jersey Number: {jersey_number}")
                print(f"Country ID: {country_id}, Country Name: {country_name}")
                print(f"Position ID: {position_id}, Position Name: {position_name}")
                print(f"From: {from_time}, To: {to_time}, From Period: {from_period}, To Period: {to_period}")
                print(f"Start Reason: {start_reason}, End Reason: {end_reason}")
                print(f"Cards: {cards}")
                print('\n')

def load_matches(file_path):
    '''Load match data from a JSON file into the database.'''
    data = load_json(file_path) 
    for entry in data:
        match_id = entry['match_id']
        match_date = entry['match_date']
        kick_off = entry['kick_off']
        home_score = entry['home_score']
        away_score = entry['away_score']
        match_status = entry['match_status']
        match_status_360 = entry['match_status_360']
        last_updated = entry['last_updated']
        last_updated_360 = entry['last_updated_360']
        match_week = entry['match_week']

        # Extracting data from nested dictionaries
        competition_id = entry['competition']['competition_id']
        competition_name = entry['competition']['competition_name']
        season_id = entry['season']['season_id']
        season_name = entry['season']['season_name']

        home_team_id = entry['home_team']['home_team_id']
        home_team_name = entry['home_team']['home_team_name']

        away_team_id = entry['away_team']['away_team_id']
        away_team_name = entry['away_team']['away_team_name']

        competition_stage_id = entry['competition_stage']['id']
        competition_stage_name = entry['competition_stage']['name']

        stadium_id = entry['stadium']['id']
        stadium_name = entry['stadium']['name']

        referee_id = entry['referee']['id']
        referee_name = entry['referee']['name']

        # Handling managers, which is a list of dictionaries
        home_team_managers = entry['home_team']['managers']
        away_team_managers = entry['away_team']['managers']

        # Print extracted data for debugging
        print(f"Match ID: {match_id}, Match Date: {match_date}, Kick Off: {kick_off}")
        print(f"Home Score: {home_score}, Away Score: {away_score}, Match Status: {match_status}")
        print(f"Competition ID: {competition_id}, Season ID: {season_id}")
        print(f"Home Team: {home_team_id} - {home_team_name}, Away Team: {away_team_id} - {away_team_name}")
        print(f"Stadium: {stadium_id} - {stadium_name}, Referee: {referee_id} - {referee_name}")
        print(f"Home Team Managers: {home_team_managers}, Away Team Managers: {away_team_managers}")
        print('\n')


def load_three_sixty(file_path):
    '''Load three-sixty data from a JSON file into the database.'''
    data = load_json(file_path) 
    for entry in data:
        event_uuid = entry['event_uuid']
        visible_area = entry['visible_area']  # This is a list representing a polygon
        freeze_frame = entry['freeze_frame']  # This is a list of dictionaries

        # Print the basic data
        print(f"Event UUID: {event_uuid}")
        print(f"Visible Area Coordinates: {visible_area}")

        # Process each freeze frame entry
        for ff in freeze_frame:
            teammate = ff['teammate']
            actor = ff['actor']
            keeper = ff['keeper']
            location = ff['location']

            # Print or process these details
            print(f"Teammate: {teammate}, Actor: {actor}, Keeper: {keeper}, Location: {location}")
         
        print('\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', choices=['competitions','events','lineups','matches','three-sixty', 'all'])
    args = parser.parse_args()
    choice = args.dataset
    conn = connect_db()

    if choice == 'competitions':
        paths = get_file_paths(choice)
        load_competitions(paths[0], conn)

    elif choice == 'events':
        paths = get_file_paths(choice)
        load_events(paths[0], conn)

    elif choice == 'lineups':
        paths = get_file_paths(choice)
        load_lineups(paths[0], conn)

    elif choice == 'matches':
        paths = get_file_paths(choice)
        load_matches(paths[0], conn)

    elif choice == 'three-sixty':
        paths = get_file_paths(choice)
        load_three_sixty(paths[0], conn)

    else:
        # TODO: Add desired run ordering
        pass

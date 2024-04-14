#! /usr/bin/python3

import argparse
from glob import glob
import json
import uuid
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

# TODO:
# Currently, there is a country "Europe" which was not found in the matches
# Also, this currently does not actully update the DB, it just inserts.
# It should check if the compettion_id exists first, and update if so

def load_competitions(file_path, conn, test):
    '''Load competition data from a JSON file into the database.'''
    data = load_json(file_path) 

    # SQL to get country_id from country_name
    country_id_sql = "SELECT country_id FROM country WHERE country_name = %s;"

    # SQL to insert data into the competition table
    insert_sql = ''' 
    INSERT INTO competition (competition_id, competition_name, competition_gender, competition_youth, competition_international, season_id, country_id) 
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (competition_id) DO NOTHING;
    '''

    with conn.cursor() as cur:
        for entry in data:
            competition_id = entry['competition_id']
            season_id = entry['season_id']
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
                competition_name,
                competition_gender,
                competition_youth,
                competition_international,
                season_id,
                country_id
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

def load_events(file_path, conn, test):
    '''Load event data from a JSON file into the database.'''
    data = load_json(file_path) 

    '''
    events_sql = 
    INSERT INTO events (event_id, match_id, event_index, period, timestamp, minute, second, event_type_id, possession, possession_team_id, play_pattern_id, team_id, location, duration, off_camera, under_pressure, counterpress, out)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    events_sql = '''
    INSERT INTO events (event_id, match_id, event_index, period, timestamp, minute, second, possession, possession_team_id, team_id, location, duration, off_camera, under_pressure, counterpress, out)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''

    shot_sql = '''
    INSERT INTO shot (event_id, statsbomb_xg, first_time)
    VALUES (%s, %s, %s)
    '''

    # Extract match_id from filename (assuming file_path like '.../1234.json')
    match_id = int(os.path.splitext(os.path.basename(file_path))[0])

    with conn.cursor() as cur:
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

            # Convert 'location' if exists and is a list of two floats
            location = tuple(entry['location']) if 'location' in entry and len(entry['location']) == 2 else None
            duration = entry.get('duration')
            
            # Extracting data from nested 'play_pattern' dictionary
            play_pattern_id = entry['play_pattern']['id']
            play_pattern_name = entry['play_pattern']['name']
            
            # Extracting data from nested 'team' dictionary
            team_id = entry['team']['id']
            team_name = entry['team']['name']
            
            # Handling potentially missing 'related_events' key
            related_events = entry.get('related_events', [])

            off_camera = entry.get('off_camera', False)
            under_pressure = entry.get('under_pressure', False)
            counterpress = entry.get('counterpress', False)
            out = entry.get('out', False)

            recipient_id, length, angle, height_id, end_location, body_part_id, type_id = None, None, None, None, None, None, None
            # TODO: Extract passes
            if hasattr(entry, 'pass'):
                if entry['pass'] is not None:
                   pass 

            # TODO: Extract shots (xG scores, outcomes etc.)
            statsbomb_xg, first_time = None, None 
            if hasattr(entry, 'shot'):
                if entry['shot'] is not None:
                    statsbomb_xg = entry['shot']['statsbomb_xg']
                    first_time = entry['shot']['first_time']
                    
            

            # TODO: Extract dribbles
            if hasattr(entry, 'dribble'):
                if entry['dribble'] is not None:
                    pass

            # Print extracted data for debugging
            print(f"Event ID: {event_id}, Index: {index}, Period: {period}, Timestamp: {timestamp}")
            print(f"Minute: {minute}, Second: {second}, Event Type: {event_type_id} - {event_type_name}")
            print(f"Possession: {possession}, Possession Team: {possession_team_id} - {possession_team_name}")
            print(f"Play Pattern: {play_pattern_id} - {play_pattern_name}, Team: {team_id} - {team_name}")
            print(f"Related Events: {related_events}") 
            print(f"Location: {location}, Duration: {duration}")
            print(f"Off Camera: {off_camera}, Under Pressure: {under_pressure}, Counterpress: {counterpress}, Out: {out}")
            print('\n')

            cur.execute(events_sql, (event_id, match_id, index, period, timestamp, minute, second, possession, possession_team_id, team_id, location, duration, off_camera, under_pressure, counterpress, out))
            if statsbomb_xg is not None:
                cur.execute(shot_sql, (event_id, statsbomb_xg, first_time)) 
        conn.commit()

def load_lineups(file_path, conn, test):
    '''Load lineup data from a JSON file into the database.'''

    data = load_json(file_path) 

    team_sql_query = ''' 
    INSERT INTO team (team_id, team_name) VALUES (%s, %s)
    ON CONFLICT (team_id) DO NOTHING;
    '''
    country_sql_query = ''' 
    INSERT INTO country (country_id, country_name) VALUES (%s, %s)
    ON CONFLICT (country_id) DO NOTHING;
    '''
    player_sql_query = ''' 
    INSERT INTO player (player_id, player_name, player_nickname, jersey_number, country_id) VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (player_id) DO NOTHING;
    '''
    position_event_sql_query = ''' 
    INSERT INTO position_event (event_id, position_id, start_reason, end_reason, from_time, to_time, from_period, to_period) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (event_id, position_id) DO NOTHING;
    '''

    event_sql_query = '''
    INSERT INTO events (event_id, match_id, event_type_id, timestamp)
    VALUES (%s, %s, %s, '00:00:00')
    RETURNING event_id;
    '''
    
    # Extract match_id from filename (assuming file_path like '.../1234.json')
    match_id = int(os.path.splitext(os.path.basename(file_path))[0])

    global pseudo_event_type_id 

    with conn.cursor() as cur:
        for entry in data:
            team_id = entry['team_id']
            team_name = entry['team_name']
            lineup = entry['lineup']
            
            for player in lineup:
                player_id = player['player_id']
                player_name = player['player_name']
                player_nickname = player['player_nickname'] if player['player_nickname'] else None
                jersey_number = player['jersey_number']

                country_id, country_name = None, None
                if hasattr(player, 'country'):
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

            # Print extracted data for debugging
            print(f"Team ID: {team_id}, Team Name: {team_name}")
            print(f"Player ID: {player_id}, Player Name: {player_name}, Nickname: {player_nickname}, Jersey Number: {jersey_number}")
            print(f"Country ID: {country_id}, Country Name: {country_name}")
            print(f"Position ID: {position_id}, Position Name: {position_name}")
            print(f"From: {from_time}, To: {to_time}, From Period: {from_period}, To Period: {to_period}")
            print(f"Start Reason: {start_reason}, End Reason: {end_reason}")
            print(f"Cards: {cards}")
            print('\n')

            event_id = uuid.uuid4()
            # Insert a pseudo-event for the lineup
            cur.execute(event_sql_query, (event_id, match_id, pseudo_event_type_id))
            pseudo_event_id = cur.fetchone()[0] # Fetch the created event_id

            # Insert team
            cur.execute(team_sql_query, (team_id, team_name))

            # Insert country
            if country_id is not None:
                cur.execute(country_sql_query, (country_id, country_name))

            # Insert player
            cur.execute(player_sql_query, (player_id, player_name, player_nickname, jersey_number, country_id))
            # Insert or update position information related to this event (player in lineup)
            #cur.execute(position_event_sql_query, (pseudo_event_id, player_id, position_id, start_reason, end_reason, from_time, to_time, from_period, to_period))

    conn.commit()


def load_matches(file_path, conn, test):
    '''Load match data from a JSON file into the database.'''
    data = load_json(file_path) 

    match_sql = '''
    INSERT INTO match (match_id, match_date, home_team_id, away_team_id, home_score, away_score, competition_id, season_id, stadium_id, referee_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (match_id) DO NOTHING;
    '''
    season_sql = '''
    INSERT INTO season (season_id, season_name)
    VALUES (%s, %s)
    ON CONFLICT (season_id) DO NOTHING;
    '''
    country_sql = '''
    INSERT INTO country (country_id, country_name)
    VALUES (%s, %s)
    ON CONFLICT (country_id) DO NOTHING;
    '''
    team_sql = '''
    INSERT INTO team (team_id, team_name, team_gender, country_id)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (team_id) DO NOTHING;
    '''
    stadium_sql = '''
    INSERT INTO stadium (stadium_id, name, country_id)
    VALUES (%s, %s, %s)
    ON CONFLICT (stadium_id) DO NOTHING;
    '''
    referee_sql = '''
    INSERT INTO referee (referee_id, name, country_id)
    VALUES (%s, %s, %s)
    ON CONFLICT (referee_id) DO NOTHING;
    '''
    comp_stage_sql = '''
    INSERT INTO competition_stage (stage_id, name)
    VALUES (%s, %s)
    ON CONFLICT (stage_id) DO NOTHING;
    '''
    comp_sql = ''' 
    INSERT INTO competition (competition_id, competition_name, season_id, country_id)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (competition_id) DO NOTHING;
    '''

    with conn.cursor() as cur:
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

            # Extracting data for populating a minimal entry for competition
            competition_id, competition_name, competition_country_name = None, None, None
            if hasattr(entry, 'competition'):
                competition_id = entry['competition']['competition_id']
                competition_name = entry['competition']['competition_name']
                competition_country_name = entry['competition']['country_name']

            season_id = entry['season']['season_id']
            season_name = entry['season']['season_name']

            # This filters for a subset of the seasons and competitions of desired focus for this project.
            if test:
                #if competition_name == 'La Liga' and season_name in ['2020/2021', '2019/2020', '2018/2019']:
                if season_name in ['2020/2021', '2019/2020', '2018/2019']:
                    pass
                #elif competition_name == 'Premier League' and season_name in ['2003/2004']:
                elif season_name in ['2003/2004']:
                    pass
                else:
                    continue

            home_team_id = entry['home_team']['home_team_id']
            home_team_name = entry['home_team']['home_team_name']
            home_team_gender = entry['home_team']['home_team_gender']
            home_country = entry['home_team']['country']

            away_team_id = entry['away_team']['away_team_id']
            away_team_name = entry['away_team']['away_team_name']
            away_team_gender = entry['away_team']['away_team_gender']
            away_country = entry['away_team']['country']

            competition_stage_id = entry['competition_stage']['id']
            competition_stage_name = entry['competition_stage']['name']

            # Certain entries don't have stadium attributes
            stadium_id, stadium_name, stadium_country = None, None, None
            if hasattr(entry, 'stadium'):
                stadium_id = entry['stadium']['id']
                stadium_name = entry['stadium']['name']
                stadium_country = entry['stadium']['country']

            # Certain entries don't have referee attributes
            referee_id, referee_name, referee_country = None, None, None
            if hasattr(entry, 'referee'):
                referee_id = entry['referee']['id']
                referee_name = entry['referee']['name']
                referee_country = entry['referee']['country']

            # Handling managers, which is a list of dictionaries
            #home_team_managers = entry['home_team']['managers']
            #away_team_managers = entry['away_team']['managers']

            # Print extracted data for debugging
            print(f"Match ID: {match_id}, Match Date: {match_date}, Kick Off: {kick_off}")
            print(f"Home Score: {home_score}, Away Score: {away_score}, Match Status: {match_status}")
            print(f"Competition ID: {competition_id}, Season ID: {season_id}")
            print(f"Home Team: {home_team_id} - {home_team_name}, Away Team: {away_team_id} - {away_team_name}")
            print(f"Stadium: {stadium_id} - {stadium_name}, Referee: {referee_id} - {referee_name}")
            #print(f"Home Team Managers: {home_team_managers}, Away Team Managers: {away_team_managers}")
            print('\n')

            #Inserting Season
            cur.execute(season_sql, (season_id, season_name))

            # Inserting countries
            all_countries = [away_country, home_country]
            if referee_id is not None:
                all_countries.append(referee_country)
            if stadium_id is not None:
                all_countries.append(stadium_country)

            for c in all_countries:
                cur.execute(country_sql, (c['id'], c['name']))

            # Check to see if the competition country matches any present country
            competition_country_id = None
            for c in all_countries:
                if c['name'] == competition_country_name:
                    competition_country_id = c['id']

            if competition_id is None:
                pass # Skip inserting as this match doesn't have a competition linked
            elif competition_country_id is None:
                print(f'Error: Cannot insert competition {competition_name} as its country {competition_country_name} is not the same as any of the current match object countries')
            else:
                # We now can insert into the competition table
                cur.execute(comp_sql, (competition_id, competition_name, season_id, competition_country_id))

            # Let's hope that the competition already existed in the DB if the above clause fails...

            # Inserting teams
            cur.execute(team_sql, (home_team_id, home_team_name, home_team_gender, home_country['id']))
            cur.execute(team_sql, (away_team_id, away_team_name, away_team_gender, away_country['id']))

            # Inserting stadium
            if stadium_id is not None:
                cur.execute(stadium_sql,  (stadium_id, stadium_name, stadium_country['id']))

            # Inserting referee
            if referee_id is not None:
                cur.execute(referee_sql,  (referee_id, referee_name, referee_country['id']))

            # Inserting competition stage

            # Leaving omitted for now; don't need it for our usecase.
            #cur.execute(comp_stage_sql (competition_stage_id, competition_stage_name))

            # Also omitting adding managers for now.


            # Inserting match
            cur.execute(match_sql, (match_id, match_date, home_team_id, away_team_id, home_score, away_score, competition_id, season_id, stadium_id, referee_id))

        conn.commit()

def load_three_sixty(file_path, conn):
    '''Load three-sixty data from a JSON file into the database.'''
    data = load_json(file_path) 

    three_sixty_sql = '''
    INSERT INTO three_sixty (event_uuid, visible_area)
    VALUES (%s, %s)
    '''
    freeze_frame_sql = '''
    INSERT INTO freeze_frames (event_uuid, teammate, actor, keeper, location)
    VALUES (%s, %s, %s, %s, POINT(%s, %s))
    '''
    with conn.cursor() as cur:
        for entry in data:
            event_uuid = entry['event_uuid']
            visible_area = entry['visible_area']  # This is a list representing a polygon
            freeze_frame = entry['freeze_frame']  # This is a list of dictionaries

            # Print the basic data
            print(f"Event UUID: {event_uuid}")
            print(f"Visible Area Coordinates: {visible_area}")

            # Skip polygons which do not contain pairs of coordinates
            if len(visible_area) % 2 != 0:
                break
            # Convert list to a PostgreSQL polygon format
            polygon_format = ','.join(f'{visible_area[i]} {visible_area[i+1]}' for i in range(0, len(visible_area), 2))
            polygon_value = f'POLYGON(({polygon_format}))'
            cur.execute(three_sixty_sql, (event_uuid, polygon_value))

            # Process each freeze frame entry
            for ff in freeze_frame:
                teammate = ff['teammate']
                actor = ff['actor']
                keeper = ff['keeper']
                location = ff['location']

                # Print or process these details
                print(f"Teammate: {teammate}, Actor: {actor}, Keeper: {keeper}, Location: {location}")

                cur.execute(freeze_frame_sql, (event_uuid, teammate, actor, keeper, location))

            print('\n')

    conn.commit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', default = 'all', choices=['competitions','events','lineups','matches','three-sixty', 'all'])
    parser.add_argument('--test', default = True, type = bool)
    args = parser.parse_args()
    choice = args.dataset
    conn = connect_db()

    # Attempt to insert the generic event if it does not exist
    insert_pseudo_event_sql = ''' 
    INSERT INTO event_type (name)
    SELECT 'Lineup Setup'
    WHERE NOT EXISTS (
        SELECT 1 FROM event_type WHERE name = 'Lineup Setup'
    );
    ''' 
    get_pseudo_event_id_sql = ''' 
    SELECT event_type_id FROM event_type WHERE name = 'Lineup Setup';
    '''
    with conn.cursor() as cur:
        cur.execute(insert_pseudo_event_sql)
        conn.commit()  # Commit any changes if the insert has occurred

        # Retrieve the ID of 'Lineup Setup', whether it was just inserted or already existed
        cur.execute(get_pseudo_event_id_sql)
        pseudo_event_type_id = cur.fetchone()[0]  # fetchone() returns a tuple, and we need the first element

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
        '''
        # First, populate from the matches dataset
        match_paths = get_file_paths('matches')
        for p in match_paths:
            load_matches(p, conn, False)
        # Next, populate from the compettions dataset
        competition_paths = get_file_paths('competitions')
        for p in competition_paths:
            load_competitions(p, conn, args.test)
        # Then, populate from the lineups dataset.
        lineup_paths = get_file_paths('lineups')
        for p in lineup_paths:
            load_lineups(p, conn, args.test)
                
        '''
        # Finally, populate the events dataset (we skip the three-sixty for our usecase)
        events_paths = get_file_paths('events')
        for p in events_paths:
           load_events(p, conn, args.test)
         

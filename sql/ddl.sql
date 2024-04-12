-- TODO:
-- Review tables to ensure they have appropriate constraints for data integrity (e.g. NOT NULL and CHECK)
-- Determine which fields are most frequently accessed, and create indexes for them.

CREATE TABLE country (
    country_id SERIAL PRIMARY KEY,
    country_name VARCHAR(64) NOT NULL UNIQUE
);

CREATE TABLE season (
    season_id SERIAL PRIMARY KEY,
    season_name VARCHAR(16) NOT NULL UNIQUE
);

-- Beta version
CREATE TABLE competition (
    competition_id SERIAL PRIMARY KEY,
    competition_name VARCHAR(32) NOT NULL,
    competition_gender VARCHAR(16) NOT NULL,
    competition_youth BOOLEAN,
    competition_international BOOLEAN,
    season_id INT,
    country_id INT,
    FOREIGN KEY(season_id) REFERENCES season(season_id),
    FOREIGN KEY(country_id) REFERENCES country(country_id)
);

CREATE TABLE manager (
    manager_id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    nickname VARCHAR(64),
    dob DATE,
    country_id INT,
    FOREIGN KEY(country_id) REFERENCES country(country_id)
);

CREATE TABLE player (
    player_id SERIAL PRIMARY KEY,
    player_name VARCHAR(64) NOT NULL,
    player_nickname  VARCHAR(64),
    jersey_number SMALLINT NOT NULL,
    country_id INT,
    FOREIGN KEY(country_id) REFERENCES country(country_id)
);

CREATE TABLE referee (
    referee_id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    country_id INT,
    FOREIGN KEY(country_id) REFERENCES country(country_id)
);

-- Beta verion
-- The structure of this is subject to change based on the following conditions:
-- If I iterate over the match dataset first, or if it contains references to all the teams, I'll likely keep it as is.
-- If I iterate first over the lineup or events, I might change this and only populate `team_id` and `team_name`
CREATE TABLE team (
    team_id SERIAL PRIMARY KEY,
    team_name VARCHAR(32) NOT NULL,
    team_gender VARCHAR(16) NOT NULL,
    country_id INT,
    FOREIGN KEY(country_id) REFERENCES country(country_id)
);

CREATE TABLE position (
    position_id SERIAL PRIMARY KEY,
		position_name VARCHAR(32) NOT NULL UNIQUE,	
);

-- start_reason and end_reason seems like they should be foreign keys
CREATE TABLE position_event (
		event_id UUID,
		position_id INT,
    start_reason VARCHAR(32),
    end_reason VARCHAR(32),
    to_time TIME,
    from_time TIME,
    to_period INT,
    from_period INT,
		FOREIGN KEY(event_id) REFERENCES events(event_id),
		FOREIGN KEY(posiiton_id) REFERENCES position(position_id)
);

-- Reason seems like something which should be a foreign key
CREATE TABLE cards (
  card_id SERIAL PRIMARY KEY,
	event_id UUID,
	time TIME,
  card_type VARCHAR(32) NOT NULL UNIQUE
	reason VARCHAR(64),
	period INT,
	FOREIGN KEY(event_id) REFERENCES events(event_id)
);

CREATE TABLE competition_stage (
  stage_id SERIAL PRIMARY KEY,
  name VARCHAR(32) NOT NULL UNIQUE
);

-- Unfinished
CREATE TABLE stadium (
  stadium_id SERIAL PRIMARY KEY,
  name VARCHAR(64) NOT NULL,
  country_id INT,
  FOREIGN KEY(country_id) REFERENCES country(country_id)
);

CREATE TABLE play_pattern (
  pattern_id SERIAL PRIMARY KEY,
  name VARCHAR(64) NOT NULL,
);

CREATE TABLE pass (
  event_id UUID PRIMARY KEY,
  recipient_id INT,
  length FLOAT,
  angle FLOAT,
  height_id INT,
  end_location POINT,
  body_part_id INT,
  type_id INT,
  FOREIGN KEY(event_id) REFERENCES events(event_id),
  FOREIGN KEY(recipient_id) REFERENCES player(player_id),
  FOREIGN KEY(height_id) REFERENCES height(height_id),
  FOREIGN KEY(body_part_id) REFERENCES body_part(body_part_id),
  FOREIGN KEY(type_id) REFERENCES pass_type(pass_type_id)
);

CREATE TABLE shot (
    event_id UUID PRIMARY KEY,
    end_location POINT,
    outcome_id INT,
    technique_id INT,
    body_part_id INT,
    type_id INT,
    statsbomb_xg FLOAT,
    FOREIGN KEY(event_id) REFERENCES events(event_id),
    FOREIGN KEY(outcome_id) REFERENCES outcome(outcome_id),
    FOREIGN KEY(technique_id) REFERENCES technique(technique_id),
    FOREIGN KEY(body_part_id) REFERENCES body_part(body_part_id),
    FOREIGN KEY(type_id) REFERENCES shot_type(shot_type_id)
);

CREATE TABLE carry (
    event_id UUID PRIMARY KEY,
    end_location POINT,
    FOREIGN KEY(event_id) REFERENCES events(event_id)
);

CREATE TABLE dribble (
    event_id UUID PRIMARY KEY,
    outcome_id INT,
    FOREIGN KEY(event_id) REFERENCES events(event_id),
    FOREIGN KEY(outcome_id) REFERENCES outcome(outcome_id)
);

CREATE TABLE ball_recovery (
    event_id UUID PRIMARY KEY,
    recovery_failure BOOLEAN,
    FOREIGN KEY(event_id) REFERENCES events(event_id)
);

CREATE TABLE clearance (
    event_id UUID PRIMARY KEY,
    body_part_id INT,
    right_foot BOOLEAN,
    FOREIGN KEY(event_id) REFERENCES events(event_id),
    FOREIGN KEY(body_part_id) REFERENCES body_part(body_part_id)
);

CREATE TABLE foul_committed (
    event_id UUID PRIMARY KEY,
    card_id INT,
    FOREIGN KEY(event_id) REFERENCES events(event_id),
    FOREIGN KEY(card_id) REFERENCES card(card_id)
);

CREATE TABLE substitution (
    event_id UUID PRIMARY KEY,
    replacement_id INT,
    outcome_id INT,
    FOREIGN KEY(event_id) REFERENCES events(event_id),
    FOREIGN KEY(replacement_id) REFERENCES player(player_id),
    FOREIGN KEY(outcome_id) REFERENCES outcome(outcome_id)
);

CREATE TABLE foul_won (
    event_id UUID PRIMARY KEY,
    defensive BOOLEAN,
    FOREIGN KEY(event_id) REFERENCES events(event_id)
);

CREATE TABLE interception (
    event_id UUID PRIMARY KEY,
    outcome_id INT,
    FOREIGN KEY(event_id) REFERENCES events(event_id),
    FOREIGN KEY(outcome_id) REFERENCES outcome(outcome_id)
);

CREATE TABLE block (
    event_id UUID PRIMARY KEY,
    deflection BOOLEAN,
    FOREIGN KEY(event_id) REFERENCES events(event_id)
);

CREATE TABLE tackle (
    event_id UUID PRIMARY KEY,
    type_id INT,
    outcome_id INT,
    FOREIGN KEY(event_id) REFERENCES events(event_id),
    FOREIGN KEY(type_id) REFERENCES tackle_type(tackle_type_id),
    FOREIGN KEY(outcome_id) REFERENCES outcome(outcome_id)
);

CREATE TABLE ball_receipt (
    event_id UUID PRIMARY KEY,
    outcome_id INT,
    FOREIGN KEY(event_id) REFERENCES events(event_id),
    FOREIGN KEY(outcome_id) REFERENCES outcome(outcome_id)
);

CREATE TABLE goalkeeper_action (
    event_id UUID PRIMARY KEY,
    outcome_id INT,
    technique_id INT,
    type_id INT,
    FOREIGN KEY(event_id) REFERENCES events(event_id),
    FOREIGN KEY(outcome_id) REFERENCES outcome(outcome_id),
    FOREIGN KEY(technique_id) REFERENCES technique(technique_id),
    FOREIGN KEY(type_id) REFERENCES goalkeeper_action_type(goalkeeper_action_type_id)
);

CREATE TABLE bad_behaviour (
    event_id UUID PRIMARY KEY,
    card_id INT,
    FOREIGN KEY(event_id) REFERENCES events(event_id),
    FOREIGN KEY(card_id) REFERENCES card(card_id)
);

CREATE TABLE off_camera (
    event_id UUID PRIMARY KEY,
    is_off_camera BOOLEAN,
    FOREIGN KEY(event_id) REFERENCES events(event_id)
);

CREATE TABLE under_pressure (
    event_id UUID PRIMARY KEY,
    is_under_pressure BOOLEAN,
    FOREIGN KEY(event_id) REFERENCES events(event_id)
);

CREATE TABLE counterpress (
    event_id UUID PRIMARY KEY,
    is_counterpress BOOLEAN,
    FOREIGN KEY(event_id) REFERENCES events(event_id)
);

-- Unfinished
CREATE TABLE events (
    event_id UUID PRIMARY KEY,
    match_id INT,
    event_index INT,
    period INT,
    timestamp TIME,
    minute INT,
    second INT,
    event_type_id INT,
    possession INT,
    possession_team_id INT,
    play_pattern_id INT,
    team_id INT,
    player_id INT,
    position_id INT,
    location POINT,
    duration FLOAT,
    off_camera BOOLEAN,
    under_pressure BOOLEAN,
    counterpress BOOLEAN,
    out BOOLEAN,
    FOREIGN KEY(match_id) REFERENCES match(match_id),
    FOREIGN KEY(event_type_id) REFERENCES event_type(event_type_id),
    FOREIGN KEY(possession_team_id) REFERENCES team(team_id),
    FOREIGN KEY(play_pattern_id) REFERENCES play_pattern(play_pattern_id),
    FOREIGN KEY(team_id) REFERENCES team(team_id),
    FOREIGN KEY(player_id) REFERENCES player(player_id),
    FOREIGN KEY(position_id) REFERENCES position(position_id)
);

-- Unfinished
-- Ensure formation and line-up types are appropriate
CREATE TABLE tactics (
    tactics_id SERIAL PRIMARY KEY,
    event_id INT,
    formation VARCHAR(32),
    lineup_type VARCHAR(32),
    FOREIGN KEY(event_id) REFERENCES events(event_id)
);

-- Partially unfinished
-- There are a number of attributes this version currently doesn't support
-- E.g. match_status, kick_off, competition_stage, ...
CREATE TABLE match (
    match_id SERIAL PRIMARY KEY,
    home_team_id INT,
    away_team_id INT,
    home_score INT,
    away_score INT,
    competition_id INT,
    season_id INT,
    stadium_id INT,
    referee_id INT,
    match_date DATE,
    FOREIGN KEY(stadium_id) REFERENCES stadium(stadium_id),
    FOREIGN KEY(home_team_id) REFERENCES team(team_id),
    FOREIGN KEY(away_team_id) REFERENCES team(team_id),
    FOREIGN KEY(competition_id) REFERENCES competition(competition_id),
    FOREIGN KEY(season_id) REFERENCES season(season_id),
    FOREIGN KEY(referee_id) REFERENCES referee(referee_id)
);

-- Partially finished
-- This works both for data from the `lineups` files, and from events
-- This also does not line players to cards with respect to the lineup
-- Think about how substitutions affect lineups and whether need to track changes in lineup during match (besides effective time)
CREATE TABLE lineup (
    lineup_id SERIAL PRIMARY KEY,
    match_id INT,
    team_id INT,
    player_id INT,
    position_id INT,
    effective_time TIME,
    FOREIGN KEY(match_id) REFERENCES match(match_id),
    FOREIGN KEY(team_id) REFERENCES team(team_id),
    FOREIGN KEY(player_id) REFERENCES player(player_id),
    FOREIGN KEY(position_id) REFERENCES position(position_id)
);

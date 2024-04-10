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
    position__name VARCHAR(32) NOT NULL UNIQUE,
    start_reason VARCHAR(32),
    end_reason VARCHAR(32),
    to_time TIME,
    from_time TIME,
    to_period INT,
    from_period INT
);

-- Unfinished. A couple notes on what might come:
-- 1) There is a `reason` field, as well as a `period` reference.
-- 2) There also a `time` attribute. This seems important as it will link it with events
-- 3) There doesn't seem to be a card_id attribute in the actual dataset. This might be something which just auto iterates?
CREATE TABLE cards (
  card_id SERIAL PRIMARY KEY,
  name VARCHAR(32) NOT NULL UNIQUE
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

-- Unfinished
CREATE TABLE event (
  event_id SERIAL PRIMARY KEY
);

-- Unfinished
CREATE TABLE match (
    match_id SERIAL PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email TEXT NOT NULL UNIQUE,
    match_date DATE,
    stadium_id INT,
    FOREIGN KEY(stadium_id) REFERENCES stadium(stadium_id)
);

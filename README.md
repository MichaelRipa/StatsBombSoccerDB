# StatsBombSoccerDB

This repository contains the implementation of a PostgreSQL database for storing and querying soccer event data, as part of a course project. The data schema and loading scripts are tailored to manage and analyze detailed soccer match events provided by StatsBomb.

## Repository Structure
- `sql/`: Contains the `ddl.sql` script for initializing the database schema.
- `json_loader/`: Includes scripts for loading data into the database:
    - `config.py`: Configuration file for PostgreSQL database connection settings and data path.
    - `load_data.py`: Script to load JSON data into the PostgreSQL database.
- `dbexport.sql`: An export of the database, which includes some sample loaded data.
- `queries.py`: Python script that runs specific SQL queries on the database and outputs the results.

## Data Source

The dataset used in this project is taken from StatsBomb's open data, specifically from their [GitHub repository](https://github.com/statsbomb/open-data/tree/0067cae166a56aa80b2ef18f61e16158d6a7359a). The data is structured as JSON files, typically used in document databases, but here it has been adapted for use in a relational database.

## Getting Started

### Prerequisites
- **PostgreSQL**: Make sure you have PostgreSQL installed on your system. You can download it from [here](https://www.postgresql.org/download/).
- **Python**: This project uses Python scripts for loading data and running queries. Ensure you have Python installed.

### Setting Up the Database
1. **Initialize the Database Schema**

Navigate to the `sql/` directory and run the `ddl.sql` file against your PostgreSQL database to set up the necessary tables and relationships:

`psql -U <username> -d <database_name> -a -f ddl.sql`

2. **Configure the Database Connection**
Edit the `config.py` file in the `json_loader/` directory with your PostgreSQL database settings.

### Loading the Data
After configuring the connection, run the `load_data.py` script to import the JSON data into the database:

`python json_loader/load_data.py`

### Running Queries
Execute the `queries.py` script to run predefined SQL queries on the loaded data:

`python queries.py`

## Example Data

The `dbexport.sql` file in the repository is an example of how the database looks once data is loaded. You can import this file into your PostgreSQL instance to quickly set up a pre-populated database.

## Contributing
While this project was initially created for a course, contributions to improve the code or extend the functionality are welcome.

#! /usr/bin/env python3
# source venv_wsl/bin/activate
#------------------------------------------------------------------------------
# File: main.py
# Description: Main application file for the Conference Management System.
# This file contains the implementation of the Data Access Objects (DAOs) for both Neo4j and MySQL databases
# as well as the Menu class to interact
#------------------------------------------------------------------------------


#-------------------------------------------------------------------------------
# Development Enviroment Details
#-------------------------------------------------------------------------------
# VSCode Remote WSL Ubuntu - this supports pexpect and ATU test enviroment
# Python 3.12.3
# pymysql
# neo4j
# AI assistant github copilot pro 
# Only AI Completion was used for this project , DAO and menu class was based webpage design course this semester.

#source venv_wsl/bin/activate

#------------------------------------------------------------------------------
# Design
#-------------------------------------------------------------------------------
# 0. The database connectivity and functionality is implemented in the DAO classes
# 1. The menu functions are implemented in the Menu class, which interacts with the DAO classes to perform the necessary database operations
# 2. The main function initializes the DAO classes and the Menu class, and then starts the menu loop to interact with the user
# 2.1 Menu consists of visable project specific options
# 2.2 Menu also consists of hidden options to reset the databases, which are used for testing purposes
#---------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------
# Return codes and error handling
# All thrown error will use the same format 
# *** ERROR *** (<error code>, "<error message>")
#------------------------------------------------------------------------------
# MYSQL
# -----
# Autocommit mode is enabled : https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlconnection-autocommit.html
#     This means that each query is committed immediately after it is executed, so there is no need
#     Author - This equivalent to BTET mode in Teradata 
# Cursor class is set to DictCursor : https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-dictcursor.html
#     This means that the results of queries will be returned as dictionaries
#     Author - as per lecture notes  
# NEO4J
# TBD
#------------------------------------------------------------------------------
import logging
import subprocess
import sys
import argparse
import datetime
from typing import Any, Optional, Tuple


# Global 
mysql_reset_file = "appdbproj.sql"
neo4j_reset_file = "dev_neo4j.cypher"

# TODO 
# 1. When adding attendee ensure that it is added in neo4j as well as mysql, and that the connection is created in neo4j for the new attendee and any existing attendees that are connected to it in mysql
# 2. When deleting attendee ensure that it is deleted in neo4j as well as mysql, and that any connections in neo4j are also deleted for the attendee
# 3. Improve error handling and logging throughout the code, especially in the DAO classes and menu functions
# 4. Add more detailed logging for debugging purposes, especially in the DAO classes and menu
# Install the mysql-connector-python package if it's not already installed
try:
    #import mysql.connector as mysql
    import pymysql as mysql
except ImportError:
    # Try to install the mysql-connector-python package if it's not already installed
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pymysql"])
    import pymysql as mysql
# Install NEO4J Python driver if it's not already installed
try:
    import neo4j as neo4j
except ImportError:
    # Try to install the neo4j package if it's not already installed
    subprocess.check_call([sys.executable, "-m", "pip", "install", "neo4j"])
    import neo4j as neo4j

#------------------------------------------------------------------------------------------------------
# Data Access Object (DAO) for Neo4j
#------------------------------------------------------------------------------------------------------
class DAO_Neo4j:
    """Data Access Object for Neo4j database.
    This class provides methods to connect to a Neo4j database and execute queries.
    """
#------------------------------------------------------------------------------
# Function: __init__
#------------------------------------------------------------------------------
    def __init__(self, uri, user, password, database="attendeenetwork"):
        self.uri = uri
        self.user = user
        self.password = password
        self.default_password = "neo4j"
        self.database = database
        self.driver = None

#------------------------------------------------------------------------------
# Function: __del__
#------------------------------------------------------------------------------
    def __del__(self):
        """Destructor to ensure the Neo4j connection is closed when the object is destroyed."""
        self.close()

#------------------------------------------------------------------------------
# Function: connect
#------------------------------------------------------------------------------
    def connect(self)-> Tuple[Optional[Any], int, str]:
        """Establish a connection to the Neo4j database."""
        self.driver = None
        try:
            # try logging on with default password first, if it fails then try with the provided password, this is to handle the case where the neo4j database is reset and the password is reset to the default password
            self.driver = neo4j.GraphDatabase.driver(uri = self.uri, 
                                                     auth = (self.user,
                                                              self.default_password),
                                                    database = self.database)
            logging.info(f"Successfully connected to Neo4j database: {self.database} with default password.")
            # try a ping query to ensure the connection is valid, if it fails then try with the provided password
            with self.driver.session() as session:
                session.run("RETURN 1")
            print(f"Successfully connected to Neo4j database: {self.database} with default password.")
        except neo4j.exceptions.Neo4jError as err:
            self.driver = None
            logging.warning(f"Failed to connect to Neo4j database with default password: {err}")
            logging.info(f"Trying to connect to Neo4j database with provided password.")
        try:
            if not self.driver: 
                self.driver = neo4j.GraphDatabase.driver(uri = self.uri, 
                                                     auth = (self.user, 
                                                           self.password), 
                                                    database = self.database)
                logging.info(f"Successfully connected to Neo4j database: {self.database}.")
        except neo4j.exceptions.Neo4jError as err:
            logging.error(f"Error connecting to Neo4j: {err}")
            return None, -1, str(err)
        except Exception as err:
            logging.error(f"Unexpected error connecting to Neo4j: {err}")
            return None, -1, str(err)
        return self.driver, 0, "Connection successful"
#------------------------------------------------------------------------------
# Function: reset_database
# ------------------------------------------------------------------------------
    def reset_database(self)-> Tuple[Optional[Any], int, str]:
        """Reset the Neo4j database using the provided Cypher file."""
        try:

            logging.info(f"Resetting Neo4j database using script: {neo4j_reset_file}")
            # File load did not work as expected, so added the queries directly into the code instead
            # TODO - add the queries to a separate file and load them into the code, and ensure that the file is properly formatted for loading into Neo4j
            self.delete_all_nodes_and_relationships()
            logging.info("Neo4j database reset successfully.")
            self.merge_attendee(101)
            logging.info("Attendee 101 merged successfully.")
            self.merge_attendee(102)
            logging.info("Attendee 102 merged successfully.")
            self.merge_attendee(103)
            logging.info("Attendee 103 merged successfully.")
            self.merge_attendee(104)
            logging.info("Attendee 104 merged successfully.")
            self.merge_attendee(105)
            logging.info("Attendee 105 merged successfully.")
            self.merge_attendee(106)
            logging.info("Attendee 106 merged successfully.")
            self.merge_attendee(107)
            logging.info("Attendee 107 merged successfully.")
            self.merge_attendee(108)
            logging.info("Attendee 108 merged successfully.")
            self.merge_attendee(109)
            logging.info("Attendee 109 merged successfully.")
            self.merge_attendee(110)
            logging.info("Attendee 110 merged successfully.")
            self.merge_attendee(111)
            logging.info("Attendee 111 merged successfully.")
            self.merge_attendee(113)
            logging.info("Attendee 113 merged successfully.")
            self.merge_attendee(114)
            logging.info("Attendee 114 merged successfully.")
            self.merge_attendee(115)
            logging.info("Attendee 115 merged successfully.")
            self.merge_attendee(116)
            logging.info("Attendee 116 merged successfully.")
            self.merge_attendee(117)
            logging.info("Attendee 117 merged successfully.")
            self.merge_attendee(118)
            logging.info("Attendee 118 merged successfully.")
            self.merge_attendee(120)
            logging.info("Attendee 120 merged successfully.")
            self.merge_connection(101, 109)
            logging.info("Connection between 101 and 109 merged successfully.")
            self.merge_connection(101, 107)
            logging.info("Connection between 101 and 107 merged successfully.")
            self.merge_connection(102, 110)
            logging.info("Connection between 102 and 110 merged successfully.")
            self.merge_connection(103, 111)
            logging.info("Connection between 103 and 111 merged successfully.")
            self.merge_connection(104, 120)
            logging.info("Connection between 104 and 120 merged successfully.")
            self.merge_connection(105, 113)
            logging.info("Connection between 105 and 113 merged successfully.")
            self.merge_connection(106, 114)
            logging.info("Connection between 106 and 114 merged successfully.")
            self.merge_connection(107, 115)
            logging.info("Connection between 107 and 115 merged successfully.")
            self.merge_connection(108, 116)
            logging.info("Connection between 108 and 116 merged successfully.")
            self.merge_connection(111, 101)
            logging.info("Connection between 111 and 101 merged successfully.")
            self.merge_connection(106, 103)
            logging.info("Connection between 106 and 103 merged successfully.")
            self.merge_connection(120, 103)
            logging.info("Connection between 120 and 103 merged successfully.")
        except neo4j.exceptions.Neo4jError as err:
            logging.error(f"Error resetting Neo4j database: {err}")
            return None, -1, str(err)
        except Exception as err:
            logging.error(f"Unexpected error resetting Neo4j database: {err}")
            return None, -1, str(err)
        return None, 0, "Database reset successful"
#------------------------------------------------------------------------------
# Function: delete_all_nodes_and_relationships
# ------------------------------------------------------------------------------
    def delete_all_nodes_and_relationships(self) -> Tuple[Optional[Any], int, str]:
        """Delete all nodes and relationships from the Neo4j database."""
        query = "MATCH (n) DETACH DELETE n"
        try:
            self.execute_query(query, None)
            logging.info("All nodes and relationships deleted successfully from Neo4j database.")
            return None, 0, "All nodes and relationships deleted successfully"
        except neo4j.exceptions.Neo4jError as err:
            logging.error(f"Error deleting all nodes and relationships from Neo4j database: {err}")
            return None, -1, str(err)
        except Exception as err:
            logging.error(f"Unexpected error deleting all nodes and relationships from Neo4j database: {err}")
            return None, -1, str(err)
#------------------------------------------------------------------------------
# Function: execute_query
#------------------------------------------------------------------------------
    def execute_query(self, query, parameters=None) -> Tuple[Optional[Any], int, str]:
        """Execute a Cypher query and return the results."""
        if not self.driver:
            logging.error("No Neo4j connection established.")
            return None, -1, "No connection"
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters)
                records = result.data()
                logging.debug(f"Query executed successfully: {query}")
                return records, 0, "Query executed successfully"
        except neo4j.exceptions.Neo4jError as err:
            logging.error(f"Error executing query: {query}")
            if parameters:
                logging.error(f"With parameters: {parameters}")
            else:
                logging.error("No parameters provided for the query.")
            logging.error(f"Error executing query: {err}")
            return None, -1, str(err)
    
#------------------------------------------------------------------------------
# Function: close
#------------------------------------------------------------------------------
    def close(self):
        """Close the connection to the Neo4j database."""
        if self.driver:
            self.driver.close()
            logging.info("Neo4j connection closed.")

    # Merge node if it does not exist
    # used when attendees are created
#------------------------------------------------------------------------------
# Function: merge_attendee
#------------------------------------------------------------------------------
    def merge_attendee(self, attendeeID)-> Tuple[Optional[Any], int, str]:
        """Merge an attendee node in the Neo4j database."""
        query = "MERGE (a:Attendee {AttendeeID: $attendeeID}) RETURN a"
        parameters = {"attendeeID": attendeeID}
        return self.execute_query(query, parameters)
#-------------------------------------------------------------------------------
# Function: get_all_attendees
#-------------------------------------------------------------------------------
    def get_all_attendees(self) -> Tuple[Optional[Any], int, str]:
        """Get all attendees from the Neo4j database."""
        query = "MATCH (a:Attendee) RETURN a.AttendeeID"
        return self.execute_query(query, None)

#------------------------------------------------------------------------------
# Function: merge_connection
#------------------------------------------------------------------------------
    def merge_connection(self, attendeeID1, attendeeID2) -> Tuple[Optional[Any], int, str]:
        """Merge a connection between two attendees in the Neo4j database."""
        query = """
        MATCH (a1:Attendee {AttendeeID: $attendeeID1})
        MATCH (a2:Attendee {AttendeeID: $attendeeID2})
        MERGE (a1)-[:CONNECTED_TO]-(a2)
        RETURN a1, a2
        """
        parameters = {"attendeeID1": attendeeID1, "attendeeID2": attendeeID2}
        if not self.driver:
            logging.error("No Neo4j connection established.")
            return None, -1, "No connection"
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters)
                records = result.data()
                logging.debug(f"Query executed successfully: {query}")
                return records, 0, "Query executed successfully"
        except neo4j.exceptions.Neo4jError as err:
            logging.error(f"Error executing query: {query}")
            if parameters:
                logging.error(f"With parameters: {parameters}")
            else:
                logging.error("No parameters provided for the query.")
            logging.error(f"Error executing query: {err}")
            return None, -1, str(err)
        except Exception as err:
            logging.error(f"Unexpected error executing query: {query}")
            if parameters:
                logging.error(f"With parameters: {parameters}")
            else:
                logging.error("No parameters provided for the query.")
            logging.error(f"Error executing query: {err}")
            return None, -1, str(err)


#------------------------------------------------------------------------------
# Function: delete_connection
#------------------------------------------------------------------------------
    def delete_connection(self, attendeeID1, attendeeID2) -> Tuple[Optional[Any], int, str]:
        """Delete a connection between two attendees from the Neo4j database."""
        query = """
        MATCH (a1:Attendee {AttendeeID: $attendeeID1})-[r:CONNECTED_TO]-(a2:Attendee {AttendeeID: $attendeeID2})
        DELETE r
        """
        parameters = {"attendeeID1": attendeeID1, "attendeeID2": attendeeID2}
        if not self.driver:
            logging.error("No Neo4j connection established.")
            return None, -1, "No connection"
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters)
                records = result.data()
                logging.debug(f"Query executed successfully: {query}")
                return records, 0, "Query executed successfully"
        except neo4j.exceptions.Neo4jError as err:
            logging.error(f"Error executing query: {query}")
            if parameters:
                logging.error(f"With parameters: {parameters}")
            else:
                logging.error("No parameters provided for the query.")
            logging.error(f"Error executing query: {err}")
            return None, -1, str(err)
        except Exception as err:
            logging.error(f"Unexpected error executing query: {query}")
            if parameters:
                logging.error(f"With parameters: {parameters}")
            else:
                logging.error("No parameters provided for the query.")
            logging.error(f"Error executing query: {err}")
            return None, -1, str(err)

    
#------------------------------------------------------------------------------
# Function: delete_all_connections
#------------------------------------------------------------------------------
    def delete_all_connections(self) -> Tuple[Optional[Any], int, str]:
        """Delete all connections from the Neo4j database."""
        query = "MATCH ()-[r:CONNECTED_TO]-() DELETE r"
        if not self.driver:
            logging.error("No Neo4j connection established.")
            return None, -1, "No connection"
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters)
                records = result.data()
                logging.debug(f"Query executed successfully: {query}")
                return records, 0, "Query executed successfully"
        except neo4j.exceptions.Neo4jError as err:
            logging.error(f"Error executing query: {query}")
            if parameters:
                logging.error(f"With parameters: {parameters}")
            else:
                logging.error("No parameters provided for the query.")
            logging.error(f"Error executing query: {err}")
            return None, -1, str(err)
        except Exception as err:
            logging.error(f"Unexpected error executing query: {query}")
            if parameters:
                logging.error(f"With parameters: {parameters}")
            else:
                logging.error("No parameters provided for the query.")
            logging.error(f"Error executing query: {err}")
            return None, -1, str(err)

    
#------------------------------------------------------------------------------
# Function: get_connected_attendees
#------------------------------------------------------------------------------
    def get_connected_attendees(self, attendeeID) -> Tuple[Optional[Any], int, str]:
        """Get all attendees connected to a specific attendee."""
        query = f"""
        MATCH (a:Attendee {{AttendeeID: {attendeeID}}})-[:CONNECTED_TO]-(connected:Attendee)
        RETURN distinct connected.AttendeeID
        """
        parameters = {}
        if not self.driver:
            logging.error("No Neo4j connection established.")
            return None, -1, "No connection"
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters)
                records = result.data()
                logging.debug(f"Query executed successfully: {query}")
                return records, 0, "Query executed successfully"
        except neo4j.exceptions.Neo4jError as err:
            logging.error(f"Error executing query: {query}")
            if parameters:
                logging.error(f"With parameters: {parameters}")
            else:
                logging.error("No parameters provided for the query.")
            logging.error(f"Error executing query: {err}")
            return None, -1, str(err)
        except Exception as err:
            logging.error(f"Unexpected error executing query: {query}")
            if parameters:
                logging.error(f"With parameters: {parameters}")
            else:
                logging.error("No parameters provided for the query.")
            logging.error(f"Error executing query: {err}")
            return None, -1, str(err)

    
  
#------------------------------------------------------------------------------
# Function: check_connection_exists
#------------------------------------------------------------------------------
    def check_connection_exists(self, attendeeID1, attendeeID2) -> Tuple[Optional[Any], int, str]:
        """Check if a connection exists between two attendees."""
        query = f"""
        MATCH (a1:Attendee {{AttendeeID: {attendeeID1}}})
        MATCH (a2:Attendee {{AttendeeID: {attendeeID2}}})
        MERGE (a1)-[:CONNECTED_TO]->(a2)
        RETURN a1, a2
        """
        parameters = {}
        if not self.driver:
            logging.error("No Neo4j connection established.")
            return None, -1, "No connection"
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters)
                records = result.data()
                logging.debug(f"Query executed successfully: {query}")
                return records, 0, "Query executed successfully"
        except neo4j.exceptions.Neo4jError as err:
            logging.error(f"Error executing query: {query}")
            if parameters:
                logging.error(f"With parameters: {parameters}")
            else:
                logging.error("No parameters provided for the query.")
            logging.error(f"Error executing query: {err}")
            return None, -1, str(err)
        except Exception as err:
            logging.error(f"Unexpected error executing query: {query}")
            if parameters:
                logging.error(f"With parameters: {parameters}")
            else:
                logging.error("No parameters provided for the query.")
            logging.error(f"Error executing query: {err}")
            return None, -1, str(err)

#------------------------------------------------------------------------------------------------------
# Data Access Object (DAO) for MySQL
#------------------------------------------------------------------------------------------------------
class DAO_MySQL:
    """Data Access Object for MySQL database.
    This class provides methods to connect to a MySQL database and execute queries.
    """
#------------------------------------------------------------------------------
# Function: __init__
#------------------------------------------------------------------------------
    def __init__(self, host, user, password, database, dao_neo4j=None):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        # this allows us to use the doa classes within the menu
        # Mainly to load relationships into temporary table and then into neo4j
        self.dao_neo4j = dao_neo4j

#------------------------------------------------------------------------------
# Function: __del__
#------------------------------------------------------------------------------
    def __del__(self):
        """Destructor to ensure the MySQL connection is closed when the object is destroyed."""
        self.close()

#------------------------------------------------------------------------------
# Function: connect
#------------------------------------------------------------------------------
    def connect(self) -> Tuple[Optional[Any], int, str]:
        """Establish a connection to the MySQL database."""
        try:
            self.connection = mysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=mysql.cursors.DictCursor
                #cursorclass=mysql.cursor.DictCursor  # Use DictCursor to get results as dictionaries
            )
            # Got caught out by the autocommit mode when testing the connection to neo4j and then back to mysql, so added this line to ensure autocommit is enabled for all queries
            self.connection.autocommit = True  # Enable autocommit mode
            logging.info("Successfully connected to MySQL database.")
        except mysql.Error as err:
            logging.error(f"Error connecting to MySQL: {err}")
            return None, -1, str(err)
        # create a temporary table to hold the connections between attendees, this will be used to load the connections from neo4j into mysql and then display them in the menu
        _,error_code, error_msg = self.create_relationship_attendees_temporary_table()
        if error_code != 0:
            logging.error("Error creating relationship attendees temporary table: %s", error_msg)
            print(f"*** ERROR *** Creating relationship attendees temporary table: ({error_msg})")
            return None, -1, str(error_msg)
        # do a delete all connections to ensure the temporary table is empty when we start the application, and then we will load the connections from neo4j into the temporary table when we need to display them in the menu
        _,error_code, error_msg = self.delete_all_attendee_connections()
        if error_code != 0:
            logging.error("Error deleting all attendee connections: %s", error_msg)
            print(f"*** ERROR *** Deleting all attendee connections: ({error_msg})")
            return None, -1, str(error_msg)
        
        return self.connection, 0, ""
    
#------------------------------------------------------------------------------
# Function: close
#------------------------------------------------------------------------------
    def close(self):
        """Close the connection to the MySQL database."""
        if self.connection:
            self.connection.close()
            logging.info("MySQL connection closed.")
    
#------------------------------------------------------------------------------
# Function: execute_query
#------------------------------------------------------------------------------
    def execute_query(self, query, values=None) -> Tuple[Optional[Any], int, str]:
        """Execute a SQL query and return the results."""
        if not self.connection:
            logging.error("No MySQL connection established.")
            return None, -1, "No connection"
        try:
            cursor = self.connection.cursor()
            if values:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
            logging.debug(f"Query executed successfully: {query}")
            return results, 0, ""
        except mysql.Error as err:
            logging.error(f"Error executing query: {query}")
            if values:
                logging.error(f"With values: {values}")
            else:
                logging.error("No values provided for the query.")
            logging.error(f"Error executing query: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error executing query: {err}")
            return None, -1, str(err)
#------------------------------------------------------------------------------
# Function: insert_record
#------------------------------------------------------------------------------
    def insert_record(self, tableName, columnConfig, values) -> Tuple[Optional[Any], int, str]:
        """Insert a record into the specified table with the given column configuration and values."""
        # Build the query string based on the table name, column configuration, and values
        columns = ", ".join([column['name'] for column in columnConfig])
        placeholders = ", ".join(["%s"] * len(columnConfig))
        query = f"INSERT INTO {tableName} ({columns}) VALUES ({placeholders})"
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, values)
            self.connection.commit()
            logging.info(f"Record inserted into {tableName} successfully.")
            return cursor.lastrowid, 0, ""
        except mysql.Error as err:
            logging.error(f"Error inserting record into {tableName}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error inserting record into {tableName}: {err}")
            return None, -1, str(err)
#------------------------------------------------------------------------------
# Function: select_record
#------------------------------------------------------------------------------
    def select_record(self, tableName, columnConfig, keyColumnNames=[], keyColumnValues=[]) -> Tuple[Optional[Any], int, str]:
        """Select records from the specified table with the given column configuration and optional where clause."""
        columns = ", ".join([column['name'] for column in columnConfig])
        query = f"SELECT {columns} FROM {tableName}"
        if keyColumnNames and keyColumnValues:
            whereClause = " AND ".join([f"{col} = %s" for col in keyColumnNames])
            query += f" WHERE {whereClause}"
        try:
            cursor = self.connection.cursor()
            if keyColumnValues:
                cursor.execute(query, keyColumnValues)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
            logging.info(f"Records selected from {tableName} successfully.")
            return results, 0, ""
        except mysql.Error as err:
            logging.error(f"Error selecting records from {tableName}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error selecting records from {tableName}: {err}")
            return None, -1, str(err)
#------------------------------------------------------------------------------
# Function: delete_record
#------------------------------------------------------------------------------
    def delete_record(self, tableName, primaryKeyColumn, primaryKeyColumnValues) -> Tuple[Optional[Any], int, str]:
        """Delete a record from the specified table based on the primary key column and values."""
        query = f"DELETE FROM {tableName} WHERE {primaryKeyColumn} = %s"
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (primaryKeyColumnValues,))
            self.connection.commit()
            logging.info(f"Record deleted from {tableName} successfully.")
            return None, 0, ""
        except mysql.Error as err:
            logging.error(f"Error deleting record from {tableName}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error deleting record from {tableName}: {err}")
            return None, -1, str(err)
#------------------------------------------------------------------------------
# Function: update_record
#------------------------------------------------------------------------------
    def update_record(self, tableName, keyColumnNames=[], keyColumnValues=[], updateColumnNames=[], updateColumnValues=[]) -> Tuple[Optional[Any], int, str]:
        """Update a record in the specified table based on the given column configuration and optional where clause."""
        if not updateColumnNames or not updateColumnValues or len(updateColumnNames) != len(updateColumnValues):
            logging.error("Update column names and values must be provided and must have the same length.")
            return None, -1, "Invalid update column configuration"
        setClause = ", ".join([f"{col} = %s" for col in updateColumnNames])
        query = f"UPDATE {tableName} SET {setClause}"
        if keyColumnNames and keyColumnValues:
            whereClause = " AND ".join([f"{col} = %s" for col in keyColumnNames])
            query += f" WHERE {whereClause}"
        values = updateColumnValues + keyColumnValues
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, values)
            self.connection.commit()
            logging.info(f"Record updated in {tableName} successfully.")
            return None, 0, ""
        except mysql.Error as err:
            logging.error(f"Error updating record in {tableName}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error updating record in {tableName}: {err}")
            return None, -1, str(err)
#------------------------------------------------------------------------------
# Function: reset_database
#------------------------------------------------------------------------------
    def reset_database(self) -> Tuple[Optional[Any], int, str]:
        """Reset the MySQL database using the provided SQL file."""
        try:
            print(f"Resetting MySQL database using script: {mysql_reset_file}")
            with open(mysql_reset_file, 'r') as file:
                sql_script = file.read()
            cursor = self.connection.cursor()
            # split on semicolon and execute each statement separately to avoid issues with multiple statements in one execute call
            for statement in sql_script.split(';'):
                print("--------------------------------------------------")
                print(f"Executing SQL statement: {statement}")
                print("--------------------------------------------------")
                if statement.strip():
                    try:
                        cursor.execute(statement)
                    except mysql.Error as err:
                        logging.error(f"Error executing SQL statement: {statement}")
                        logging.error(f"Error details: {err}")
                        return None, err.args[0], err.args[1]
                    except Exception as err:
                        logging.error(f"Unexpected error executing SQL statement: {statement}")
                        logging.error(f"Error details: {err}")
                        return None, -1, str(err)
                    
            # Using autocommit mode, so no need to commit after executing the script
            self.connection.commit()
            logging.info("MySQL database reset successfully.")
        except mysql.Error as err:
            logging.error(f"Error resetting MySQL database: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error resetting MySQL database: {err}")
            return None, -1, str(err)
        return None, 0, "Database reset successful"

#------------------------------------------------------------------------------
# Function: create_relationship_attendees_temporary_table
#------------------------------------------------------------------------------
    def create_relationship_attendees_temporary_table(self) -> Tuple[Optional[Any], int, str]:
        """Create a temporary table to hold attendee connections."""
        query = """
        CREATE TEMPORARY TABLE IF NOT EXISTS attendee_connections (
            connectedAttendeeId INT,
            PRIMARY KEY (connectedAttendeeId)
        )
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
            logging.info("Temporary table 'attendee_connections' created successfully.")
            return None, 0, "Temporary table created successfully"
        except mysql.Error as err:
            logging.error(f"Error creating temporary table 'attendee_connections': {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error creating temporary table 'attendee_connections': {err}")
            return None, -1, str(err)

    
#------------------------------------------------------------------------------
# Function: add_attendee_connection
#------------------------------------------------------------------------------
    def add_attendee_connection(self, attendeeID1)-> Tuple[Optional[Any], int, str]:
        """Add a connection between two attendees in the temporary table."""
        # This database shows “connections” between attendees. Any attendee (that is in the MySQL database) can have a CONNECTED_TO relationship with any other attendee.
        # The direction of the CONNECTED_TO relationship is unimportant.
        # Check if the connection already exists in either direction
        logging.info(f"Adding connection for AttendeeID: {attendeeID1}")
        check_query = """SELECT 1 FROM attendee_connections 
                         WHERE (connectedAttendeeId = %s)"""
        
        existing_connection = None
        check_values = (attendeeID1,)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(check_query, check_values)
                existing_connection = cursor.fetchone()
        except mysql.Error as err:
            logging.error(f"Error checking connection for AttendeeID {attendeeID1}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error checking connection for AttendeeID {attendeeID1}: {err}")
            return None, -1, str(err)
        if existing_connection:
            logging.info("Connection already exists.")
            return None, -1, "Connection already exists"
        # If the connection does not exist, insert it into the table    
        query = "INSERT INTO attendee_connections (connectedAttendeeId) VALUES (%s)"
        values = (attendeeID1,)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
            logging.info(f"Connection added for AttendeeID: {attendeeID1}")
        except mysql.Error as err:
            logging.error(f"Error adding connection for AttendeeID {attendeeID1}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error adding connection for AttendeeID {attendeeID1}: {err}")
            return None, -1, str(err)
        return None, 0, "Connection added successfully"
    
#------------------------------------------------------------------------------
# Function: delete_attendee_connection
#------------------------------------------------------------------------------
    def delete_attendee_connection(self, connectedAttendeeId) -> Tuple[Optional[Any], int, str]:
        """Delete a connection between two attendees from the temporary table."""
        query = """DELETE FROM attendee_connections 
                   WHERE (connectedAttendeeId = %s )"""
        values = (connectedAttendeeId,)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
            logging.info(f"Connection deleted for connectedAttendeeId: {connectedAttendeeId}")
        except mysql.Error as err:
            logging.error(f"Error deleting connection for connectedAttendeeId {connectedAttendeeId}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error deleting connection for connectedAttendeeId {connectedAttendeeId}: {err}")
            return None, -1, str(err)
        return None, 0, "Connection deleted successfully"
    
#------------------------------------------------------------------------------
# Function: delete_all_attendee_connections
#------------------------------------------------------------------------------
    def delete_all_attendee_connections(self) -> Tuple[Optional[Any], int, str]:
        """Delete all connections from the temporary table."""
        query = "DELETE FROM attendee_connections"
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
            logging.info("All connections deleted successfully.")
        except mysql.Error as err:
            logging.error(f"Error deleting all connections: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error deleting all connections: {err}")
            return None, -1, str(err)
        return None, 0, "All connections deleted successfully"
#-------------------------------------------------------------------------------
# Function: get_all_attendee_connections
#------------------------------------------------------------------------------
    def get_all_attendee_connections(self) -> Tuple[Optional[Any], int, str]:
        """Get all connections from the temporary table."""
        query = "SELECT connectedAttendeeId FROM attendee_connections"
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
            logging.info("All connections retrieved successfully.")
        except mysql.Error as err:
            logging.error(f"Error retrieving all connections: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error retrieving all connections: {err}")
            return None, -1, str(err)
        return results, 0, "All connections retrieved successfully"

#------------------------------------------------------------------------------
# Function: get_connection_from_neo4j
#------------------------------------------------------------------------------
    def get_connection_from_neo4j(self, attendeeID)-> Tuple[Optional[Any], int, str]:
        """Get all attendees connected to a specific attendee from Neo4j."""

        if not self.dao_neo4j:
            logging.error("Neo4j DAO is not initialized.")
            return None, -1, "No Neo4j DAO"
        _, error_code, error_message = self.create_relationship_attendees_temporary_table()
        if error_code != 0:
            logging.error("Error creating relationship attendees temporary table: %s", error_message)
            print(f"*** ERROR *** Creating relationship attendees temporary table: ({error_message})")
            return None, -1, str(error_message)
        # Get connected attendees from Neo4j and return the results
        results, error_code, error_message = self.dao_neo4j.get_connected_attendees(attendeeID)
        if error_code != 0:
            logging.error(f"Error getting connected attendees from Neo4j: {error_message}")
            return None, -1, str(error_message)
        # now populate the temporary table with the results
        _ , error_code, error_message = self.delete_all_attendee_connections()
        if error_code != 0:
            logging.error(f"Error deleting all attendee connections: {error_message}")
            return None, -1, str(error_message)
        logging.debug(f"Results retrieved: {results}")
        for record in results:
            connectedAttendeeID = record['connected.AttendeeID']
            logging.info(f"Connected AttendeeID: {connectedAttendeeID} for AttendeeID: {attendeeID}")
            _, error_code, error_message = self.add_attendee_connection(connectedAttendeeID)
            if error_code != 0:
                logging.error(f"Error adding attendee connection: {error_message}")
                return None, -1, str(error_message)
        return results, 0, "Connected attendees retrieved successfully"


#------------------------------------------------------------------------------
# Function: create_company
#------------------------------------------------------------------------------
    def create_company(self, companyID, companyName, industry):
        """Create a new company record in the database."""
        query = "INSERT INTO company (companyID, companyName, industry) VALUES (%s, %s, %s)"
        values = (companyID, companyName, industry)
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(query, values)
                self.connection.commit()
                logging.info("Company created successfully.")
            except mysql.Error as err:
                logging.error(f"Error creating company: {err}")
                return None, err.args[0], err.args[1]
            except Exception as err:
                logging.error(f"Unexpected error creating company: {err}")
                return None, -1, str(err)
        return None, 0, "Company created successfully"
    
#------------------------------------------------------------------------------
# Function: read_company
#------------------------------------------------------------------------------
    def read_company(self, companyID):
        """Read a company record from the database."""
        query = "SELECT companyID, companyName, industry FROM company WHERE companyID = %s"
        values = (companyID,)
        try:            
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                result = cursor.fetchone()
                logging.info(f"Company read successfully for companyID: {companyID}")
            return result, 0, "Company read successfully"
        except mysql.Error as err:
            logging.error(f"Error reading company with companyID {companyID}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error reading company with companyID {companyID}: {err}")
            return None, -1, str(err)
    
#------------------------------------------------------------------------------
# Function: read_all_companies
#------------------------------------------------------------------------------
    def read_all_companies(self,LIMIT=100)-> Tuple[Optional[Any], int, str]:
        """Read all company records from the database."""
        query = f"SELECT companyID, companyName, industry FROM company LIMIT {LIMIT}"
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                logging.info("All companies read successfully.")
            return results, 0, "All companies read successfully"
        except mysql.Error as err:
            logging.error(f"Error reading all companies: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error reading all companies: {err}")
            return None, -1, str(err)
    
#------------------------------------------------------------------------------
# Function: update_company
#------------------------------------------------------------------------------
    def update_company(self, companyID, companyName, industry)-> Tuple[Optional[Any], int, str]:
        """Update a company record in the database."""
        query = "UPDATE company SET companyName = %s, industry = %s WHERE companyID = %s"
        values = (companyName, industry, companyID)
        try:            
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                self.connection.commit()
                logging.info(f"Company updated successfully for companyID: {companyID}")
            return None, 0, "Company updated successfully"
        except mysql.Error as err:
            logging.error(f"Error updating company with companyID {companyID}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error updating company with companyID {companyID}: {err}")
            return None, -1, str(err)
    
#------------------------------------------------------------------------------
# Function: delete_company
#------------------------------------------------------------------------------
    def delete_company(self, companyID)-> Tuple[Optional[Any], int, str]:
        """Delete a company record from the database."""
        query = "DELETE FROM company WHERE companyID = %s"
        values = (companyID,)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                self.connection.commit()
                logging.info(f"Company deleted successfully for companyID: {companyID}")
            return None, 0, "Company deleted successfully"
        except mysql.Error as err:
            logging.error(f"Error deleting company with companyID {companyID}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error deleting company with companyID {companyID}: {err}")
            return None, -1, str(err)
    #   CREATE TABLE attendee (
    #       attendeeID INT PRIMARY KEY,
    #       attendeeName VARCHAR(100) NOT NULL,
    #       attendeeDOB DATE NOT NULL,
    #       attendeeGender ENUM('Male','Female') NOT NULL,
    #       attendeeCompanyID INT NOT NULL,
    #       FOREIGN KEY (attendeeCompanyID) REFERENCES company(companyID)
    #   );

#------------------------------------------------------------------------------
# Function: create_attendee
#------------------------------------------------------------------------------
    def create_attendee(self, attendeeID, attendeeName, attendeeDOB, attendeeGender, attendeeCompanyID) -> Tuple[Optional[Any], int, str]:
        """Create a new attendee record in the database."""
        query = "INSERT INTO attendee (attendeeID, attendeeName, attendeeDOB, attendeeGender, attendeeCompanyID) VALUES (%s, %s, %s, %s, %s)"
        values = (attendeeID, attendeeName, attendeeDOB, attendeeGender, attendeeCompanyID)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                self.connection.commit()
                logging.info(f"Attendee created successfully for attendeeID: {attendeeID}")
            return None, 0, "Attendee created successfully"
        except mysql.Error as err:
            logging.error(f"Error creating attendee with attendeeID {attendeeID}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error creating attendee with attendeeID {attendeeID}: {err}")
            return None, -1, str(err)
    
#------------------------------------------------------------------------------
# Function: read_attendee
#------------------------------------------------------------------------------
    def read_attendee(self, attendeeID)-> Tuple[Optional[Any], int, str]:
        """Read an attendee record from the database."""
        query = "SELECT attendeeID, attendeeName, attendeeDOB, attendeeGender, attendeeCompanyID FROM attendee WHERE attendeeID = %s"
        values = (attendeeID,)
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(query, values)
                result = cursor.fetchone()
                logging.info(f"Attendee read successfully for attendeeID: {attendeeID}")
                return result, 0, "Attendee read successfully"
            except mysql.Error as err:
                logging.error(f"Error reading attendee with attendeeID {attendeeID}: {err}")
                return None, err.args[0], err.args[1]
            except Exception as err:
                logging.error(f"Unexpected error reading attendee with attendeeID {attendeeID}: {err}")
                return None, -1, str(err)
    
#------------------------------------------------------------------------------
# Function: read_all_attendees
#------------------------------------------------------------------------------
    def read_all_attendees(self,LIMIT=100)-> Tuple[Optional[Any], int, str]:
        """Read all attendee records from the database."""
        query = f"SELECT attendeeID, attendeeName, attendeeDOB, attendeeGender, attendeeCompanyID FROM attendee LIMIT {LIMIT}"
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                logging.info("All attendees read successfully.")
            return results, 0, "All attendees read successfully"
        except mysql.Error as err:
            logging.error(f"Error reading all attendees: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error reading all attendees: {err}")
            return None, -1, str(err)

    
#------------------------------------------------------------------------------
# Function: update_attendee
#------------------------------------------------------------------------------
    def update_attendee(self, attendeeID, attendeeName, attendeeDOB, attendeeGender, attendeeCompanyID) -> Tuple[Optional[Any], int, str]:
        """Update an attendee record in the database."""
        query = "UPDATE attendee SET attendeeName = %s, attendeeDOB = %s, attendeeGender = %s, attendeeCompanyID = %s WHERE attendeeID = %s"
        values = (attendeeName, attendeeDOB, attendeeGender, attendeeCompanyID, attendeeID)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                self.connection.commit()
                logging.info(f"Attendee updated successfully for attendeeID: {attendeeID}")
            return None, 0, "Attendee updated successfully"
        except mysql.Error as err:
            logging.error(f"Error updating attendee with attendeeID {attendeeID}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error updating attendee with attendeeID {attendeeID}: {err}")
            return None, -1, str(err)
    
#------------------------------------------------------------------------------
# Function: delete_attendee
#------------------------------------------------------------------------------
    def delete_attendee(self, attendeeID) -> Tuple[Optional[Any], int, str]:
        """Delete an attendee record from the database."""
        query = "DELETE FROM attendee WHERE attendeeID = %s"
        values = (attendeeID,)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                self.connection.commit()
                logging.info(f"Attendee deleted successfully for attendeeID: {attendeeID}")
            return None, 0, "Attendee deleted successfully"
        except mysql.Error as err:
            logging.error(f"Error deleting attendee with attendeeID {attendeeID}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error deleting attendee with attendeeID {attendeeID}: {err}")
            return None, -1, str(err)

    #    
    #   CREATE TABLE room (
    #       roomID INT PRIMARY KEY,
    #       roomName VARCHAR(80) NOT NULL,
    #       capacity INT NOT NULL
    #   );
    
#------------------------------------------------------------------------------
# Function: create_room
#------------------------------------------------------------------------------
    def create_room(self, roomID, roomName, capacity) -> Tuple[Optional[Any], int, str]:
        """Create a new room record in the database."""
        query = "INSERT INTO room (roomID, roomName, capacity) VALUES (?, ?, ?)"
        values = (roomID, roomName, capacity)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                self.connection.commit()
                logging.info(f"Room created successfully for roomID: {roomID}")
            return None, 0, "Room created successfully"
        except mysql.Error as err:
            logging.error(f"Error creating room with roomID {roomID}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error creating room with roomID {roomID}: {err}")
            return None, -1, str(err)   
        return self.execute_query(query, values)

#------------------------------------------------------------------------------
# Function: read_room
#------------------------------------------------------------------------------
    def read_room(self, roomID) -> Tuple[Optional[Any], int, str]:
        """Read a room record from the database."""
        query = "SELECT roomID, roomName, capacity FROM room WHERE roomID = ?"
        values = (roomID,)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                result = cursor.fetchone()
                logging.info(f"Room read successfully for roomID: {roomID}")
                return result, 0, "Room read successfully"
        except mysql.Error as err:
            logging.error(f"Error reading room with roomID {roomID}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error reading room with roomID {roomID}: {err}")
            return None, -1, str(err)
        return self.execute_query(query, values)
    
#------------------------------------------------------------------------------
# Function: read_all_rooms
#------------------------------------------------------------------------------
    def read_all_rooms(self,LIMIT=100) -> Tuple[Optional[Any], int, str]:
        """Read all room records from the database."""
        query = f"SELECT roomID, roomName, capacity FROM room LIMIT {LIMIT}"
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                logging.info("All rooms read successfully.")
            return results, 0, "All rooms read successfully"
        except mysql.Error as err:
            logging.error(f"Error reading all rooms: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error reading all rooms: {err}")
            return None, -1, str(err)
    
#------------------------------------------------------------------------------
# Function: update_room
#------------------------------------------------------------------------------
    def update_room(self, roomID, roomName, capacity) -> Tuple[Optional[Any], int, str]:
        """Update a room record in the database."""
        query = "UPDATE room SET roomName = ?, capacity = ? WHERE roomID = ?"
        values = (roomName, capacity, roomID)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                self.connection.commit()
                logging.info(f"Room updated successfully for roomID: {roomID}")
            return None, 0, "Room updated successfully"
        except mysql.Error as err:
            logging.error(f"Error updating room with roomID {roomID}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error updating room with roomID {roomID}: {err}")
            return None, -1, str(err)
    
#------------------------------------------------------------------------------
# Function: delete_room
#------------------------------------------------------------------------------
    def delete_room(self, roomID) -> Tuple[Optional[Any], int, str]:
        """Delete a room record from the database."""
        query = "DELETE FROM room WHERE roomID = ?"
        values = (roomID,)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                self.connection.commit()
                logging.info(f"Room deleted successfully for roomID: {roomID}")
            return None, 0, "Room deleted successfully"
        except mysql.Error as err:
            logging.error(f"Error deleting room with roomID {roomID}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error deleting room with roomID {roomID}: {err}")
            return None, -1, str(err)
    
#------------------------------------------------------------------------------
# Function: create_session
#------------------------------------------------------------------------------
    def create_session(self, sessionID, sessionTitle, speakerName, sessionDate, roomID) -> Tuple[Optional[Any], int, str]:
        """Create a new session record in the database."""
        query = "INSERT INTO session (sessionID, sessionTitle, speakerName, sessionDate, roomID) VALUES (?, ?, ?, ?, ?)"
        values = (sessionID, sessionTitle, speakerName, sessionDate, roomID)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                self.connection.commit()
                logging.info(f"Session created successfully for sessionID: {sessionID}")
            return None, 0, "Session created successfully"
        except mysql.Error as err:
            logging.error(f"Error creating session with sessionID {sessionID}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error creating session with sessionID {sessionID}: {err}")
            return None, -1, str(err)

#------------------------------------------------------------------------------
# Function: read_session
#------------------------------------------------------------------------------
    def read_session(self, sessionID) -> Tuple[Optional[Any], int, str]:
        """Read a session record from the database."""
        query = "SELECT sessionID, sessionTitle, speakerName, sessionDate, roomID FROM session WHERE sessionID = ?"
        values = (sessionID,)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                result = cursor.fetchone()
                logging.info(f"Session read successfully for sessionID: {sessionID}")
            return result, 0, "Session read successfully"
        except mysql.Error as err:
            logging.error(f"Error reading session with sessionID {sessionID}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error reading session with sessionID {sessionID}: {err}")
            return None, -1, str(err)

#------------------------------------------------------------------------------
# Function: read_all_sessions
#------------------------------------------------------------------------------
    def read_all_sessions(self,LIMIT=100) -> Tuple[Optional[Any], int, str]:
        """Read all session records from the database."""
        query = f"SELECT sessionID, sessionTitle, speakerName, sessionDate, roomID FROM session LIMIT {LIMIT}"
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                logging.info(f"All sessions read successfully with limit: {LIMIT}")
            return result, 0, "All sessions read successfully"
        except mysql.Error as err:
            logging.error(f"Error reading all sessions: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error reading all sessions: {err}")
            return None, -1, str(err)

#------------------------------------------------------------------------------
# Function: update_session
#------------------------------------------------------------------------------
    def update_session(self, sessionID, sessionTitle, speakerName, sessionDate, roomID) -> Tuple[Optional[Any], int, str]:
        """Update a session record in the database."""
        query = "UPDATE session SET sessionTitle = ?, speakerName = ?, sessionDate = ?, roomID = ? WHERE sessionID = ?"
        values = (sessionTitle, speakerName, sessionDate, roomID, sessionID)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                self.connection.commit()
                logging.info(f"Session updated successfully for sessionID: {sessionID}")
            return None, 0, "Session updated successfully"
        except mysql.Error as err:
            logging.error(f"Error updating session with sessionID {sessionID}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error updating session with sessionID {sessionID}: {err}")
            return None, -1, str(err)

#------------------------------------------------------------------------------
# Function: delete_session
#------------------------------------------------------------------------------
    def delete_session(self, sessionID) -> Tuple[Optional[Any], int, str]:
        """Delete a session record from the database."""
        query = "DELETE FROM session WHERE sessionID = ?"
        values = (sessionID,)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                self.connection.commit()
                logging.info(f"Session deleted successfully for sessionID: {sessionID}")
            return None, 0, "Session deleted successfully"
        except mysql.Error as err:
            logging.error(f"Error deleting session with sessionID {sessionID}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error deleting session with sessionID {sessionID}: {err}")
            return None, -1, str(err)

#------------------------------------------------------------------------------
# Function: create_registration
#------------------------------------------------------------------------------
    def create_registration(self, registrationID, attendeeID, sessionID, registeredAt) -> Tuple[Optional[Any], int, str]:
        """Create a new registration record in the database."""
        query = "INSERT INTO registration (registrationID, attendeeID, sessionID, registeredAt) VALUES (?, ?, ?, ?)"
        values = (registrationID, attendeeID, sessionID, registeredAt)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                self.connection.commit()
                logging.info(f"Registration created successfully for registrationID: {registrationID}")
            return None, 0, "Registration created successfully"
        except mysql.Error as err:
            logging.error(f"Error creating registration with registrationID {registrationID}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error creating registration with registrationID {registrationID}: {err}")
            return None, -1, str(err)
    
#------------------------------------------------------------------------------
# Function: read_registration
#------------------------------------------------------------------------------
    def read_registration(self, registrationID) -> Tuple[Optional[Any], int, str]:
        """Read a registration record from the database."""
        query = "SELECT registrationID, attendeeID, sessionID, registeredAt FROM registration WHERE registrationID = ?"
        values = (registrationID,)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                result = cursor.fetchone()
                logging.info(f"Registration read successfully for registrationID: {registrationID}")
            return result, 0, "Registration read successfully"
        except mysql.Error as err:
            logging.error(f"Error reading registration with registrationID {registrationID}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error reading registration with registrationID {registrationID}: {err}")
            return None, -1, str(err)

    
#------------------------------------------------------------------------------
# Function: read_all_registrations
#------------------------------------------------------------------------------
    def read_all_registrations(self,LIMIT=100) -> Tuple[Optional[Any], int, str]:
        """Read all registration records from the database."""
        query = f"SELECT registrationID, attendeeID, sessionID, registeredAt FROM registration LIMIT {LIMIT}"
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                logging.info(f"All registrations read successfully with limit: {LIMIT}")
            return results, 0, "All registrations read successfully"
        except mysql.Error as err:
            logging.error(f"Error reading all registrations: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error reading all registrations: {err}")
            return None, -1, str(err)
        

    
#------------------------------------------------------------------------------
# Function: update_registration
#------------------------------------------------------------------------------
    def update_registration(self, registrationID, attendeeID, sessionID, registeredAt) -> Tuple[Optional[Any], int, str]:
        """Update a registration record in the database."""
        query = "UPDATE registration SET attendeeID = ?, sessionID = ?, registeredAt = ? WHERE registrationID = ?"
        values = (attendeeID, sessionID, registeredAt, registrationID)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                self.connection.commit()
                logging.info(f"Registration updated successfully for registrationID: {registrationID}")
            return None, 0, "Registration updated successfully"
        except mysql.Error as err:
            logging.error(f"Error updating registration with registrationID {registrationID}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error updating registration with registrationID {registrationID}: {err}")
            return None, -1, str(err)
        
#------------------------------------------------------------------------------
# Function: delete_registration
#------------------------------------------------------------------------------
    def delete_registration(self, registrationID) -> Tuple[Optional[Any], int, str]:
        """Delete a registration record from the database."""
        query = "DELETE FROM registration WHERE registrationID = ?"
        values = (registrationID,)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                self.connection.commit()
                logging.info(f"Registration deleted successfully for registrationID: {registrationID}")
            return None, 0, "Registration deleted successfully"
        except mysql.Error as err:
            logging.error(f"Error deleting registration with registrationID {registrationID}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error deleting registration with registrationID {registrationID}: {err}")
            return None, -1, str(err)

    # -- Report sessions by speaker

#------------------------------------------------------------------------------
# Function: report_sessions_by_speaker
#------------------------------------------------------------------------------
    def report_sessions_by_speaker(self, speakerName)-> Tuple[Optional[Any], int, str]:
        """Report sessions by a specific speaker."""
        # Add % wildcards to the speakerName for partial matching
        # Select speakerName , sessionTitle and name of the room from session table where speakerName matches the input
        # Order the results by speakerName, sessionTitle and roomName so is consistent and easy to read
        like_pattern = f"%{speakerName}%"
        query = """SELECT speakerName,
                  sessionTitle,
                  R.roomName
           FROM session AS SES
           INNER JOIN room AS R ON SES.roomID = R.roomID
           WHERE speakerName LIKE %s
           ORDER BY speakerName, sessionTitle, roomName"""
        values = (like_pattern,)
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                results = cursor.fetchall()
                logging.info(f"Sessions report generated successfully for speakerName: {speakerName}")
            return results, 0, "Sessions report generated successfully"
        except mysql.Error as err:
            logging.error(f"Error generating sessions report for speakerName {speakerName}: {err}")
            return None, err.args[0], err.args[1]
        except Exception as err:
            logging.error(f"Unexpected error generating sessions report for speakerName {speakerName}: {err}")
            return None, -1, str(err)

    
#------------------------------------------------------------------------------
# Function: print_sessions_report
#------------------------------------------------------------------------------
    def print_sessions_report(self, speakerName)-> Tuple[Optional[Any], int, str]:
        """Print a report of sessions by a specific speaker."""
        results, error_code , error_msg  = self.report_sessions_by_speaker(speakerName)
        # if there is sql error
        print(f"\nSession Details For : {speakerName}")
        print("-" * 40)
        if error_code != 0:
            logging.error("Failed to generate sessions report.")
            print(f"Error generating report: {error_msg}")
            return
        # if there are no results found for the speaker
        if results is None or len(results) == 0:
            logging.info(f"No speakers found for that name")
            print(f"No sessions found for speaker: {speakerName}")
            return
        # print the results in a readable format
        for row in results:
            print(f"{row['speakerName']} | {row['sessionTitle']} | {row['roomName']}")

#------------------------------------------------------------------------------
# Function: report_attendees_by_company
#------------------------------------------------------------------------------
    def report_attendees_by_company(self, companyID)-> Tuple[Optional[Any], int, str]:
        """Report attendees by a specific company."""
        values = ()
        query = f"""SELECT ATT.attendeeName,
                  ATT.attendeeDOB,
                  SES.sessionTitle,
                  SES.speakerName,
                  RM.roomName
           FROM attendee AS ATT
           INNER JOIN company AS CMP 
                ON ATT.attendeeCompanyID = CMP.companyID
           INNER JOIN registration AS REG 
                ON ATT.attendeeID = REG.attendeeID
           INNER JOIN session AS SES 
                ON REG.sessionID = SES.sessionID
           INNER JOIN room AS RM 
                ON SES.roomID = RM.roomID
           WHERE CMP.companyID = {companyID}
           ORDER BY ATT.attendeeName, SES.sessionTitle, SES.speakerName, RM.roomName"""
        return self.execute_query(query, values)

#------------------------------------------------------------------------------
# Function: report_connected_attendees
#------------------------------------------------------------------------------
    def report_connected_attendees(self, attendeeID) -> Tuple[Optional[Any], int, str]:
        """Report attendees connected to a specific attendee."""
        query = f"""SELECT attendeeID, attendeeName FROM attendee WHERE attendeeID IN
            (SELECT connectedAttendeeId from attendee_connections WHERE connectedAttendeeId <> %s) ORDER BY attendeeName"""
        return self.execute_query(query, (attendeeID,))

#------------------------------------------------------------------------------
# Function: print_attendees_report
#------------------------------------------------------------------------------
    def print_attendees_report(self, companyID, companyName="")-> Tuple[Optional[Any], int, str]:
        """Print a report of attendees by a specific company."""
        results, error_code, error_msg = self.report_attendees_by_company(companyID)
        if error_code != 0:
            logging.error("Failed to generate attendees report.")
            print(f"Error generating report: {error_msg}")
            return None, error_code, error_msg
        if results is None or len(results) == 0:
            logging.info(f"No attendees found for {companyName}")
            print(f"{companyName}  Attendees")
            print(f"No attendees found for  {companyName}")
            return results, None, None
        print(f"{companyName}  Attendees")
        for row in results:
            print(f"{row['attendeeName']} | {row['attendeeDOB']} | {row['sessionTitle']} | {row['speakerName']} | {row['roomName']}")
        return results, None, None
   # Add a new attendee 


#------------------------------------------------------------------------------------------------------
# Menu 
#------------------------------------------------------------------------------------------------------

MAIN_MENU_OPTIONS = {
    "1": "View Speakers & Sessions",
    "2": "View Attendees by Company",
    "3": "Add New Attendee",
    "4": "View Connected Attendees",
    "5": "Add Attendee Connection",
    "6": "View Rooms",
    "x": "Exit"

}

# This configuration defines the structure of the database tables, including the column names and their data types. 
# # can be used for validation, dynamic query generation, or other purposes within the application.
# TODO : build from data dictionary in the database instead of hardcoding here
TABLE_COLUMN_CONFIG = {
    "company": [{ "name": "companyID", "type": "integer","primary_key": True},
                  { "name": "companyName", "type": "string"},
                   { "name": "industry", "type": "string"}],
    "attendee": [{ "name": "attendeeID", "type": "integer","primary_key": True},
                  { "name": "attendeeName", "type": "string"},
                  { "name": "attendeeDOB", "type": "date"},
                  { "name": "attendeeGender", "type": "enum", "values": ["Male", "Female"]},
                  { "name": "speakerName", "type": "string"},
                  { "name": "attendeeCompanyID", "type": "integer"}],
    "room": [{ "name": "roomID", "type": "integer","primary_key": True},
              { "name": "roomName", "type": "string"},
              { "name": "capacity", "type": "integer"}],
    "session": [{ "name": "sessionID","type": "integer","primary_key": True},
                 { "name": "sessionTitle", "type": "string"}, 
                 { "name": "speakerName", "type": "string"},
                 { "name": "sessionDate", "type": "date"},
                 { "name": "roomID", "type": "integer"}],
    "registration": [{ "name": "registrationID", "type": "integer","primary_key": True},
                      { "name": "attendeeID", "type": "integer"},
                      { "name": "sessionID", "type": "integer"},
                      { "name": "registeredAt", "type": "datetime"}]
              
}

class Menu:
    """Menu class to display options and handle user input.
    This class provides methods to display a menu and process user selections.
    """
#------------------------------------------------------------------------------
# Function: __init__
#------------------------------------------------------------------------------
    def __init__(self,dao_mysql=None, dao_neo4j=None):
        # this allows us to use the doa classes within the menu

        self.dao_mysql = dao_mysql
        self.dao_neo4j = dao_neo4j
        self.view_rooms=None

#------------------------------------------------------------------------------
# Function: display_menu
#------------------------------------------------------------------------------
    def display_menu(self):
        """Display the main menu  to the user."""
        print("\nConference Management:")
        print("\n----------------------")
        for key, value in MAIN_MENU_OPTIONS.items():
            print(f"{key} - {value}")

#------------------------------------------------------------------------------
# Function: menu_print_attendees_by_company
#------------------------------------------------------------------------------
    def menu_print_attendees_by_company(self):
        """Menu option to print attendees by company."""

        while True:
            # the user is asked to enter a valid company ID 
            # 
            inputString = input("Enter Company ID : ")
            # check if string is a number
            if not inputString.isdigit():
                logging.warning("Invalid input. Please enter a numeric company ID.")
                continue
            # try to cast to int and catch any exceptions
            try:
                companyID = int(inputString)
            except ValueError:
                logging.warning("Invalid input. Please enter a numeric company ID.")
                continue
            # check if the number is positive
            if int(inputString) <= 0:
                logging.warning("Invalid input. Please enter a positive numeric company ID.")
                continue
            # Check if company ID exists in the database
            companyResults, error_code, error_msg = self.dao_mysql.read_company(companyID)
            if error_code != 0:
                logging.error("Error checking if company exists: %s", error_msg)
                continue
            if not companyResults or len(companyResults) == 0:
                logging.info(f"No company found with ID: {companyID}")
                print(f"Company with ID  {companyID} doesn't exist.")
                continue
            logging.info(f"Company found with ID: {companyID}")
            logging.info(f"Results: {companyResults}")
            companyName = companyResults['companyName'] # Assuming the company name is in the 'companyName' column
            report_attendees_by_company, error_code, error_msg = self.dao_mysql.report_attendees_by_company(companyID)
            if error_code != 0:
                logging.error("Failed to generate attendees report: %s", error_msg)
                return None, error_code, error_msg
            if report_attendees_by_company is None or len(report_attendees_by_company) == 0:
                logging.info(f"No attendees found for company ID: {companyID}")
                print(f"{companyName}  Attendees")
                print(f"No attendees found for  {companyName}")
                continue
            print(f"{companyName}  Attendees")
            for row in report_attendees_by_company:
                print(f"{row['attendeeName']} | {row['attendeeDOB']} | {row['sessionTitle']} | {row['speakerName']} | {row['roomName']}")
            break

#------------------------------------------------------------------------------
# Function: menu_get_attendee
#------------------------------------------------------------------------------
    def menu_get_attendee(self):
        """Menu option to get an attendee by ID."""
        while True:
            inputString = input("Enter Attendee ID : ")
            if inputString.lower() == "x":
                logging.info("Exiting attendee lookup.")
                return
            if not inputString.isdigit():
                logging.warning("Invalid input. Please enter a numeric attendee ID.")
                continue
            try:
                attendeeID = int(inputString)
            except ValueError:
                logging.warning("Invalid input. Please enter a numeric attendee ID.")
                continue
            if int(inputString) <= 0:
                logging.warning("Invalid input. Please enter a positive numeric attendee ID.")
                continue
            attendeeResults, error_code, error_msg = self.dao_mysql.read_attendee(attendeeID)
            if error_code != 0:
                logging.error("Error checking if attendee exists: %s", error_msg)
                continue
            if not attendeeResults or len(attendeeResults) == 0:
                logging.info(f"No attendee found with ID: {attendeeID}")
                print(f"Attendee with ID  {attendeeID} doesn't exist.")
                continue
            print(f"Attendee Details for ID: {attendeeID}")
            print("-" * 40)
            logging.info(f"Attendee found with ID: {attendeeID}")
            logging.info(f"Results: {attendeeResults}")
            print(f"Attendee ID: {attendeeResults['attendeeID']}")
            print(f"Name : {attendeeResults['attendeeName']}")
            print(f"DOB : {attendeeResults['attendeeDOB']}")
            print(f"Gender : {attendeeResults['attendeeGender']}")
            print(f"Company ID : {attendeeResults['attendeeCompanyID']}")
            print("-" * 40)
#------------------------------------------------------------------------------
# Function: menu_delete_attendee
# ------------------------------------------------------------------------------
    def menu_delete_attendee(self):
        """Menu option to delete an attendee by ID."""
        while True:
            inputString = input("Enter Attendee ID to delete : ")
            if inputString.lower() == "x":
                logging.info("Exiting attendee deletion.")
                return
            if not inputString.isdigit():
                logging.warning("Invalid input. Please enter a numeric attendee ID.")
                continue
            try:
                attendeeID = int(inputString)
            except ValueError:
                logging.warning("Invalid input. Please enter a numeric attendee ID.")
                continue
            if int(inputString) <= 0:
                logging.warning("Invalid input. Please enter a positive numeric attendee ID.")
                continue
            attendeeResults, error_code, error_msg = self.dao_mysql.read_attendee(attendeeID)
            if error_code != 0:
                logging.error("Error checking if attendee exists: %s", error_msg)
                continue
            if not attendeeResults or len(attendeeResults) == 0:
                logging.info(f"No attendee found with ID: {attendeeID}")
                print(f"Attendee with ID  {attendeeID} doesn't exist.")
                continue
            confirm = input(f"Are you sure you want to delete attendee with ID {attendeeID}? (y/n): ")
            if confirm.lower() == "y":
                _, error_code, error_msg = self.dao_mysql.delete_attendee(attendeeID)
                if error_code != 0:
                    logging.error("Error deleting attendee: %s", error_msg)
                    print(f"Error deleting attendee: {error_msg}")
                    continue
                logging.info(f"Attendee with ID {attendeeID} deleted successfully.")
                print(f"Attendee with ID {attendeeID} deleted successfully.")
            else:
                logging.info("Attendee deletion cancelled.")
                print("Attendee deletion cancelled.")
            break            
#------------------------------------------------------------------------------
# Function: menu_add_attendee
#------------------------------------------------------------------------------
    def menu_add_attendee(self):
        print("Add New Attendee")
        print("----------------")
        attendeeId = input("Attendee ID : ")
        attendeeName = input("Name : ")
        attendeeDOB = input("DOB : ")
        attendeeGender = input("Gender : ")
        attendeeCompanyID = input("Company ID : ")
        # Check if attendee ID is a number
        #if not attendeeId.isdigit():
        #    logging.error("Invalid input. Please enter a numeric attendee ID.")
        #    print(f"*** ERROR *** Attendee ID: {attendeeId} is not a valid number")
        #    return
        # see if attendee already exists
        existingAttendee, error_code, error_msg = self.dao_mysql.read_attendee(attendeeId)
        if error_code != 0:
            logging.error("Error checking if attendee exists: %s", error_msg)
            print(f'*** ERROR *** Error checking if attendee exists: ({error_msg})')
            return
        if existingAttendee and len(existingAttendee) > 0:
            logging.info(f"Attendee with ID {attendeeId} already exists.")
            print(f"*** ERROR *** Attendee ID: {attendeeId} already exists")
            return
        # Check if Gender is Male or Female
        if attendeeGender not in ["Male", "Female"]:
            logging.error("Invalid input. Please enter 'Male' or '  Female' for gender.")
            print(f"*** ERROR *** Gender must be Male/Female")
            return
        # Check if company ID is a number
        if not attendeeCompanyID.isdigit():
            logging.error("Invalid input. Please enter a numeric company ID.")
            print(f"*** ERROR *** Company ID: {attendeeCompanyID} is not a valid number")
            return
        # Check if company ID exists        
        companyResults, error_code, error_msg = self.dao_mysql.read_company(attendeeCompanyID)
        if error_code != 0:
            logging.error("Error checking if company exists: %s", error_msg)
            print(f'*** ERROR *** Company ID: {attendeeCompanyID} - Error checking if company exists: ({error_msg})')
            return
        if not companyResults or len(companyResults) == 0:
            logging.info(f"No company found with ID: {attendeeCompanyID}")
            print(f"*** ERROR *** Company ID: {attendeeCompanyID} does not exist")
            return
        # Now enter New attendee into the database
        _, error_code, error_msg = self.dao_mysql.create_attendee(attendeeId, attendeeName, attendeeDOB, attendeeGender, attendeeCompanyID)
        if error_code != 0:
            logging.error("Error creating new attendee: %s", error_msg)
            print(f'*** ERROR *** ({error_msg})')
            return
        logging.info(f"Attendee {attendeeName} created successfully with ID: {attendeeId}")
        print(f"Attendee successfully added")
        return
    
#------------------------------------------------------------------------------
# menu_view_connected_attendees
#------------------------------------------------------------------------------
    def menu_view_connected_attendees(self):
        """Menu option to view attendees connected to a specific attendee."""
        
        # get attendee from mysql to get name
        while True:
            attendeeId = input("Enter Attendee ID :")
            # if it is non numeric then show error and ask again
            # saves accessing the database if the input is invalid
            if not attendeeId.isdigit():
                logging.warning("Invalid input. Please enter a numeric attendee ID.")
                print(f"*** ERROR *** Invalid attendee ID")
                continue
            attendeeResults, error_code, error_msg = self.dao_mysql.read_attendee(attendeeId)
            if error_code != 0:
                logging.error("Error checking if attendee exists: %s", error_msg)
                print(f"*** ERROR *** Invalid attendee ID")
                # Better error but above is as per requirements
                #print(f'*** ERROR *** Error checking if attendee exists: ({err.args[0]}, "{err.args[1]}")')
                continue
            if not attendeeResults or len(attendeeResults) == 0:
                logging.info(f"No attendee found with ID: {attendeeId}")
                print(f"*** ERROR *** Attendee does not exist")
                # exit the loop and return to main menu
                break
            #print(f"Attendee Details for ID: {attendeeResults}")
            attendeeName = attendeeResults['attendeeName']  # Assuming the attendee name is in the 'name' column
            logging.info(f"Attendee found: {attendeeName} (ID: {attendeeId})")
            print(f"Attendee Name: {attendeeName}")
            # Create a temporary table in MySQL to hold the connected attendees for this attendee   
            # Get connected attendees from Neo4j and populate the temporary table in MySQL
            logging.info(f"Getting connected attendees for {attendeeName} (ID: {attendeeId}) from Neo4j and populating temporary table in MySQL")
            logging.info("Creating relationship attendees temporary table in MySQL")

            # Delete any existing connections for this attendee in the temporary table to avoid duplicates
            logging.info("Deleting existing attendee connections in the temporary table")

            _, error_code, error_msg = self.dao_mysql.delete_all_attendee_connections()
            if error_code != 0:
                logging.error("Error deleting existing attendee connections: %s", error_msg)
                print(f"*** ERROR *** Deleting existing attendee connections: ({error_msg})")
                break
            logging.info("Getting connections from Neo4j and inserting into temporary table in MySQL")
            results, error_code, error_msg = self.dao_mysql.get_connection_from_neo4j(attendeeId)
            if error_code != 0:
                logging.error("Error getting connections from Neo4j: %s", error_msg)
                print(f"*** ERROR *** Getting connections from Neo4j: ({error_msg})")
                break
            report, error_code, error_msg = self.dao_mysql.report_connected_attendees(attendeeId)
            if error_code != 0:
                logging.error("Error generating connected attendees report: %s", error_msg)
                print(f"*** ERROR *** Generating connected attendees report: ({error_msg})")
                break
            print(f"These attendees are connected:")
            for row in report:
                print(f"{row['attendeeID']} | {row['attendeeName']}")

#------------------------------------------------------------------------------
# Function: menu_add_attendee_connection
#------------------------------------------------------------------------------
    def menu_add_attendee_connection(self):
        """Menu option to add a connection between two attendees."""
        while True:
            attendeeID1 = input("Enter Attendee ID 1 : ")
            attendeeID2 = input("Enter Attendee ID 2 : ")
            # Check if attendee IDs are numeric
            if not attendeeID1.isdigit() or not attendeeID2.isdigit():
                logging.error("Invalid input. Please enter numeric attendee IDs.")
                print(f"*** ERROR *** Attendee IDs must be numbers")
                continue
            # Check if both attendees ID are the same
            if attendeeID1 == attendeeID2:
                logging.error("Invalid input. Attendee IDs cannot be the same.")
                print(f"*** ERROR *** An attendee cannot connect to him/herself")
                continue
            ## Check if attendee ID 1 exists
            attendeeResults1, error_code, error_msg = self.dao_mysql.read_attendee(attendeeID1)
            if error_code != 0:
                logging.error("Error checking if attendee 1 exists: %s", error_msg)
                print(f"*** ERROR *** Attendee ID 1: {attendeeID1} - Error checking if attendee exists: ({error_msg})")
                continue
            if not attendeeResults1 or len(attendeeResults1) == 0:
                logging.info(f"No attendee found with ID: {attendeeID1}")
                print(f"*** ERROR *** One or both attendee ID's do not exist")
                continue
            # Check if attendee ID 2 exists
            attendeeResults2, error_code, error_msg = self.dao_mysql.read_attendee(attendeeID2)
            if error_code != 0:
                logging.error("Error checking if attendee 2 exists: %s", error_msg)
                print(f"*** ERROR *** Attendee ID 2: {attendeeID2} - Error checking if attendee exists: ({error_msg})")
                continue
            if not attendeeResults2 or len(attendeeResults2) == 0:
                logging.info(f"No attendee found with ID: {attendeeID2}")
                print(f"*** ERROR *** One or both attendee ID's do not exist")
                continue
            # Check if the connection already exists in Neo4j
            connectionResults, error_code, error_msg = self.dao_neo4j.check_connection_exists(attendeeID1, attendeeID2)
            #logging.debug(f"Connection results: {connectionResults}, Error code: {error_code}, Error message: {error_msg}")
            if error_code != 0:
                logging.error("Error checking if connection exists in Neo4j: %s", error_msg)
                print(f"*** ERROR *** Checking connection in Neo4j: ({error_msg})")
                continue
            if connectionResults and len(connectionResults) > 0:
                logging.info(f"Connection already exists between attendees {attendeeID1} and {attendeeID2}")
                print(f"*** ERROR *** Connection already exists between attendees {attendeeID1} and {attendeeID2}")
                break
            # Add the connection to Neo4j
            _, error_code, error_msg = self.dao_neo4j.merge_connection(attendeeID1, attendeeID2)
            if error_code != 0:
                logging.error("Error adding connection to Neo4j: %s", error_msg)
                print(f"*** ERROR *** Adding connection to Neo4j: ({error_msg})")
                break
            logging.info(f"Connection successfully added between attendees {attendeeID1} and {attendeeID2}")
            print(f"Attendee {attendeeID1} is now connected to {attendeeID2}")
            break


#------------------------------------------------------------------------------
# Function: menu_view_rooms
#------------------------------------------------------------------------------
    def menu_view_rooms(self):
        """Menu option to view all rooms."""
        # Populate only once
        if self.view_rooms is None:
            self.view_rooms = []

            results, error_code, error_msg = self.dao_mysql.read_all_rooms()
            if error_code != 0:
                logging.error("Error retrieving rooms: %s", error_msg)
                print(f"*** ERROR *** Retrieving rooms: ({error_code} {error_msg})")
                return
            if results is None or len(results) == 0:
                logging.info("No rooms found in the database.")
                print("No rooms found.")
                return
            self.view_rooms = results

        print("RoomID    | RoomName | Capacity")
        for row in self.view_rooms:
            print(f"{row['roomID']} | {row['roomName']}  | {row['capacity']}")
#------------------------------------------------------------------------------
# Function: menu_reset_mysql_database
#------------------------------------------------------------------------------
    def menu_reset_mysql_database(self):
        """Menu option to reset the MySQL database."""
        confirm = input("Are you sure you want to reset the MySQL database? This will delete all data. (y/n): ")
        if confirm.lower() == "y":
            logging.info("Resetting the MySQL database...")
            _, error_code, error_msg = self.dao_mysql.reset_database()
            if error_code != 0:
                logging.error("Error resetting the MySQL database: %s", error_msg)
                print(f"*** ERROR *** Resetting the MySQL database: ({error_msg})")
                return
            logging.info("MySQL database reset successfully.")
            print("MySQL database has been reset successfully.")
        else:
            logging.info("MySQL database reset cancelled.")
            print("MySQL database reset cancelled.") 
#------------------------------------------------------------------------------
# Function: menu_reset_neo4j_database
#------------------------------------------------------------------------------
    def menu_reset_neo4j_database(self):
        """Menu option to reset the Neo4j database."""
        confirm = input("Are you sure you want to reset the Neo4j database? This will delete all data. (y/n): ")
        if confirm.lower() == "y":
            logging.info("Resetting the Neo4j database...")
            _, error_code, error_msg = self.dao_neo4j.reset_database()
            if error_code != 0:
                logging.error("Error resetting the Neo4j database: %s", error_msg)
                print(f"*** ERROR *** Resetting the Neo4j database: ({error_msg})")
                return
            logging.info("Neo4j database reset successfully.")
            print("Neo4j database has been reset successfully.")
        else:
            logging.info("Neo4j database reset cancelled.")
            print("Neo4j database reset cancelled.") 
#------------------------------------------------------------------------------
# Function: menu_insert_table
#------------------------------------------------------------------------------
    def menu_insert_table(self, tableName):
        """Menu option to insert a new record into a specified table."""
        if tableName not in TABLE_COLUMN_CONFIG:
            logging.error(f"Invalid table name: {tableName}")
            print(f"*** ERROR *** Invalid table name: {tableName}")
            return
        # check if tablename in the config and get the column names and types
        if tableName not in TABLE_COLUMN_CONFIG:
            logging.error(f"Table {tableName} is not defined in the configuration.")
            print(f"*** ERROR *** Table {tableName} is not defined in the configuration.")
            return
        columnConfig = TABLE_COLUMN_CONFIG[tableName]
        values = []
        for column in columnConfig:
            inputValue = input(f"{column['name']} : ")
            # Basic validation based on type
            if column['type'] == "integer":
                if not inputValue.isdigit():
                    logging.error(f"Invalid input for {column['name']}. Expected an integer.")
                    print(f"*** ERROR *** Invalid input for {column['name']}. Expected an integer.")
                    return
                values.append(int(inputValue))
            elif column['type'] == "enum":
                if inputValue not in column['values']:
                    logging.error(f"Invalid input for {column['name']}. Expected one of: {', '.join(column['values'])}.")
                    print(f"*** ERROR *** Invalid input for {column['name']}. Expected one of: {', '.join(column['values'])}.")
                    return
                values.append(inputValue)
            elif column['type'] == "date":
                # Basic date validation (YYYY-MM-DD)
                try:
                    datetime.date.strptime(inputValue, "%Y-%m-%d")
                except ValueError:
                    logging.error(f"Invalid input for {column['name']}. Expected a date in YYYY-MM-DD format.")
                    print(f"*** ERROR *** Invalid input for {column['name']}. Expected a date in YYYY-MM-DD format.")
                    return
                values.append(inputValue)
            else:
                values.append(inputValue)
        # Now insert the record into the database
        print(type(columnConfig))
        _, error_code, error_msg = self.dao_mysql.insert_record(tableName, columnConfig, values)
        if error_code != 0:
            logging.error(f"Error inserting record into {tableName}: {error_msg}")
            print(f"*** ERROR *** Inserting record into {tableName}: ({error_msg})")
            return

            
        logging.info(f"Record inserted into {tableName} with values: {values}")
        print(f"Record successfully inserted into {tableName}.")
#------------------------------------------------------------------------------
# Function: menu_insert_table
#------------------------------------------------------------------------------
    def menu_select_table(self, tableName):
        """Menu option to select and display records from a specified table."""
        if tableName not in TABLE_COLUMN_CONFIG:
            logging.error(f"Invalid table name: {tableName}")
            print(f"*** ERROR *** Invalid table name: {tableName}")
            return
        # find the primary key column for the table
        primaryKeyColumn = []
        primaryKeyColumnValues = []
        for column in TABLE_COLUMN_CONFIG[tableName]:
            if column.get("primary_key", False):
                primaryKeyColumn.append(column['name'])
                value = input(f"{column['name']} : ")
                primaryKeyColumnValues.append(value)
                # Basic validation based on type
                if column['type'] == "integer":
                    if not value.isdigit():
                        logging.error(f"Invalid input for {column['name']}. Expected an integer.")
                        print(f"*** ERROR *** Invalid input for {column['name']}. Expected an integer.")
                        return
                elif column['type'] == "date":
                    # Basic date validation (YYYY-MM-DD)
                    try:
                        datetime.date.strptime(value, "%Y-%m-%d")
                    except ValueError:
                        logging.error(f"Invalid input for {column['name']}. Expected a date in YYYY-MM-DD format.")
                        print(f"*** ERROR *** Invalid input for {column['name']}. Expected a date in YYYY-MM-DD format.")
                        return
                elif column['type'] == "enum":
                    if value not in column['values']:
                        logging.error(f"Invalid input for {column['name']}. Expected one of: {', '.join(column['values'])}.")
                        print(f"*** ERROR *** Invalid input for {column['name']}. Expected one of: {', '.join(column['values'])}.")
                        return
                else:
                        primaryKeyColumnValues.append(value)
        if len(primaryKeyColumn) == 0:
            logging.error(f"No primary key defined for table: {tableName}")
            print(f"*** ERROR *** No primary key defined for table: {tableName}")
            return
            # Now select the record from the database
        results, error_code, error_msg = self.dao_mysql.select_record(tableName, primaryKeyColumn, primaryKeyColumnValues)
        if error_code != 0:
            logging.error(f"Error selecting record from {tableName}: {error_msg}")
            print(f"*** ERROR *** Selecting record from {tableName}: ({error_msg})")
            return
        if results is None or len(results) == 0:
            logging.info(f"No record found in {tableName} with {primaryKeyColumn} = {primaryKeyColumnValues}")
            print(f"No record found in {tableName} with {primaryKeyColumn} = {primaryKeyColumnValues}")
            return
        logging.info(f"Record found in {tableName} with {primaryKeyColumn} = {primaryKeyColumnValues}: {results}")
        print(f"Record found in {tableName}:")
        for key, value in results[0].items():
            print(f"{key} : {value}")
#------------------------------------------------------------------------------
# Function: menu_delete_table
#------------------------------------------------------------------------------
    def menu_delete_table(self, tableName):
        """Menu option to delete a record from a specified table based on primary key."""
        if tableName not in TABLE_COLUMN_CONFIG:
            logging.error(f"Invalid table name: {tableName}")
            print(f"*** ERROR *** Invalid table name: {tableName}")
            return
        # find the primary key column for the table
        primaryKeyColumn = []
        primaryKeyColumnValues = []
        for column in TABLE_COLUMN_CONFIG[tableName]:
            if column.get("primary_key", False):
                primaryKeyColumn.append(column['name'])
                value = input(f"{column['name']} : ")
                primaryKeyColumnValues.append(value)
                # Basic validation based on type
                if column['type'] == "integer":
                    if not value.isdigit():
                        logging.error(f"Invalid input for {column['name']}. Expected an integer.")
                        print(f"*** ERROR *** Invalid input for {column['name']}. Expected an integer.")
                        return
                elif column['type'] == "date":
                    # Basic date validation (YYYY-MM-DD)
                    try:
                        datetime.date.strptime(value, "%Y-%m-%d")
                    except ValueError:
                        logging.error(f"Invalid input for {column['name']}. Expected a date in YYYY-MM-DD format.")
                        print(f"*** ERROR *** Invalid input for {column['name']}. Expected a date in YYYY-MM-DD format.")
                        return
                elif column['type'] == "enum":
                    if value not in column['values']:
                        logging.error(f"Invalid input for {column['name']}. Expected one of: {', '.join(column['values'])}.")
                        print(f"*** ERROR *** Invalid input for {column['name']}. Expected one of: {', '.join(column['values'])}.")
                        return
                else:
                        primaryKeyColumnValues.append(value)
        if len(primaryKeyColumn) == 0:
            logging.error(f"No primary key defined for table: {tableName}")
            print(f"*** ERROR *** No primary key defined for table: {tableName}")
            return
        # Now delete the record from the database
        _, error_code, error_msg = self.dao_mysql.delete_record(tableName, primaryKeyColumn, primaryKeyColumnValues)
        if error_code != 0:
            logging.error(f"Error deleting record from {tableName}: {error_msg}")
            print(f"*** ERROR *** Deleting record from {tableName}: {error_msg}")
        else:
            logging.info(f"Record deleted from {tableName} with {primaryKeyColumn} = {primaryKeyColumnValues}")
            print(f"Record deleted from {tableName} with {primaryKeyColumn} = {primaryKeyColumnValues}")
#------------------------------------------------------------------------------
# Function: menu_update_table
#------------------------------------------------------------------------------
    def menu_update_table(self, tableName):
        """Menu option to update a record in a specified table based on primary key."""
        if tableName not in TABLE_COLUMN_CONFIG:
            logging.error(f"Invalid table name: {tableName}")
            print(f"*** ERROR *** Invalid table name: {tableName}")
            return
        # find the primary key column for the table
        primaryKeyColumn = []
        primaryKeyColumnValues = []
        for column in TABLE_COLUMN_CONFIG[tableName]:
            if column.get("primary_key", False):
                primaryKeyColumn.append(column['name'])
                value = input(f"{column['name']} : ")
                primaryKeyColumnValues.append(value)
                # Basic validation based on type
                if column['type'] == "integer":
                    if not value.isdigit():
                        logging.error(f"Invalid input for {column['name']}. Expected an integer.")
                        print(f"*** ERROR *** Invalid input for {column['name']}. Expected an integer.")
                        return
                elif column['type'] == "date":
                    # Basic date validation (YYYY-MM-DD)
                    try:
                        datetime.date.strptime(value, "%Y-%m-%d")
                    except ValueError:
                        logging.error(f"Invalid input for {column['name']}. Expected a date in YYYY-MM-DD format.")
                        print(f"*** ERROR *** Invalid input for {column['name']}. Expected a date in YYYY-MM-DD format.")
                        return
                elif column['type'] == "enum":
                    if value not in column['values']:
                        logging.error(f"Invalid input for {column['name']}. Expected one of: {', '.join(column['values'])}.")
                        print(f"*** ERROR *** Invalid input for {column['name']}. Expected one of: {', '.join(column['values'])}.")
                        return
                else:
                        primaryKeyColumnValues.append(value)
        if len(primaryKeyColumn) == 0:
            logging.error(f"No primary key defined for table: {tableName}")
            print(f"*** ERROR *** No primary key defined for table: {tableName}")
            return
        # Using the primary key values, select the record to update and display current values
        results, error_code, error_msg = self.dao_mysql.select_record(tableName, primaryKeyColumn, primaryKeyColumnValues)
        if error_code != 0:
            logging.error(f"Error selecting record from {tableName}: {error_msg}")
            print(f"*** ERROR *** Selecting record from {tableName}: ({error_msg})")
            return
        if results is None or len(results) == 0:
            logging.info(f"No record found in {tableName} with {primaryKeyColumn} = {primaryKeyColumnValues}")
            print(f"No record found in {tableName} with {primaryKeyColumn} = {primaryKeyColumnValues}")
            return
        # Loop through cols and if not primary key then ask if want to update and get new value
        updateValues = {}
        for column in TABLE_COLUMN_CONFIG[tableName]:
            if column['name'] in primaryKeyColumn:
                continue
            currentValue = results[0][column['name']]
            newValue = input(f"{column['name']} ( {currentValue}): ")
            # skip on empty string implies no change to the value and keep the current value in the database
            if newValue.strip() == "":
                continue
            # Basic validation based on type
            if column['type'] == "integer":
                if not newValue.isdigit():
                    logging.error(f"Invalid input for {column['name']}. Expected an integer.")
                    print(f"*** ERROR *** Invalid input for {column['name']}. Expected an integer.")
                    return
                updateValues[column['name']] = int(newValue)
            elif column['type'] == "date":
                # Basic date validation (YYYY-MM-DD)
                try:
                    datetime.date.strptime(newValue, "%Y-%m-%d")
                except ValueError:
                    logging.error(f"Invalid input for {column['name']}. Expected a date in YYYY-MM-DD format.")
                    print(f"*** ERROR *** Invalid input for {column['name']}. Expected a date in YYYY-MM-DD format.")
                    return
                updateValues[column['name']] = newValue
            elif column['type'] == "enum":
                if newValue not in column['values']:
                    logging.error(f"Invalid input for {column['name']}. Expected one of: {', '.join(column['values'])}.")
                    print(f"*** ERROR *** Invalid input for {column['name']}. Expected one of: {', '.join(column['values'])}.")
                    return
                updateValues[column['name']] = newValue
            else:
                updateValues[column['name']] = newValue
        if len(updateValues) == 0:
            logging.info("No updates provided. Record remains unchanged.")
            print("No updates provided. Record remains unchanged.")
            return
        # Now update the record in the database
        _, error_code, error_msg = self.dao_mysql.update_record(tableName, primaryKeyColumn, primaryKeyColumnValues, updateValues)
        if error_code != 0:
            logging.error(f"Error updating record in {tableName}: {error_msg}")
            print(f"*** ERROR *** Updating record in {tableName}: ({error_msg})")
            return
        logging.info(f"Record in {tableName} updated successfully.")
        print(f"Record in {tableName} updated successfully.")


#------------------------------------------------------------------------------
# Function: handle_selection
#------------------------------------------------------------------------------
    def handle_selection(self, selection):
        """Handle the user's menu selection."""
        if not self.dao_mysql or not self.dao_neo4j:
            logging.error("MySQL or Neo4j DAO is not initialized.")
            print(f"*** ERROR *** MySQL or Neo4j DAO is not initialized.")
            return
        if selection == "1":
            logging.info("You selected: View Speakers & Sessions")
            speakerName = input("Enter speaker name : ")
            self.dao_mysql.print_sessions_report(speakerName)
        elif selection == "2":
            logging.info("You selected: View Attendees by Company")
            self.menu_print_attendees_by_company()
        elif selection == "3":
            logging.info("You selected: Add New Attendee")
            self.menu_add_attendee()
        elif selection == "4":
            logging.info("You selected: View Connected Attendees")
            self.menu_view_connected_attendees()
        elif selection == "5":
            logging.info("You selected: Add Attendee Connection")
            self.menu_add_attendee_connection()
        elif selection == "6":
            logging.info("You selected: View Rooms")
            self.menu_view_rooms()
        # Secret Group 1
        # Company
        elif selection == "88001":
            logging.info("Insert into Company")
            self.menu_insert_table("company")
        elif selection == "88002":
            logging.info("Select from Company")
            self.menu_select_table("company")
        elif selection == "88003":
            logging.info("Delete from Company")
            self.menu_delete_table("company")
        elif selection == "88004":
            logging.info("Update Company")
            self.menu_update_table("company")
        # Attendee
        elif selection == "88011":
            logging.info("Insert into Attendee")
            self.menu_insert_table("attendee")
        elif selection == "88012":
            logging.info("Select from Attendee")
            self.menu_select_table("attendee")
        elif selection == "88013":
            logging.info("Delete from Attendee")
            self.menu_delete_table("attendee")
        elif selection == "88014":
            logging.info("Update Attendee")
            self.menu_update_table("attendee")
        # Room
        elif selection == "88021":
            logging.info("Insert into Room")
            self.menu_insert_table("room")
        elif selection == "88022":
            logging.info("Select from Room")
            self.menu_select_table("room")
        elif selection == "88023":
            logging.info("Delete from Room")
            self.menu_delete_table("room")
        elif selection == "88024":
            logging.info("Update Room")
            self.menu_update_table("room")
        # Session
        elif selection == "88031":
            logging.info("Insert into Session")
            self.menu_insert_table("session")
        elif selection == "88032":
            logging.info("Select from Session")
            self.menu_select_table("session")
        elif selection == "88033":
            logging.info("Delete from Session")
            self.menu_delete_table("session")
        elif selection == "88034":
            logging.info("Update Session")
            self.menu_update_table("session")
        # Registration
        elif selection == "88041":
            logging.info("Insert into Registration")
            self.menu_insert_table("registration")
        elif selection == "88042":
            logging.info("Select from Registration")
            self.menu_select_table("registration")
        elif selection == "88043":
            logging.info("Delete from Registration")
            self.menu_delete_table("registration")
        elif selection == "88044":
            logging.info("Update Registration")
            self.menu_update_table("registration")


        # Secret Group 2
        # Secret option to exit the application
        # Attendee Select , and Delete
        elif selection == "99001":
            logging.info("Get Attendee with ID")
            Menu.menu_get_attendee(self)
        elif selection == "99002":
            logging.info("Delete Attendee with ID")
            Menu.menu_delete_attendee(self)
        elif selection == "99900":
            logging.info("Reset MySQL Database")
            Menu.menu_reset_mysql_database(self)
        elif selection == "99901":
            logging.info("Reset Neo4j Database")
            Menu.menu_reset_neo4j_database(self)
        elif selection.lower() == "x":
            logging.info("Exiting the application. Goodbye!")
            sys.exit(0)

#------------------------------------------------------------------------------
# Function: run
#------------------------------------------------------------------------------
    def run(self):
        """Run the menu loop to continuously display the menu and handle user input."""
        while True:
            self.display_menu()
            selection = input("Please select an option: ")
            self.handle_selection(selection)

#------------------------------------------------------------------------------
# Function: main
#------------------------------------------------------------------------------
def main():
    """Main function to initialize logging and start the application.
    This function sets up logging and serves as the entry point for the application.
    """
    # argparse to handle command line arguments for database connection details
    parser = argparse.ArgumentParser(description="A tool to migrate data from MySQL to Neo4j.")
    parser.add_argument("--mysql-host", required=False,default="localhost", help="MySQL host")
    parser.add_argument("--mysql-user", required=False,default="root", help="MySQL user")
    parser.add_argument("--mysql-password", required=False,default='root', help="MySQL password")
    parser.add_argument("--mysql-database", required=False,default='appdbproj', help="MySQL database")
    parser.add_argument("--neo4j-uri", required=False,default="bolt://localhost:7687", help="Neo4j URI")
    parser.add_argument("--neo4j-user", required=False,default="neo4j", help="Neo4j user")
    parser.add_argument("--neo4j-password", required=False,default="neo4jneo4j", help="Neo4j password")
    parser.add_argument("--neo4j-database", required=False,default="attendeeNetwork", help="Neo4j database")
    parser.add_argument("--log-level", required=False,default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    # debug level logging for testing
    parser.add_argument("--debug", action="store_true", help="Enable debug level logging")
    args = parser.parse_args()


    # Write logs to main.log and reset it at the start of each run.
    logging.basicConfig(
            level=getattr(logging, args.log_level.upper(), logging.INFO),
            # add file and function name and line number to the log messages for better debugging
            format="%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s",
            handlers=[
                logging.FileHandler("main.log", mode="w")
            ]
        )
    logging.info("Starting the application...")
    logging.debug("Debug mode is enabled.")

    # Connect to the databases and initialize the DAOs
    # Neo4j first because it is needed for the MySQL DAO to load connections from Neo4j into the temporary table
    dao_neo4j = DAO_Neo4j(args.neo4j_uri, args.neo4j_user, args.neo4j_password,args.neo4j_database)
    _,error_code,error_msg = dao_neo4j.connect()
    if error_code != 0:
        logging.error("Failed to connect to Neo4j database: (%s, %s)", error_code, error_msg)
        print(f"*** ERROR *** Failed to connect to Neo4j database: ({error_code}, \"{error_msg}\")")
        sys.exit(1)

    dao_mysql = DAO_MySQL(args.mysql_host, args.mysql_user, args.mysql_password, args.mysql_database, dao_neo4j=dao_neo4j)
    _, error_code, error_msg = dao_mysql.connect()
    if error_code != 0:
        logging.error("Failed to connect to MySQL database: (%s, %s)", error_code, error_msg)
        print(f"*** ERROR *** Failed to connect to MySQL database: ({error_code}, \"{error_msg}\")")
        sys.exit(1)


    menu = Menu(dao_mysql=dao_mysql, dao_neo4j=dao_neo4j)
    menu.run()

if __name__ == "__main__":
    main()
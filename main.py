#! /usr/bin/env python3
# source venv_wsl/bin/activate
#------------------------------------------------------------------------------
# File: main.py
# Description: Main application file for the Conference Management System.
# This file contains the implementation of the Data Access Objects (DAOs) for both Neo4j and MySQL databases
# as well as the Menu class to interact
#------------------------------------------------------------------------------

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
    def connect(self):
        """Establish a connection to the Neo4j database."""
        try:
            self.driver = neo4j.GraphDatabase.driver(uri = self.uri, 
                                                     auth = (self.user, 
                                                           self.password), 
                                                    database = self.database)
            logging.info(f"Successfully connected to Neo4j database: {self.database}.")
        except neo4j.exceptions.Neo4jError as err:
            logging.error(f"Error connecting to Neo4j: {err}")
            return None, err
        return self.driver, None
#------------------------------------------------------------------------------
# Function: reset_database
# ------------------------------------------------------------------------------
    def reset_database(self):
        """Reset the Neo4j database using the provided Cypher file."""
        try:
            print(f"Resetting Neo4j database using script: {neo4j_reset_file}")
            with open(neo4j_reset_file, 'r') as file:
                cypher_script = file.read()
            with self.driver.session() as session:
                session.run(cypher_script)
            logging.info("Neo4j database reset successfully.")
        except neo4j.exceptions.Neo4jError as err:
            logging.error(f"Error resetting Neo4j database: {err}")
            return None, err
        return None, None
        
#------------------------------------------------------------------------------
# Function: execute_query
#------------------------------------------------------------------------------
    def execute_query(self, query, parameters=None):
        """Execute a Cypher query and return the results."""
        if not self.driver:
            logging.error("No Neo4j connection established.")
            return None, "No connection"
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters)
                records = result.data()
                logging.debug(f"Query executed successfully: {query}")
                return records, None
        except neo4j.exceptions.Neo4jError as err:
            logging.error(f"Error executing query: {query}")
            if parameters:
                logging.error(f"With parameters: {parameters}")
            else:
                logging.error("No parameters provided for the query.")
            logging.error(f"Error executing query: {err}")
            return None, err
    
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
    def merge_attendee(self, attendeeID, attendeeName):
        """Merge an attendee node in the Neo4j database."""
        query = "MERGE (a:Attendee {AttendeeID: $attendeeID}) ON CREATE SET a.AttendeeName = $attendeeName RETURN a"
        parameters = {"attendeeID": attendeeID, "attendeeName": attendeeName}
        return self.execute_query(query, parameters)
#-------------------------------------------------------------------------------
# Function: get_all_attendees
#-------------------------------------------------------------------------------
    def get_all_attendees(self):
        """Get all attendees from the Neo4j database."""
        query = "MATCH (a:Attendee) RETURN a.AttendeeID"
        return self.execute_query(query, None)

#------------------------------------------------------------------------------
# Function: merge_connection
#------------------------------------------------------------------------------
    def merge_connection(self, attendeeID1, attendeeID2):
        """Merge a connection between two attendees in the Neo4j database."""
        query = """
        MATCH (a1:Attendee {AttendeeID: $attendeeID1}), (a2:Attendee {AttendeeID: $attendeeID2})
        MERGE (a1)-[:CONNECTED_TO]-(a2)
        RETURN a1, a2
        """
        parameters = {"attendeeID1": attendeeID1, "attendeeID2": attendeeID2}
        return self.execute_query(query, parameters)    

#------------------------------------------------------------------------------
# Function: delete_connection
#------------------------------------------------------------------------------
    def delete_connection(self, attendeeID1, attendeeID2):
        """Delete a connection between two attendees from the Neo4j database."""
        query = """
        MATCH (a1:Attendee {AttendeeID: $attendeeID1})-[r:CONNECTED_TO]-(a2:Attendee {AttendeeID: $attendeeID2})
        DELETE r
        """
        parameters = {"attendeeID1": attendeeID1, "attendeeID2": attendeeID2}
        return self.execute_query(query, parameters)
    
#------------------------------------------------------------------------------
# Function: delete_all_connections
#------------------------------------------------------------------------------
    def delete_all_connections(self):
        """Delete all connections from the Neo4j database."""
        query = "MATCH ()-[r:CONNECTED_TO]-() DELETE r"
        return self.execute_query(query)
    
#------------------------------------------------------------------------------
# Function: get_connected_attendees
#------------------------------------------------------------------------------
    def get_connected_attendees(self, attendeeID):
        """Get all attendees connected to a specific attendee."""
        query = f"""
        MATCH (a:Attendee {{AttendeeID: {attendeeID}}})-[:CONNECTED_TO]-(connected:Attendee)
        RETURN distinct connected.AttendeeID
        """
        parameters = {}
        return self.execute_query(query, parameters)
    
  
#------------------------------------------------------------------------------
# Function: check_connection_exists
#------------------------------------------------------------------------------
    def check_connection_exists(self, attendeeID1, attendeeID2):
        """Check if a connection exists between two attendees."""
        query = f"""
        MATCH (a1:Attendee {{AttendeeID: {attendeeID1}}})-[:CONNECTED_TO]-(a2:Attendee {{AttendeeID: {attendeeID2}}})
        RETURN a1, a2
        """
        parameters = {}
        return self.execute_query(query, parameters)
    

  
    

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
    def connect(self):
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
            return None, err
        return self.connection, None
    
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
    def execute_query(self, query, values=None):
        """Execute a SQL query and return the results."""
        if not self.connection:
            logging.error("No MySQL connection established.")
            return None, "No connection"
        try:
            cursor = self.connection.cursor()
            if values:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
            logging.debug(f"Query executed successfully: {query}")
            return results, None
        except mysql.Error as err:
            logging.error(f"Error executing query: {query}")
            if values:
                logging.error(f"With values: {values}")
            else:
                logging.error("No values provided for the query.")
            logging.error(f"Error executing query: {err}")
            return None, err
    # company table CRUD operations
    # CREATE TABLE company (
    #companyID INT PRIMARY KEY,
    #companyName VARCHAR(100) NOT NULL,
    #industry VARCHAR(60) NOT NULL
    #);
#------------------------------------------------------------------------------
# Function: reset_database
#------------------------------------------------------------------------------
    def reset_database(self):
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
                    cursor.execute(statement)
            # Using autocommit mode, so no need to commit after executing the script
            #self.connection.commit()
            logging.info("MySQL database reset successfully.")
        except mysql.Error as err:
            logging.error(f"Error resetting MySQL database: {err}")
            return None, err
        return None, None

#------------------------------------------------------------------------------
# Function: create_relationship_attendees_temporary_table
#------------------------------------------------------------------------------
    def create_relationship_attendees_temporary_table(self):
        """Create a temporary table to hold attendee connections."""
        query = """
        CREATE TEMPORARY TABLE IF NOT EXISTS attendee_connections (
            connectedAttendeeId INT,
            PRIMARY KEY (connectedAttendeeId)
        )
        """
        return self.execute_query(query, None)
    
#------------------------------------------------------------------------------
# Function: add_attendee_connection
#------------------------------------------------------------------------------
    def add_attendee_connection(self, attendeeID1):
        """Add a connection between two attendees in the temporary table."""
        # This database shows “connections” between attendees. Any attendee (that is in the MySQL database) can have a CONNECTED_TO relationship with any other attendee.
        # The direction of the CONNECTED_TO relationship is unimportant.
        # Check if the connection already exists in either direction
        logging.info(f"Adding connection for AttendeeID: {attendeeID1}")
        check_query = """SELECT 1 FROM attendee_connections 
                         WHERE (connectedAttendeeId = %s)"""
        
        check_values = (attendeeID1,)
        existing_connection, err = self.execute_query(check_query, check_values)
        if existing_connection:
            logging.info("Connection already exists.")
            return None, "Connection already exists"
        # If the connection does not exist, insert it into the table    
        query = "INSERT INTO attendee_connections (connectedAttendeeId) VALUES (%s)"
        values = (attendeeID1,)
        self.execute_query(query, values)
        logging.info(f"Connection added for AttendeeID: {attendeeID1}")
        return None, None
    
#------------------------------------------------------------------------------
# Function: delete_attendee_connection
#------------------------------------------------------------------------------
    def delete_attendee_connection(self, connectedAttendeeId):
        """Delete a connection between two attendees from the temporary table."""
        query = """DELETE FROM attendee_connections 
                   WHERE (connectedAttendeeId = %s )"""
        values = (connectedAttendeeId,)
        self.execute_query(query, values)
        return None, None
    
#------------------------------------------------------------------------------
# Function: delete_all_attendee_connections
#------------------------------------------------------------------------------
    def delete_all_attendee_connections(self):
        """Delete all connections from the temporary table."""
        query = "DELETE FROM attendee_connections"
        self.execute_query(query)
        return None, None
#-------------------------------------------------------------------------------
# Function: get_all_attendee_connections
#------------------------------------------------------------------------------
    def get_all_attendee_connections(self):
        """Get all connections from the temporary table."""
        query = "SELECT connectedAttendeeId FROM attendee_connections"
        return self.execute_query(query, None)

#------------------------------------------------------------------------------
# Function: get_connection_from_neo4j
#------------------------------------------------------------------------------
    def get_connection_from_neo4j(self, attendeeID):
        """Get all attendees connected to a specific attendee from Neo4j."""

        if not self.dao_neo4j:
            logging.error("Neo4j DAO is not initialized.")
            return None, "No Neo4j DAO"
        _, err = self.create_relationship_attendees_temporary_table()
        if err:
            logging.error("Error creating relationship attendees temporary table: %s", err)
            print(f"*** ERROR *** Creating relationship attendees temporary table: ({err})")
            return None, err
        # Get connected attendees from Neo4j and return the results
        results, err = self.dao_neo4j.get_connected_attendees(attendeeID)
        if err:
            logging.error(f"Error getting connected attendees from Neo4j: {err}")
            return None, err
        # now populate the temporary table with the results
        self.delete_all_attendee_connections()
        for record in results:
            connectedAttendeeID = record['connected.AttendeeID']
            logging.info(f"Connected AttendeeID: {connectedAttendeeID} for AttendeeID: {attendeeID}")
            self.add_attendee_connection(connectedAttendeeID)
        return results, None


#------------------------------------------------------------------------------
# Function: create_company
#------------------------------------------------------------------------------
    def create_company(self, companyID, companyName, industry):
        """Create a new company record in the database."""
        query = "INSERT INTO company (companyID, companyName, industry) VALUES (%s, %s, %s)"
        values = (companyID, companyName, industry)
        return self.execute_query(query, values)
    
#------------------------------------------------------------------------------
# Function: read_company
#------------------------------------------------------------------------------
    def read_company(self, companyID):
        """Read a company record from the database."""
        query = "SELECT companyID, companyName, industry FROM company WHERE companyID = %s"
        values = (companyID,)
        return self.execute_query(query, values)
    
#------------------------------------------------------------------------------
# Function: read_all_companies
#------------------------------------------------------------------------------
    def read_all_companies(self,LIMIT=100):
        """Read all company records from the database."""
        query = f"SELECT companyID, companyName, industry FROM company LIMIT {LIMIT}"
        return self.execute_query(query)
    
#------------------------------------------------------------------------------
# Function: update_company
#------------------------------------------------------------------------------
    def update_company(self, companyID, companyName, industry):
        """Update a company record in the database."""
        query = "UPDATE company SET companyName = %s, industry = %s WHERE companyID = %s"
        values = (companyName, industry, companyID)
        return self.execute_query(query, values)
    
#------------------------------------------------------------------------------
# Function: delete_company
#------------------------------------------------------------------------------
    def delete_company(self, companyID):
        """Delete a company record from the database."""
        query = "DELETE FROM company WHERE companyID = %s"
        values = (companyID,)
        return self.execute_query(query, values)
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
    def create_attendee(self, attendeeID, attendeeName, attendeeDOB, attendeeGender, attendeeCompanyID):
        """Create a new attendee record in the database."""
        query = "INSERT INTO attendee (attendeeID, attendeeName, attendeeDOB, attendeeGender, attendeeCompanyID) VALUES (%s, %s, %s, %s, %s)"
        values = (attendeeID, attendeeName, attendeeDOB, attendeeGender, attendeeCompanyID)
        return self.execute_query(query, values)
    
#------------------------------------------------------------------------------
# Function: read_attendee
#------------------------------------------------------------------------------
    def read_attendee(self, attendeeID):
        """Read an attendee record from the database."""
        query = "SELECT attendeeID, attendeeName, attendeeDOB, attendeeGender, attendeeCompanyID FROM attendee WHERE attendeeID = %s"
        values = (attendeeID,)
        return self.execute_query(query, values)
    
#------------------------------------------------------------------------------
# Function: read_all_attendees
#------------------------------------------------------------------------------
    def read_all_attendees(self,LIMIT=100):
        """Read all attendee records from the database."""
        query = f"SELECT attendeeID, attendeeName, attendeeDOB, attendeeGender, attendeeCompanyID FROM attendee LIMIT {LIMIT}"
        return self.execute_query(query)
    
#------------------------------------------------------------------------------
# Function: update_attendee
#------------------------------------------------------------------------------
    def update_attendee(self, attendeeID, attendeeName, attendeeDOB, attendeeGender, attendeeCompanyID):
        """Update an attendee record in the database."""
        query = "UPDATE attendee SET attendeeName = %s, attendeeDOB = %s, attendeeGender = %s, attendeeCompanyID = %s WHERE attendeeID = %s"
        values = (attendeeName, attendeeDOB, attendeeGender, attendeeCompanyID, attendeeID)
        return self.execute_query(query, values)
    
#------------------------------------------------------------------------------
# Function: delete_attendee
#------------------------------------------------------------------------------
    def delete_attendee(self, attendeeID):
        """Delete an attendee record from the database."""
        query = "DELETE FROM attendee WHERE attendeeID = %s"
        values = (attendeeID,)
        return self.execute_query(query, values)

    #    
    #   CREATE TABLE room (
    #       roomID INT PRIMARY KEY,
    #       roomName VARCHAR(80) NOT NULL,
    #       capacity INT NOT NULL
    #   );
    
#------------------------------------------------------------------------------
# Function: create_room
#------------------------------------------------------------------------------
    def create_room(self, roomID, roomName, capacity):
        """Create a new room record in the database."""
        query = "INSERT INTO room (roomID, roomName, capacity) VALUES (?, ?, ?)"
        values = (roomID, roomName, capacity)
        return self.execute_query(query, values)
    
#------------------------------------------------------------------------------
# Function: read_room
#------------------------------------------------------------------------------
    def read_room(self, roomID):
        """Read a room record from the database."""
        query = "SELECT roomID, roomName, capacity FROM room WHERE roomID = ?"
        values = (roomID,)
        return self.execute_query(query, values)
    
#------------------------------------------------------------------------------
# Function: read_all_rooms
#------------------------------------------------------------------------------
    def read_all_rooms(self,LIMIT=100):
        """Read all room records from the database."""
        query = f"SELECT roomID, roomName, capacity FROM room LIMIT {LIMIT}"
        return self.execute_query(query)
    
#------------------------------------------------------------------------------
# Function: update_room
#------------------------------------------------------------------------------
    def update_room(self, roomID, roomName, capacity):
        """Update a room record in the database."""
        query = "UPDATE room SET roomName = ?, capacity = ? WHERE roomID = ?"
        values = (roomName, capacity, roomID)
        return self.execute_query(query, values)
    
#------------------------------------------------------------------------------
# Function: delete_room
#------------------------------------------------------------------------------
    def delete_room(self, roomID):
        """Delete a room record from the database."""
        query = "DELETE FROM room WHERE roomID = ?"
        values = (roomID,)
        return self.execute_query(query, values)
    
    #   CREATE TABLE session (
    #       sessionID INT PRIMARY KEY,
    #       sessionTitle VARCHAR(150) NOT NULL,
    #       speakerName VARCHAR(100) NOT NULL,
    #       sessionDate DATE NOT NULL,
    #       roomID INT NOT NULL,
    #       FOREIGN KEY (roomID) REFERENCES room(roomID)
    #   );

#------------------------------------------------------------------------------
# Function: create_session
#------------------------------------------------------------------------------
    def create_session(self, sessionID, sessionTitle, speakerName, sessionDate, roomID):
        """Create a new session record in the database."""
        query = "INSERT INTO session (sessionID, sessionTitle, speakerName, sessionDate, roomID) VALUES (?, ?, ?, ?, ?)"
        values = (sessionID, sessionTitle, speakerName, sessionDate, roomID)
        return self.execute_query(query, values)

#------------------------------------------------------------------------------
# Function: read_session
#------------------------------------------------------------------------------
    def read_session(self, sessionID):
        """Read a session record from the database."""
        query = "SELECT sessionID, sessionTitle, speakerName, sessionDate, roomID FROM session WHERE sessionID = ?"
        values = (sessionID,)
        return self.execute_query(query, values)

#------------------------------------------------------------------------------
# Function: read_all_sessions
#------------------------------------------------------------------------------
    def read_all_sessions(self,LIMIT=100):
        """Read all session records from the database."""
        query = f"SELECT sessionID, sessionTitle, speakerName, sessionDate, roomID FROM session LIMIT {LIMIT}"
        return self.execute_query(query)

#------------------------------------------------------------------------------
# Function: update_session
#------------------------------------------------------------------------------
    def update_session(self, sessionID, sessionTitle, speakerName, sessionDate, roomID):
        """Update a session record in the database."""
        query = "UPDATE session SET sessionTitle = ?, speakerName = ?, sessionDate = ?, roomID = ? WHERE sessionID = ?"
        values = (sessionTitle, speakerName, sessionDate, roomID, sessionID)
        return self.execute_query(query, values)

#------------------------------------------------------------------------------
# Function: delete_session
#------------------------------------------------------------------------------
    def delete_session(self, sessionID):
        """Delete a session record from the database."""
        query = "DELETE FROM session WHERE sessionID = ?"
        values = (sessionID,)
        return self.execute_query(query, values)

    #   CREATE TABLE registration (
    #       registrationID INT PRIMARY KEY,
    #       attendeeID INT NOT NULL,
    #       sessionID INT NOT NULL,
    #       registeredAt DATETIME NOT NULL,
    #       FOREIGN KEY (attendeeID) REFERENCES attendee(attendeeID),
    #       FOREIGN KEY (sessionID) REFERENCES session(sessionID)
    #   );

#------------------------------------------------------------------------------
# Function: create_registration
#------------------------------------------------------------------------------
    def create_registration(self, registrationID, attendeeID, sessionID, registeredAt):
        """Create a new registration record in the database."""
        query = "INSERT INTO registration (registrationID, attendeeID, sessionID, registeredAt) VALUES (?, ?, ?, ?)"
        values = (registrationID, attendeeID, sessionID, registeredAt)
        return self.execute_query(query, values)
    
#------------------------------------------------------------------------------
# Function: read_registration
#------------------------------------------------------------------------------
    def read_registration(self, registrationID):
        """Read a registration record from the database."""
        query = "SELECT registrationID, attendeeID, sessionID, registeredAt FROM registration WHERE registrationID = ?"
        values = (registrationID,)
        return self.execute_query(query, values)
    
#------------------------------------------------------------------------------
# Function: read_all_registrations
#------------------------------------------------------------------------------
    def read_all_registrations(self,LIMIT=100):
        """Read all registration records from the database."""
        query = f"SELECT registrationID, attendeeID, sessionID, registeredAt FROM registration LIMIT {LIMIT}"
        return self.execute_query(query)
    
#------------------------------------------------------------------------------
# Function: update_registration
#------------------------------------------------------------------------------
    def update_registration(self, registrationID, attendeeID, sessionID, registeredAt):
        """Update a registration record in the database."""
        query = "UPDATE registration SET attendeeID = ?, sessionID = ?, registeredAt = ? WHERE registrationID = ?"
        values = (attendeeID, sessionID, registeredAt, registrationID)
        return self.execute_query(query, values)

#------------------------------------------------------------------------------
# Function: delete_registration
#------------------------------------------------------------------------------
    def delete_registration(self, registrationID):
        """Delete a registration record from the database."""
        query = "DELETE FROM registration WHERE registrationID = ?"
        values = (registrationID,)
        return self.execute_query(query, values)

    # -- Report sessions by speaker

#------------------------------------------------------------------------------
# Function: report_sessions_by_speaker
#------------------------------------------------------------------------------
    def report_sessions_by_speaker(self, speakerName):
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
        return self.execute_query(query, values)
    
#------------------------------------------------------------------------------
# Function: print_sessions_report
#------------------------------------------------------------------------------
    def print_sessions_report(self, speakerName):
        """Print a report of sessions by a specific speaker."""
        results, err = self.report_sessions_by_speaker(speakerName)
        # if there is sql error
        print(f"\nSession Details For : {speakerName}")
        print("-" * 40)
        if err:
            logging.error("Failed to generate sessions report.")
            print(f"Error generating report: {err}")
            return
        # if there are no results found for the speaker
        if results is None or len(results) == 0:
            logging.info(f"No speakers found for that name")
            print(f"No sessions found for speaker: {speakerName}")
            return
        # print the results in a readable format
        for row in results:
            print(f"{row['speakerName']} | {row['sessionTitle']} | {row['roomName']}")
    
    # Report attendees by company
    # Input: company id
    # Output:
    # When a valid (numeric) company ID is entered, the company name is shown and the following details are shown for each attendee from that company:
    #The name of each attendee
    #The date of birth of each attendee
    #The title of the session the attendee attended
    #The name of the speaker at the session the attendee attended
    #The name of the room the session was held in. 

#------------------------------------------------------------------------------
# Function: report_attendees_by_company
#------------------------------------------------------------------------------
    def report_attendees_by_company(self, companyID):
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
    def report_connected_attendees(self, attendeeID):
        """Report attendees connected to a specific attendee."""
        query = f"""SELECT attendeeID, attendeeName FROM attendee WHERE attendeeID IN
            (SELECT connectedAttendeeId from attendee_connections WHERE connectedAttendeeId <> %s) ORDER BY attendeeName"""
        return self.execute_query(query, (attendeeID,))

#------------------------------------------------------------------------------
# Function: print_attendees_report
#------------------------------------------------------------------------------
    def print_attendees_report(self, companyID, companyName=""):
        """Print a report of attendees by a specific company."""
        results, err = self.report_attendees_by_company(companyID)
        if err:
            logging.error("Failed to generate attendees report.")
            return None, err
        if results is None or len(results) == 0:
            logging.info(f"No attendees found for {companyName}")
            print(f"{companyName}  Attendees")
            print(f"No attendees found for  {companyName}")
            return results, None
        print(f"{companyName}  Attendees")
        for row in results:
            print(f"{row['attendeeName']} | {row['attendeeDOB']} | {row['sessionTitle']} | {row['speakerName']} | {row['roomName']}")
        return results, None
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
            companyResults, err = self.dao_mysql.read_company(companyID)
            if err:
                logging.error("Error checking if company exists: %s", err)
                continue
            if not companyResults or len(companyResults) == 0:
                logging.info(f"No company found with ID: {companyID}")
                print(f"Company with ID  {companyID} doesn't exist.")
                continue
            companyName = companyResults[0]['companyName'] # Assuming the company name is in the 'companyName' column
            report_attendees_by_company, err = self.dao_mysql.report_attendees_by_company(companyID)
            if err:
                logging.error("Failed to generate attendees report.")
                return None, err
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
            attendeeResults, err = self.dao_mysql.read_attendee(attendeeID)
            if err:
                logging.error("Error checking if attendee exists: %s", err)
                continue
            if not attendeeResults or len(attendeeResults) == 0:
                logging.info(f"No attendee found with ID: {attendeeID}")
                print(f"Attendee with ID  {attendeeID} doesn't exist.")
                continue
            print(f"Attendee Details for ID: {attendeeID}")
            print("-" * 40)
            for attendee in attendeeResults:
                print(f"Attendee ID: {attendee[0]}")
                print(f"Name : {attendee[1]}")
                print(f"DOB : {attendee[2]}")
                print(f"Gender : {attendee[3]}")
                print(f"Company ID : {attendee[4]}")
                print("-" * 40)
            break
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
            attendeeResults, err = self.dao_mysql.read_attendee(attendeeID)
            if err:
                logging.error("Error checking if attendee exists: %s", err)
                continue
            if not attendeeResults or len(attendeeResults) == 0:
                logging.info(f"No attendee found with ID: {attendeeID}")
                print(f"Attendee with ID  {attendeeID} doesn't exist.")
                continue
            confirm = input(f"Are you sure you want to delete attendee with ID {attendeeID}? (y/n): ")
            if confirm.lower() == "y":
                _, err = self.dao_mysql.delete_attendee(attendeeID)
                if err:
                    logging.error("Error deleting attendee: %s", err)
                    print(f"Error deleting attendee: {err}")
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
        existingAttendee, err = self.dao_mysql.read_attendee(attendeeId)
        if err:
            logging.error("Error checking if attendee exists: %s", err)
            print(f'*** ERROR *** Error checking if attendee exists: ({err.args[0]}, "{err.args[1]}")')
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
        companyResults, err = self.dao_mysql.read_company(attendeeCompanyID)
        if err:
            logging.error("Error checking if company exists: %s", err)
            print(f'*** ERROR *** Company ID: {attendeeCompanyID} - Error checking if company exists: ({err.args[0]}, "{err.args[1]}")')
            return
        if not companyResults or len(companyResults) == 0:
            logging.info(f"No company found with ID: {attendeeCompanyID}")
            print(f"*** ERROR *** Company ID: {attendeeCompanyID} does not exist")
            return
        # Now enter New attendee into the database
        _, err = self.dao_mysql.create_attendee(attendeeId, attendeeName, attendeeDOB, attendeeGender, attendeeCompanyID)
        if err:
            logging.error("Error creating new attendee: %s", err)
            print(f'*** ERROR *** ({err.args[0]}, "{err.args[1]}")')
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
            attendeeResults, err = self.dao_mysql.read_attendee(attendeeId)
            if err:
                logging.error("Error checking if attendee exists: %s", err)
                print(f"*** ERROR *** Invalid attendee ID")
                # Better error but above is as per requirements
                #print(f'*** ERROR *** Error checking if attendee exists: ({err.args[0]}, "{err.args[1]}")')
                continue
            if not attendeeResults or len(attendeeResults) == 0:
                logging.info(f"No attendee found with ID: {attendeeId}")
                print(f"*** ERROR *** Attendee does not exist")
                # exit the loop and return to main menu
                break
            attendeeName = attendeeResults[0]['attendeeName']  # Assuming the attendee name is in the 'name' column
            logging.info(f"Attendee found: {attendeeName} (ID: {attendeeId})")
            print(f"Attendee Name: {attendeeName}")
            # Create a temporary table in MySQL to hold the connected attendees for this attendee   
            # Get connected attendees from Neo4j and populate the temporary table in MySQL
            logging.info(f"Getting connected attendees for {attendeeName} (ID: {attendeeId}) from Neo4j and populating temporary table in MySQL")
            logging.info("Creating relationship attendees temporary table in MySQL")

            # Delete any existing connections for this attendee in the temporary table to avoid duplicates
            logging.info("Deleting existing attendee connections in the temporary table")

            _, err = self.dao_mysql.delete_all_attendee_connections()
            if err:
                logging.error("Error deleting existing attendee connections: %s", err)
                print(f"*** ERROR *** Deleting existing attendee connections: ({err.args[0]}, \"{err.args[1]}\")")
                break
            logging.info("Getting connections from Neo4j and inserting into temporary table in MySQL")
            results, err = self.dao_mysql.get_connection_from_neo4j(attendeeId)
            if err:
                logging.error("Error getting connections from Neo4j: %s", err)
                print(f"*** ERROR *** Getting connections from Neo4j: ({err.args[0]}, \"{err.args[1]}\")")
                break
            print("Results: ", results)
            report, err = self.dao_mysql.report_connected_attendees(attendeeId)
            if err:
                logging.error("Error generating connected attendees report: %s", err)
                print(f"*** ERROR *** Generating connected attendees report: ({err.args[0]}, \"{err.args[1]}\")")
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
            attendeeId1 = input("Enter Attendee ID 1 : ")
            attendeeId2 = input("Enter Attendee ID 2 : ")
            # Check if attendee IDs are numeric
            if not attendeeId1.isdigit() or not attendeeId2.isdigit():
                logging.error("Invalid input. Please enter numeric attendee IDs.")
                print(f"*** ERROR *** Attendee IDs must be numbers")
                continue
            # Check if both attendees ID are the same
            if attendeeId1 == attendeeId2:
                logging.error("Invalid input. Attendee IDs cannot be the same.")
                print(f"*** ERROR *** An attendee cannot connect to him/herself")
                continue
            ## Check if attendee ID 1 exists
            attendeeResults1, err = self.dao_mysql.read_attendee(attendeeId1)
            if err:
                logging.error("Error checking if attendee 1 exists: %s", err)
                print(f"*** ERROR *** Attendee ID 1: {attendeeId1} - Error checking if attendee exists: ({err.args[0]}, \"{err.args[1]}\"))")
                continue
            if not attendeeResults1 or len(attendeeResults1) == 0:
                logging.info(f"No attendee found with ID: {attendeeId1}")
                print(f"*** ERROR *** One or both attendee ID's do not exist")
                continue
            # Check if attendee ID 2 exists
            attendeeResults2, err = self.dao_mysql.read_attendee(attendeeId2)
            if err:
                logging.error("Error checking if attendee 2 exists: %s", err)
                print(f"*** ERROR *** Attendee ID 2: {attendeeId2} - Error checking if attendee exists: ({err.args[0]}, \"{err.args[1]}\"))")
                continue
            if not attendeeResults2 or len(attendeeResults2) == 0:
                logging.info(f"No attendee found with ID: {attendeeId2}")
                print(f"*** ERROR *** One or both attendee ID's do not exist")
                continue
            # Check if the connection already exists in Neo4j
            connectionResults, err = self.dao_neo4j.check_connection_exists(attendeeId1, attendeeId2)
            if err:
                logging.error("Error checking if connection exists in Neo4j: %s", err)
                print(f"*** ERROR *** Checking connection in Neo4j: ({err.args[0]}, \"{err.args[1]}\"))")
                continue
            if connectionResults and len(connectionResults) > 0:
                logging.info(f"Connection already exists between attendees {attendeeId1} and {attendeeId2}")
                print(f"*** ERROR *** Connection already exists between attendees {attendeeId1} and {attendeeId2}")
                continue
            # Add the connection to Neo4j
            _, err = self.dao_neo4j.merge_connection(attendeeId1, attendeeId2)
            if err:
                logging.error("Error adding connection to Neo4j: %s", err)
                print(f"*** ERROR *** Adding connection to Neo4j: ({err.args[0]}, \"{err.args[1]}\"))")
                break
            logging.info(f"Connection successfully added between attendees {attendeeId1} and {attendeeId2}")
            print(f"Attendee {attendeeId1} is now connected to {attendeeId2}")
            break


#------------------------------------------------------------------------------
# Function: menu_view_rooms
#------------------------------------------------------------------------------
    def menu_view_rooms(self):
        """Menu option to view all rooms."""
        # Populate only once
        if self.view_rooms is None:
            self.view_rooms = []

            results, err = self.dao_mysql.read_all_rooms()
            if err:
                logging.error("Error retrieving rooms: %s", err)
                print(f"*** ERROR *** Retrieving rooms: ({err.args[0]}, \"{err.args[1]}\")")
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
            _, err = self.dao_mysql.reset_database()
            if err:
                logging.error("Error resetting the MySQL database: %s", err)
                print(f"*** ERROR *** Resetting the MySQL database: ({err.args[0]}, \"{err.args[1]}\")")
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
            _, err = self.dao_neo4j.reset_database()
            if err:
                logging.error("Error resetting the Neo4j database: %s", err)
                print(f"*** ERROR *** Resetting the Neo4j database: ({err.args[0]}, \"{err.args[1]}\")")
                return
            logging.info("Neo4j database reset successfully.")
            print("Neo4j database has been reset successfully.")
        else:
            logging.info("Neo4j database reset cancelled.")
            print("Neo4j database reset cancelled.") 
#------------------------------------------------------------------------------
# Function: handle_selection
#------------------------------------------------------------------------------
    def handle_selection(self, selection):
        """Handle the user's menu selection."""
        if selection == "1":
            logging.info("You selected: View Speakers & Sessions")
            if not self.dao_mysql:
                logging.error("MySQL DAO is not initialized.")
                return
            speakerName = input("Enter speaker name : ")
            self.dao_mysql.print_sessions_report(speakerName)
        elif selection == "2":
            logging.info("You selected: View Attendees by Company")
            if not self.dao_mysql:
                logging.error("MySQL DAO is not initialized.")
                return
            self.menu_print_attendees_by_company()
        elif selection == "3":
            logging.info("You selected: Add New Attendee")
            if not self.dao_mysql:
                logging.error("MySQL DAO is not initialized.")
                return
            self.menu_add_attendee()
        elif selection == "4":
            if not self.dao_mysql or not self.dao_neo4j:
                logging.error("MySQL or Neo4j DAO is not initialized.")
                return
            self.menu_view_connected_attendees()
        elif selection == "5":
            logging.info("You selected: Add Attendee Connection")
            if not self.dao_mysql or not self.dao_neo4j:
                logging.error("MySQL or Neo4j DAO is not initialized.")
                return
            self.menu_add_attendee_connection()
        elif selection == "6":
            logging.info("You selected: View Rooms")
            self.menu_view_rooms()
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
    parser.add_argument("--neo4j-database", required=False,default="attendeenetwork", help="Neo4j database")
    parser.add_argument("--log-level", required=False,default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    parser.add_argument("--log-file", required=False,default="app.log", help="Log file path")
    # debug level logging for testing
    parser.add_argument("--debug", action="store_true", help="Enable debug level logging")
    args = parser.parse_args()


    # Keep logging simple for now , log to file and optionally to console
    logging.basicConfig(
            level=getattr(logging, args.log_level.upper(), logging.INFO),
            # add file and function name and line number to the log messages for better debugging
            format="%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s",
            handlers=[
                logging.FileHandler(args.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
    logging.info("Starting the application...")
    logging.debug("Debug mode is enabled.")

    # Connect to the databases and initialize the DAOs
    # Neo4j first because it is needed for the MySQL DAO to load connections from Neo4j into the temporary table
    dao_neo4j = DAO_Neo4j(args.neo4j_uri, args.neo4j_user, args.neo4j_password,args.neo4j_database)
    _, err = dao_neo4j.connect()
    if err:
        logging.error("Failed to connect to Neo4j database.")
        sys.exit(1)

    dao_mysql = DAO_MySQL(args.mysql_host, args.mysql_user, args.mysql_password, args.mysql_database, dao_neo4j=dao_neo4j)
    _, err = dao_mysql.connect()
    if err:
        logging.error("Failed to connect to MySQL database.")
        sys.exit(1)


    menu = Menu(dao_mysql=dao_mysql, dao_neo4j=dao_neo4j)
    menu.run()

if __name__ == "__main__":
    main()
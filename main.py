#! /usr/bin/env python3
#------------------------------------------------------------------------------
# File: main.py
# Description: Main application file for the Conference Management System.
# This file contains the implementation of the Data Access Objects (DAOs) for both Neo4j and MySQL databases
# as well as the Menu class to interact
#------------------------------------------------------------------------------
import logging
import subprocess
import sys
import argparse

# TODO 
# 1. When adding attendee ensure that it is added in neo4j as well as mysql, and that the connection is created in neo4j for the new attendee and any existing attendees that are connected to it in mysql
# 2. When deleting attendee ensure that it is deleted in neo4j as well as mysql, and that any connections in neo4j are also deleted for the attendee

# Install the mysql-connector-python package if it's not already installed
try:
    import mysql.connector as mysql
except ImportError:
    # Try to install the mysql-connector-python package if it's not already installed
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mysql-connector-python"])
    import mysql.connector as mysql
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
    def __init__(self, uri, user, password):
        self.uri = uri
        self.user = user
        self.password = password
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
            self.driver = neo4j.GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            logging.info("Successfully connected to Neo4j database.")
        except neo4j.exceptions.Neo4jError as err:
            logging.error(f"Error connecting to Neo4j: {err}")
            return None, err
        return self.driver, None
    
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
        query = """
        MATCH (a:Attendee {AttendeeID: $attendeeID})-[:CONNECTED_TO]-(connected:Attendee)
        RETURN connected.AttendeeID AS AttendeeID, connected.AttendeeName AS AttendeeName
        """
        parameters = {"attendeeID": attendeeID}
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
                database=self.database
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
# Function: create_relationship_attendees_temporary_table
#------------------------------------------------------------------------------
    def create_relationship_attendees_temporary_table(self):
        """Create a temporary table to hold attendee connections."""
        query = """
        CREATE TEMPORARY TABLE IF NOT EXISTS attendee_connections (
            attendeeID1 INT,
            attendeeID2 INT,
            PRIMARY KEY (attendeeID1, attendeeID2)
        )
        """
        return self.execute_query(query)
    
#------------------------------------------------------------------------------
# Function: add_attendee_connection
#------------------------------------------------------------------------------
    def add_attendee_connection(self, attendeeID1, attendeeID2):
        """Add a connection between two attendees in the temporary table."""
        # This database shows “connections” between attendees. Any attendee (that is in the MySQL database) can have a CONNECTED_TO relationship with any other attendee.
        # The direction of the CONNECTED_TO relationship is unimportant.
        # Check if the connection already exists in either direction
        check_query = """SELECT 1 FROM attendee_connections 
                         WHERE (attendeeID1 = %s AND attendeeID2 = %s)
                            OR (attendeeID1 = %s AND attendeeID2 = %s)"""
        
        check_values = (attendeeID1, attendeeID2, attendeeID2, attendeeID1)
        existing_connection, err = self.execute_query(check_query, check_values)
        if existing_connection:
            logging.info("Connection already exists.")
            return None, "Connection already exists"
        # If the connection does not exist, insert it into the table    
        query = "INSERT INTO attendee_connections (attendeeID1, attendeeID2) VALUES (%s, %s)"
        values = (attendeeID1, attendeeID2)
        self.execute_query(query, values)
        return None, None
    
#------------------------------------------------------------------------------
# Function: delete_attendee_connection
#------------------------------------------------------------------------------
    def delete_attendee_connection(self, attendeeID1, attendeeID2):
        """Delete a connection between two attendees from the temporary table."""
        query = """DELETE FROM attendee_connections 
                   WHERE (attendeeID1 = %s AND attendeeID2 = %s)
                      OR (attendeeID1 = %s AND attendeeID2 = %s)"""
        values = (attendeeID1, attendeeID2, attendeeID2, attendeeID1)
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

#------------------------------------------------------------------------------
# Function: get_connection_from_neo4j
#------------------------------------------------------------------------------
    def get_connection_from_neo4j(self, attendeeID):
        """Get all attendees connected to a specific attendee from Neo4j."""
        if not self.dao_neo4j:
            logging.error("Neo4j DAO is not initialized.")
            return None, "No Neo4j DAO"
        # Get connected attendees from Neo4j and return the results
        results, err = self.dao_neo4j.get_connected_attendees(attendeeID)
        if err:
            logging.error(f"Error getting connected attendees from Neo4j: {err}")
            return None, err
        # now populate the temporary table with the results
        self.delete_all_attendee_connections()
        for record in results:
            connectedAttendeeID = record["AttendeeID"]
            self.add_attendee_connection(attendeeID, connectedAttendeeID)


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
        query = """SELECT speakerName,
                  sessionTitle,
                  R.roomName
           FROM session AS SES
           INNER JOIN room AS R ON SES.roomID = R.roomID
           WHERE speakerName LIKE %s
           ORDER BY speakerName, sessionTitle, roomName"""
        values = (f"%{speakerName}%",)
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
        for speaker, session, room in results:
            print(f"{speaker} | {session} | {room}")
    
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
        for attendee, dob, session, speaker, room in results:
            print(f"{attendee} | {dob} | {session} | {speaker} | {room}")
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
            companyName = companyResults[0][1]  # Assuming the company name is in the second column
            result,err =  self.dao_mysql.print_attendees_report(companyID, companyName)
            print(result,len(result))
            if err or result is  None or len(result) == 0:
                logging.info(f"No attendees found for company ID: {companyID}")
                continue
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
        if not attendeeId.isdigit():
            logging.error("Invalid input. Please enter a numeric attendee ID.")
            print(f"*** ERROR *** Attendee ID: {attendeeId} is not a valid number")
            return
        # see if attendee already exists
        existingAttendee, err = self.dao_mysql.read_attendee(attendeeId)
        if err:
            logging.error("Error checking if attendee exists: %s", err)
            print(f"*** ERROR *** Error checking if attendee exists: {err}")
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
            print(f"*** ERROR *** Company ID: {attendeeCompanyID} - Error checking if company exists: {err}")
            return
        if not companyResults or len(companyResults) == 0:
            logging.info(f"No company found with ID: {attendeeCompanyID}")
            print(f"*** ERROR *** Company ID: {attendeeCompanyID} does not exist")
            return
        # Now enter New attendee into the database
        _, err = self.dao_mysql.create_attendee(attendeeId, attendeeName, attendeeDOB, attendeeGender, attendeeCompanyID)
        if err:
            logging.error("Error creating new attendee: %s", err)
            print(f"*** ERROR *** {err}")
            return
        logging.info(f"Attendee {attendeeName} created successfully with ID: {attendeeId}")
        print(f"Attendee successfully added")
        return
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
            logging.info("You selected: View Connected Attendees")
        elif selection == "5":
            logging.info("You selected: Add Attendee Connection")
        elif selection == "6":
            logging.info("You selected: View Rooms")
        # Secret option to exit the application
        # Attendee Select , and Delete
        elif selection == "99001":
            logging.info("Get Attendee with ID")
            Menu.menu_get_attendee(self)
        elif selection == "99002":
            logging.info("Delete Attendee with ID")
            Menu.menu_delete_attendee(self)
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
    parser.add_argument("--neo4j-password", required=False,default="neo4j", help="Neo4j password")
    # debug level logging for testing
    parser.add_argument("--debug", action="store_true", help="Enable debug level logging")
    args = parser.parse_args()


    # Keep logging simple for now , log to file and optionally to console
    logging.basicConfig(
            level=logging.DEBUG if args.debug else logging.INFO,
            # add file and function name and line number to the log messages for better debugging
            format="%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s",
            handlers=[
                logging.FileHandler("app.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
    logging.info("Starting the application...")
    logging.debug("Debug mode is enabled.")

    # Connect to the databases and initialize the DAOs
    # Neo4j first because it is needed for the MySQL DAO to load connections from Neo4j into the temporary table
    dao_neo4j = DAO_Neo4j(args.neo4j_uri, args.neo4j_user, args.neo4j_password)
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
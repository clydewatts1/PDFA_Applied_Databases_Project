

## Testing

To improve the quality and accuracy of the project a testing framework pexpect and pytest have been used to create automated tests for the main.py program. These tests simulate user interactions with the command-line interface, allowing us to verify that the program behaves as expected under various scenarios.
Additional menu items will be added to help with testing , example select and delete attendess by attendee ID.


## Secret Menu

A number of additional menu items above the project requirements have been added to help with testing and debugging. 

The menu items are organized into two groups: the first group includes options for inserting, selecting, deleting, and updating records in the main tables (company, attendee, room, session, registration), while the second group includes options for resetting the MySQL and Neo4j databases.

The menu items in the first group are numbered from 88000 to 88999 and are accessible through the main menu. They provide functionality for performing CRUD (Create, Read, Update, Delete) operations on the main tables, allowing developers and testers to easily manipulate the data in the databases for testing purposes.
- 88000 - 88004: CRUD operations for Company table
- 88011 - 88014: CRUD operations for Attendee table
- 88021 - 88024: CRUD operations for Room table
- 88031 - 88034: CRUD operations for Session table
- 88041 - 88044: CRUD operations for Registration table

The menu items begin 99000 - 99999 and are not listed in the main menu. They can be accessed by entering the corresponding number at the main menu prompt. These secret menu items provide additional functionality for testing and debugging purposes, such as viewing all attendees, viewing all companies, and viewing all sessions. They are intended for use by developers and testers to facilitate the testing process and ensure the correctness of the program.

- 99001 - Get Attendee by ID
- 99002 - Delete Attendee by ID
- 99900 - Reset MySQL Database
- 99901 - Reset Neo4j Database
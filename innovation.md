

## Testing

To improve the quality and accuracy of the project a testing framework pexpect and pytest have been used to create automated tests for the main.py program. These tests simulate user interactions with the command-line interface, allowing us to verify that the program behaves as expected under various scenarios.
Additional menu items will be added to help with testing , example select and delete attendess by attendee ID.


## Secret Menu

A number of additional menu items above the project requirements have been added to help with testing and debugging. 

The menu items begin 99000 - 99999 and are not listed in the main menu. They can be accessed by entering the corresponding number at the main menu prompt. These secret menu items provide additional functionality for testing and debugging purposes, such as viewing all attendees, viewing all companies, and viewing all sessions. They are intended for use by developers and testers to facilitate the testing process and ensure the correctness of the program.

- 99001 - Get Attendee by ID
- 99002 - Delete Attendee by ID
- 99900 - Reset MySQL Database
- 99901 - Reset Neo4j Database
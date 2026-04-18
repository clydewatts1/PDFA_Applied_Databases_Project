from unicodedata import name

import pexpect
import re
import sys
import argparse
quiet = False


def start_program():
    child = pexpect.spawn('python3 -u main.py', encoding='utf-8', timeout=20)
    if not quiet:
        print("Started main.py program for testing.")
        child.logfile = sys.stdout
    else:
        print("Started main.py program for testing in quiet mode (no output will be shown).")
        child.logfile = None
    return child

def validate_menu_top_level(child):
    try:
        child.expect('Conference Management:')

        child.expect('----------------------')
        child.expect('1 - View Speakers & Sessions')
        child.expect('2 - View Attendees by Company')
        child.expect('3 - Add New Attendee')
        child.expect('4 - View Connected Attendees')
        child.expect('5 - Add Attendee Connection')
        child.expect('6 - View Rooms')
        child.expect('x - Exit')
        child.expect('Please select an option:')
        print("✅ PASS: Main Menu displayed correctly with all options and prompt.")
    except pexpect.TIMEOUT:
        print("❌ FAIL: Timed out waiting for expected text.")
        print(f"What the screen actually looked like:\n{child.before}")
    except Exception as e:
        print(f"❌ FAIL: An error occurred: {e}")

#----------------------------------------------------------------------------------------
# Test Cases
#----------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------
# Test Case: Reset Databases
#----------------------------------------------------------------------------------------
def test_reset_databases():
    print("Running Test: Reset Databases")
    
    child = start_program()
    try:
        validate_menu_top_level(child)
        print("✅ PASS: Program prompted for choice.")
        child.sendline('99900')
        child.expect('Are you sure you want to reset the MySQL database? This will delete all data. (y/n):')
        print("Sent '99900' to reset MySQL database.")
        child.sendline('y')
        child.expect('MySQL database has been reset successfully.')
        print("✅ PASS: MySQL database reset successfully.")
        child.expect('Please select an option:')
        child.sendline('99901')
        print("Sent '99901' to reset Neo4j database.")
        child.expect('Are you sure you want to reset the Neo4j database? This will delete all data. (y/n):')
        child.sendline('y')
        print("✅ PASS: Neo4j database reset successfully.")
        child.sendline('x')
    except pexpect.TIMEOUT:
        print("❌ FAIL: Timed out waiting for expected text.")
        print(f"What the screen actually looked like:\n{child.before}")
    except Exception as e:
        print(f"❌ FAIL: An error occurred: {e}")
    finally:
        child.close(force=True)
#----------------------------------------------------------------------------------------
# Test Case: Exit Cleanly
#----------------------------------------------------------------------------------------

def test_exit_cleanly():
    print("Running Test: Exit Cleanly")
    
    child = start_program()
    try:
        validate_menu_top_level(child)
        print("✅ PASS: Program prompted for choice.")
        child.sendline('x')
        print("Sent 'x' to exit the program.")
        child.expect(pexpect.EOF)        
        print("✅ PASS: Program exited cleanly.")       
    except pexpect.TIMEOUT:
        print("❌ FAIL: Timed out waiting for expected text.")
        print(f"What the screen actually looked like:\n{child.before}")
    except Exception as e:
        print(f"❌ FAIL: An error occurred: {e}")

#----------------------------------------------------------------------------------------
# Test Case: Exit with Multiple Non-Number Inputs
#----------------------------------------------------------------------------------------

def test_exit_multiple_non_number_inputs():
    print("Running Test: Exit with Multiple Non-Number Inputs")
    
    child = start_program()
    try:
        validate_menu_top_level(child)
        print("✅ PASS: Program prompted for choice.")
        child.sendline('a')
        print("Sent 'a' as invalid input.")
        child.expect('Please select an option:')
        child.sendline('(')
        print("Sent '(' as invalid input.")
        child.expect('Please select an option:')
        print("✅ PASS: Program prompted for choice again after invalid input.")
        child.sendline('x')
        print("Sent 'x' to exit the program.")
        child.expect(pexpect.EOF)        
        print("✅ PASS: Program exited cleanly.")       
    except pexpect.TIMEOUT:
        print("❌ FAIL: Timed out waiting for expected text.")
        print(f"What the screen actually looked like:\n{child.before}")
    except Exception as e:
        print(f"❌ FAIL: An error occurred: {e}")
#----------------------------------------------------------------------------------------
# Test Cases: Menu 1 : View Speakers & Sessions
#----------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------
# Test Case: View Speakers & Sessions - Positive Test
#----------------------------------------------------------------------------------------

def test_view_speakers_positive():
    """
    Positive Test: Searches for a valid speaker partial name ('dr') 
    and verifies the correct speaker data is returned.
    """
    print("\n--- Running Test: Option 1 (Positive) ---")
    
    # Remember the -u flag to prevent Python buffering!
    child = start_program()
    
    # Optional: Uncomment the next line if you want to watch the test run live
    # child.logfile = sys.stdout 
    
    try:
        # Wait for the main menu and select Option 1
        validate_menu_top_level(child)
        child.sendline('1')
        print("✅ PASS: Selected Option 1.")
        
        # Wait for the prompt and send the search query
        child.expect('Enter speaker name :')
        name = 'dr'
        child.sendline(name)
        print(f"✅ PASS: Entered search query '{name}'.")
        
        # Verify the success header appears
        child.expect(f'Session Details For : {name}')
        print("✅ PASS: Found session details header.")
   # 2. Verify the dashed line (optional, but good for strict UI testing)
        child.expect('----------------------------------------')
        print("✅ PASS: Found dashed line.")
        child.expect('Dr. Niamh Burke | Customer 360 with SQL | Main Hall')
        print("✅ PASS: Successfully found and displayed 'Dr. Niamh Burke'.")
        child.expect('Dr. Niamh Burke | Modern Data Pipelines | Main Hall')
        print("✅ PASS: Successfully found and displayed 'Dr. Niamh Burke' for second session.")
        child.expect('Dr. Sara Khan | AI in Healthcare Operations | Main Hall')
        print("✅ PASS: Successfully found and displayed 'Dr. Sara Khan'.")
        
    except pexpect.TIMEOUT:
        print("❌ FAIL: Timed out waiting for expected text.")
        print(f"Output before timeout:\n{child.before}")
    except Exception as e:
        print(f"❌ FAIL: An error occurred: {e}")
    finally:
        child.close(force=True)

#----------------------------------------------------------------------------------------
# Test Case: View Speakers & Sessions - Negative Test
#----------------------------------------------------------------------------------------
def test_view_speakers_negative():
    """
    Negative Test: Searches for a speaker name that does not exist ('xyz')
    and verifies the correct error message is displayed.
    """
    print("\n--- Running Test: Option 1 (Negative) ---")
    
    child = start_program()
    
    try:
        # Wait for the main menu and select Option 1
        validate_menu_top_level(child)
        child.sendline('1')
        print("✅ PASS: Selected Option 1.")
        
        # Wait for the prompt and send the search query
        child.expect('Enter speaker name :')
        print("✅ PASS: Prompted for speaker name.")
        child.sendline('xyz')
        
        child.expect('Session Details For : xyz')
        print("✅ PASS: Displayed session details header for 'xyz'.")
        # Verify the EXACT error message from the specification appears
        print("Checking No speakers found message...")
        child.expect('No speakers found for that name')
        validate_menu_top_level(child)
        print("✅ PASS: Successfully handled missing speaker and showed correct error.")
        
    except pexpect.TIMEOUT:
        print("❌ FAIL: Timed out waiting for expected text.")
        print(f"Output before timeout:\n{child.before}")
    except Exception as e:
        print(f"❌ FAIL: An error occurred: {e}")
    finally:
        child.close(force=True)

#----------------------------------------------------------------------------------------
# Test Cases: Menu 2 : View Attendees by Company
#----------------------------------------------------------------------------------------

def test_view_attendees_by_company_positive():
    print("\n--- Running Test: Option 2 (Positive) ---")
    
    child = start_program()
    
    try:
        # Wait for the main menu and select Option 2
        validate_menu_top_level(child)
        child.sendline('2')
        print("✅ PASS: Selected Option 2.")
        
        # Wait for the prompt and send the search query
        child.expect('Enter Company ID :')
        company_id = '2'
        child.sendline(company_id)
        print(f"✅ PASS: Entered company ID '{company_id}'.")

        # Expect to See company name in header
        child.expect('CloudSprint  Attendees')
        print("✅ PASS: Found company name in header.")
        # We expect following Records
        child.expect('Cian Roche | 1989-09-08 | Cloud Cost Optimisation | Ruth Collins | Cloud Suite')
        child.expect('Cian Roche | 1989-09-08 | FinTech Risk Signals | Marta Silva | Executive Lounge')
        child.expect('Evan Brady | 1988-12-18 | Cloud Cost Optimisation | Ruth Collins | Cloud Suite')
        child.expect('Liam Byrne | 1990-02-24 | Customer 360 with SQL | Dr. Niamh Burke | Main Hall')
        child.expect('Liam Byrne | 1990-02-24 | Scaling Neo4j for Recommendations | Prof. Alan Shaw | Graph Lab')
        # We expect to see the menu again after results
        validate_menu_top_level(child)
    except pexpect.TIMEOUT:
        print("❌ FAIL: Timed out waiting for expected text.")
        print(f"Output before timeout:\n{child.before}")
    except Exception as e:
        print(f"❌ FAIL: An error occurred: {e}")
    finally:
        child.close(force=True)
#----------------------------------------------------------------------------------------
# Test Case: View Attendees by Company - Multiple Company ID Test
#----------------------------------------------------------------------------------------


def test_view_attendees_by_company_multiple():
    print("\n--- Running Test: Option 2 (Multiple Company ID Test) ---")
    
    # Remember the -u flag to prevent Python buffering!
    child = start_program()
   
    try:
        # Wait for the main menu and select Option 2
        validate_menu_top_level(child)
        child.sendline('2')
        print("✅ PASS: Selected Option 2.")
        child.expect('Enter Company ID :')
        print("✅ PASS: Prompted for Company ID.")
        company_id = '0'    
        child.sendline(company_id)
        child.expect('Enter Company ID :')
        print(f"✅ PASS: Prompted for Company ID. {company_id} is invalid as expected.")
        company_id = '-1'    
        child.sendline(company_id)
        child.expect('Enter Company ID :')
        print(f"✅ PASS: Prompted for Company ID. {company_id} is invalid as expected.")
        company_id = 'asdf'
        child.sendline(company_id)
        child.expect('Enter Company ID :')
        print(f"✅ PASS: Prompted for Company ID. {company_id} is invalid as expected.")
        company_id = '|'
        child.sendline(company_id)
        child.expect('Enter Company ID :')
        print(f"✅ PASS: Prompted for Company ID. {company_id} is invalid as expected.")
        company_id = '2'
        child.sendline(company_id)
        print(f"✅ PASS: Entered company ID '{company_id}'.")

        # Expect to See company name in header
        child.expect('CloudSprint  Attendees')
        print("✅ PASS: Found company name in header.")
        # We expect following Records
        child.expect('Cian Roche | 1989-09-08 | Cloud Cost Optimisation | Ruth Collins | Cloud Suite')
        child.expect('Cian Roche | 1989-09-08 | FinTech Risk Signals | Marta Silva | Executive Lounge')
        child.expect('Evan Brady | 1988-12-18 | Cloud Cost Optimisation | Ruth Collins | Cloud Suite')
        child.expect('Liam Byrne | 1990-02-24 | Customer 360 with SQL | Dr. Niamh Burke | Main Hall')
        child.expect('Liam Byrne | 1990-02-24 | Scaling Neo4j for Recommendations | Prof. Alan Shaw | Graph Lab')
        # We expect to see the menu again after results
        validate_menu_top_level(child)
    except pexpect.TIMEOUT:
        print("❌ FAIL: Timed out waiting for expected text.")
        print(f"Output before timeout:\n{child.before}")
    except Exception as e:
        print(f"❌ FAIL: An error occurred: {e}")
    finally:
        child.close(force=True)
#----------------------------------------------------------------------------------------
# Test Case: View Attendees by Company - Not Valid Company ID Test
#----------------------------------------------------------------------------------------

def test_view_attendees_by_company_not_valid_company():
    print("\n--- Running Test: Option 2 (Invalid Company ID) ---")
    
    # Remember the -u flag to prevent Python buffering!
    child = start_program()
   
    try:
        # Wait for the main menu and select Option 2
        validate_menu_top_level(child)
        child.sendline('2')
        print("✅ PASS: Selected Option 2.")
        child.expect('Enter Company ID :')
        print("✅ PASS: Prompted for Company ID.")
        company_id = '99'    
        child.sendline(company_id)
        child.expect(f'Company with ID  {company_id} doesn\'t exist')
        child.expect('Enter Company ID :')
        print(f"✅ PASS: Prompted for Company ID. {company_id} is invalid as expected.")
        company_id = '2'
        child.sendline(company_id)
        print(f"✅ PASS: Entered company ID '{company_id}'.")

        # Expect to See company name in header
        child.expect('CloudSprint  Attendees')
        print("✅ PASS: Found company name in header.")
        # We expect following Records
        child.expect('Cian Roche | 1989-09-08 | Cloud Cost Optimisation | Ruth Collins | Cloud Suite')
        child.expect('Cian Roche | 1989-09-08 | FinTech Risk Signals | Marta Silva | Executive Lounge')
        child.expect('Evan Brady | 1988-12-18 | Cloud Cost Optimisation | Ruth Collins | Cloud Suite')
        child.expect('Liam Byrne | 1990-02-24 | Customer 360 with SQL | Dr. Niamh Burke | Main Hall')
        child.expect('Liam Byrne | 1990-02-24 | Scaling Neo4j for Recommendations | Prof. Alan Shaw | Graph Lab')
        # We expect to see the menu again after results
        validate_menu_top_level(child)
    except pexpect.TIMEOUT:
        print("❌ FAIL: Timed out waiting for expected text.")
        print(f"Output before timeout:\n{child.before}")
    except Exception as e:
        print(f"❌ FAIL: An error occurred: {e}")
    finally:
        child.close(force=True)

#----------------------------------------------------------------------------------------
# Test Case: View Attendees by Company - No Attendees for Company ID Test
#----------------------------------------------------------------------------------------

def test_view_attendees_by_company_no_attendees():
    print("\n--- Running Test: Option 2 (No Attendees for Company ID) ---")
    
    # Remember the -u flag to prevent Python buffering!
    child = start_program()
   
    try:
        # Wait for the main menu and select Option 2
        validate_menu_top_level(child)
        child.sendline('2')
        print("✅ PASS: Selected Option 2.")
        child.expect('Enter Company ID :')
        print("✅ PASS: Prompted for Company ID.")
        company_id = '9'    
        child.sendline(company_id)
        print(f"✅ PASS: Entered company ID '{company_id}'.")
        child.expect('WindyDays  Attendees')
        print("✅ PASS: Found company name in header.")
        child.expect('No attendees found for  WindyDays')
        print("✅ PASS: Correctly handled case with no attendees for company.")
        child.expect('Enter Company ID :')
        print(f"✅ PASS: Prompted for Company ID. {company_id} is invalid as expected.")
        company_id = '2'
        child.sendline(company_id)
        print(f"✅ PASS: Entered company ID '{company_id}'.")

        # Expect to See company name in header
        child.expect('CloudSprint  Attendees')
        print("✅ PASS: Found company name in header.")
        # We expect following Records
        child.expect('Cian Roche | 1989-09-08 | Cloud Cost Optimisation | Ruth Collins | Cloud Suite')
        child.expect('Cian Roche | 1989-09-08 | FinTech Risk Signals | Marta Silva | Executive Lounge')
        child.expect('Evan Brady | 1988-12-18 | Cloud Cost Optimisation | Ruth Collins | Cloud Suite')
        child.expect('Liam Byrne | 1990-02-24 | Customer 360 with SQL | Dr. Niamh Burke | Main Hall')
        child.expect('Liam Byrne | 1990-02-24 | Scaling Neo4j for Recommendations | Prof. Alan Shaw | Graph Lab')
        # We expect to see the menu again after results
        validate_menu_top_level(child)
    except pexpect.TIMEOUT:
        print("❌ FAIL: Timed out waiting for expected text.")
        print(f"Output before timeout:\n{child.before}")
    except Exception as e:
        print(f"❌ FAIL: An error occurred: {e}")
    finally:
        child.close(force=True)


#----------------------------------------------------------------------------------------
# Test Cases: Menu 3 : Add New Attendee
#----------------------------------------------------------------------------------------



def test_add_new_attendee_positive(attendeeID:str,name:str,DOB:str,gender:str,companyID:str):
    print("\n--- Running Test: Option 3 (Add New Attendee - Positive) ---")
    
    # Remember the -u flag to prevent Python buffering!
    child = start_program()
   
    try:
        # Wait for the main menu and select Option 3
        validate_menu_top_level(child)
        child.sendline('3')
        print("✅ PASS: Selected Option 3.")
        child.expect('Add New Attendee')
        print("✅ PASS: Navigated to Add New Attendee menu.")
        child.expect('----------------')
        print("✅ PASS: Found dashed line.")
        child.expect('Attendee ID :')
        print("✅ PASS: Prompted for Attendee ID.")
        child.sendline(str(attendeeID))
        print(f"✅ PASS: Entered Attendee ID '{attendeeID}'.")
        child.expect('Name : ')
        print("✅ PASS: Prompted for Name.")
        child.sendline(name)
        print(f"✅ PASS: Entered Name '{name}'.")
        child.expect('DOB : ')
        print("✅ PASS: Prompted for DOB.")
        child.sendline(DOB)
        print(f"✅ PASS: Entered DOB '{DOB}'.")
        child.expect('Gender : ')
        print("✅ PASS: Prompted for Gender.")
        child.sendline(gender)
        print(f"✅ PASS: Entered Gender '{gender}'.")
        child.expect('Company ID : ')
        print("✅ PASS: Prompted for Company ID.")
        child.sendline(companyID)
        print(f"✅ PASS: Entered Company ID '{companyID}'.")
        child.expect('Attendee successfully added')
        print("✅ PASS: Attendee added successfully.")
        validate_menu_top_level(child)
        child.sendline('x')
    except pexpect.TIMEOUT:
        print("❌ FAIL: Timed out waiting for expected text.")
        print(f"Output before timeout:\n{child.before}")
    except Exception as e:
        print(f"❌ FAIL: An error occurred: {e}")
    finally:
        child.close(force=True)


#----------------------------------------------------------------------------------------
# Test Cases: Menu 3 : Add New Attendee
#----------------------------------------------------------------------------------------



def test_add_new_attendee_negative_existing(attendeeID:str,name:str,DOB:str,gender:str,companyID:str):
    print("\n--- Running Test: Option 3 (Add New Attendee - Negative: Existing Attendee) ---")
    
    # Remember the -u flag to prevent Python buffering!
    child = start_program()
   
    try:
        # Wait for the main menu and select Option 3
        validate_menu_top_level(child)
        child.sendline('3')
        print("✅ PASS: Selected Option 3.")
        child.expect('Add New Attendee')
        print("✅ PASS: Navigated to Add New Attendee menu.")
        child.expect('----------------')
        print("✅ PASS: Found dashed line.")
        child.expect('Attendee ID :')
        print("✅ PASS: Prompted for Attendee ID.")
        child.sendline(str(attendeeID))
        print(f"✅ PASS: Entered Attendee ID '{attendeeID}'.")
        child.expect('Name : ')
        print("✅ PASS: Prompted for Name.")
        child.sendline(name)
        print(f"✅ PASS: Entered Name '{name}'.")
        child.expect('DOB : ')
        print("✅ PASS: Prompted for DOB.")
        child.sendline(DOB)
        print(f"✅ PASS: Entered DOB '{DOB}'.")
        child.expect('Gender : ')
        print("✅ PASS: Prompted for Gender.")
        child.sendline(gender)
        print(f"✅ PASS: Entered Gender '{gender}'.")
        child.expect('Company ID : ')
        print("✅ PASS: Prompted for Company ID.")
        child.sendline(companyID)
        print(f"✅ PASS: Entered Company ID '{companyID}'.")
        # * are part of the error message so need to escape them in the regex
        child.expect(re.escape(f'*** ERROR *** Attendee ID: {attendeeID} already exists'))
        print("✅ PASS: Detected existing attendee.")
        validate_menu_top_level(child)
        child.sendline('x')
    except pexpect.TIMEOUT:
        print("❌ FAIL: Timed out waiting for expected text.")
        print(f"Output before timeout:\n{child.before}")
    except Exception as e:
        print(f"❌ FAIL: An error occurred: {e}")
    finally:
        child.close(force=True)

#----------------------------------------------------------------------------------------
# Test Case: Add New Attendee - Negative Test - Invalid Gender
#----------------------------------------------------------------------------------------



def test_add_new_attendee_negative_existing(attendeeID:str,name:str,DOB:str,gender:str,companyID:str):
    print("\n--- Running Test: Option 3 (Add New Attendee - Negative: Existing Attendee) ---")
    
    # Remember the -u flag to prevent Python buffering!
    child = start_program()
   
    try:
        # Wait for the main menu and select Option 3
        validate_menu_top_level(child)
        child.sendline('3')
        print("✅ PASS: Selected Option 3.")
        child.expect('Add New Attendee')
        print("✅ PASS: Navigated to Add New Attendee menu.")
        child.expect('----------------')
        print("✅ PASS: Found dashed line.")
        child.expect('Attendee ID :')
        print("✅ PASS: Prompted for Attendee ID.")
        child.sendline(str(attendeeID))
        print(f"✅ PASS: Entered Attendee ID '{attendeeID}'.")
        child.expect('Name : ')
        print("✅ PASS: Prompted for Name.")
        child.sendline(name)
        print(f"✅ PASS: Entered Name '{name}'.")
        child.expect('DOB : ')
        print("✅ PASS: Prompted for DOB.")
        child.sendline(DOB)
        print(f"✅ PASS: Entered DOB '{DOB}'.")
        child.expect('Gender : ')
        print("✅ PASS: Prompted for Gender.")
        child.sendline(gender)
        print(f"✅ PASS: Entered Gender '{gender}'.")
        child.expect('Company ID : ')
        print("✅ PASS: Prompted for Company ID.")
        child.sendline(companyID)
        print(f"✅ PASS: Entered Company ID '{companyID}'.")
        # * are part of the error message so need to escape them in the regex
        child.expect(re.escape(f'*** ERROR *** Attendee ID: {attendeeID} already exists'))
        print("✅ PASS: Detected existing attendee.")
        validate_menu_top_level(child)
        child.sendline('x')
    except pexpect.TIMEOUT:
        print("❌ FAIL: Timed out waiting for expected text.")
        print(f"Output before timeout:\n{child.before}")
    except Exception as e:
        print(f"❌ FAIL: An error occurred: {e}")
    finally:
        child.close(force=True)
#----------------------------------------------------------------------------------------
# Test Cases: Menu 3 : Invalid Gender
#----------------------------------------------------------------------------------------

def test_add_new_attendee_negative_invalid_gender(attendeeID:str,name:str,DOB:str,gender:str,companyID:str):
    print("\n--- Running Test: Option 3 (Add New Attendee - Negative: Invalid Gender) ---")
    
    # Remember the -u flag to prevent Python buffering!
    child = start_program()
   
    try:
        # check if test attendee gender is invalid before starting the test, if not print a warning that the test may not work as expected
        if gender in ['Male','Female']:
            print(f"⚠️ WARNING: The gender '{gender}' is valid. This test is intended for invalid genders.")
        # Wait for the main menu and select Option 3
        validate_menu_top_level(child)
        child.sendline('3')
        print("✅ PASS: Selected Option 3.")
        child.expect('Add New Attendee')
        print("✅ PASS: Navigated to Add New Attendee menu.")
        child.expect('----------------')
        print("✅ PASS: Found dashed line.")
        child.expect('Attendee ID :')
        print("✅ PASS: Prompted for Attendee ID.")
        child.sendline(str(attendeeID))
        print(f"✅ PASS: Entered Attendee ID '{attendeeID}'.")
        child.expect('Name : ')
        print("✅ PASS: Prompted for Name.")
        child.sendline(name)
        print(f"✅ PASS: Entered Name '{name}'.")
        child.expect('DOB : ')
        print("✅ PASS: Prompted for DOB.")
        child.sendline(DOB)
        print(f"✅ PASS: Entered DOB '{DOB}'.")
        child.expect('Gender : ')
        print("✅ PASS: Prompted for Gender.")
        child.sendline(gender)
        print(f"✅ PASS: Entered Gender '{gender}'.")
        child.expect('Company ID : ')
        print("✅ PASS: Prompted for Company ID.")
        child.sendline(companyID)
        print(f"✅ PASS: Entered Company ID '{companyID}'.")
        # * are part of the error message so need to escape them in the regex
        child.expect(re.escape(f'*** ERROR *** Gender must be Male/Female'))
        print("✅ PASS: Detected invalid gender.")
        validate_menu_top_level(child)
        child.sendline('x')
    except pexpect.TIMEOUT:
        print("❌ FAIL: Timed out waiting for expected text.")
        print(f"Output before timeout:\n{child.before}")
    except Exception as e:
        print(f"❌ FAIL: An error occurred: {e}")
    finally:
        child.close(force=True)

#----------------------------------------------------------------------------------------
# Test Cases: Menu 3 : Invalid Company ID
#----------------------------------------------------------------------------------------

def test_add_new_attendee_negative_invalid_company_id(attendeeID:str,name:str,DOB:str,gender:str,companyID:str):
    print("\n--- Running Test: Option 3 (Add New Attendee - Negative: Invalid Company ID) ---")
    
    # Remember the -u flag to prevent Python buffering!
    child = start_program()
   
    try:
        # check if test attendee company ID is invalid before starting the test, if not print a warning that the test may not work as expected
        if companyID.isdigit():
            print(f"⚠️ WARNING: The company ID '{companyID}' is valid. This test is intended for invalid company IDs.")
        # Wait for the main menu and select Option 3
        validate_menu_top_level(child)
        child.sendline('3')
        print("✅ PASS: Selected Option 3.")
        child.expect('Add New Attendee')
        print("✅ PASS: Navigated to Add New Attendee menu.")
        child.expect('----------------')
        print("✅ PASS: Found dashed line.")
        child.expect('Attendee ID :')
        print("✅ PASS: Prompted for Attendee ID.")
        child.sendline(str(attendeeID))
        print(f"✅ PASS: Entered Attendee ID '{attendeeID}'.")
        child.expect('Name : ')
        print("✅ PASS: Prompted for Name.")
        child.sendline(name)
        print(f"✅ PASS: Entered Name '{name}'.")
        child.expect('DOB : ')
        print("✅ PASS: Prompted for DOB.")
        child.sendline(DOB)
        print(f"✅ PASS: Entered DOB '{DOB}'.")
        child.expect('Gender : ')
        print("✅ PASS: Prompted for Gender.")
        child.sendline(gender)
        print(f"✅ PASS: Entered Gender '{gender}'.")
        child.expect('Company ID : ')
        print("✅ PASS: Prompted for Company ID.")
        child.sendline(companyID)
        print(f"✅ PASS: Entered Company ID '{companyID}'.")
        # * are part of the error message so need to escape them in the regex
        child.expect(re.escape(f'*** ERROR *** Company ID: {companyID} does not exist'))
        print("✅ PASS: Detected invalid company ID.")
        validate_menu_top_level(child)
        child.sendline('x')
    except pexpect.TIMEOUT:
        print("❌ FAIL: Timed out waiting for expected text.")
        print(f"Output before timeout:\n{child.before}")
    except Exception as e:
        print(f"❌ FAIL: An error occurred: {e}")
    finally:
        child.close(force=True)

#----------------------------------------------------------------------------------------
# Test Cases: Menu 3 : Invalid Attendee ID
#----------------------------------------------------------------------------------------

def test_add_new_attendee_negative_invalid_attendee_id(attendeeID:str,name:str,DOB:str,gender:str,companyID:str):
    print("\n--- Running Test: Option 3 (Add New Attendee - Negative: Invalid Attendee ID) ---")
    
    # Remember the -u flag to prevent Python buffering!
    child = start_program()
   
    try:
        # check if test attendee company ID is invalid before starting the test, if not print a warning that the test may not work as expected
        validate_menu_top_level(child)
        child.sendline('3')
        print("✅ PASS: Selected Option 3.")
        child.expect('Add New Attendee')
        print("✅ PASS: Navigated to Add New Attendee menu.")
        child.expect('----------------')
        print("✅ PASS: Found dashed line.")
        child.expect('Attendee ID :')
        print("✅ PASS: Prompted for Attendee ID.")
        child.sendline(str(attendeeID))
        print(f"✅ PASS: Entered Attendee ID '{attendeeID}'.")
        child.expect('Name : ')
        print("✅ PASS: Prompted for Name.")
        child.sendline(name)
        print(f"✅ PASS: Entered Name '{name}'.")
        child.expect('DOB : ')
        print("✅ PASS: Prompted for DOB.")
        child.sendline(DOB)
        print(f"✅ PASS: Entered DOB '{DOB}'.")
        child.expect('Gender : ')
        print("✅ PASS: Prompted for Gender.")
        child.sendline(gender)
        print(f"✅ PASS: Entered Gender '{gender}'.")
        child.expect('Company ID : ')
        print("✅ PASS: Prompted for Company ID.")
        child.sendline(companyID)
        print(f"✅ PASS: Entered Company ID '{companyID}'.")
        # * are part of the error message so need to escape them in the regex
        # Pick up database error
        child.expect(re.escape(f'*** ERROR *** (1366'))        
        print("✅ PASS: Detected invalid attendee ID.")
        validate_menu_top_level(child)
        child.sendline('x')
    except pexpect.TIMEOUT:
        print("❌ FAIL: Timed out waiting for expected text.")
        print(f"Output before timeout:\n{child.before}")
    except Exception as e:
        print(f"❌ FAIL: An error occurred: {e}")
    finally:
        child.close(force=True)
#----------------------------------------------------------------------------------------
# Test Cases: Menu 3 : Invalid DOB
#----------------------------------------------------------------------------------------

def test_add_new_attendee_negative_invalid_dob(attendeeID:str,name:str,DOB:str,gender:str,companyID:str):
    print("\n--- Running Test: Option 3 (Add New Attendee - Negative: Invalid DOB) ---")
    
    # Remember the -u flag to prevent Python buffering!
    child = start_program()
   
    try:
        # check if test attendee company ID is invalid before starting the test, if not print a warning that the test may not work as expected
        validate_menu_top_level(child)
        child.sendline('3')
        print("✅ PASS: Selected Option 3.")
        child.expect('Add New Attendee')
        print("✅ PASS: Navigated to Add New Attendee menu.")
        child.expect('----------------')
        print("✅ PASS: Found dashed line.")
        child.expect('Attendee ID :')
        print("✅ PASS: Prompted for Attendee ID.")
        child.sendline(str(attendeeID))
        print(f"✅ PASS: Entered Attendee ID '{attendeeID}'.")
        child.expect('Name : ')
        print("✅ PASS: Prompted for Name.")
        child.sendline(name)
        print(f"✅ PASS: Entered Name '{name}'.")
        child.expect('DOB : ')
        print("✅ PASS: Prompted for DOB.")
        child.sendline(DOB)
        print(f"✅ PASS: Entered DOB '{DOB}'.")
        child.expect('Gender : ')
        print("✅ PASS: Prompted for Gender.")
        child.sendline(gender)
        print(f"✅ PASS: Entered Gender '{gender}'.")
        child.expect('Company ID : ')
        print("✅ PASS: Prompted for Company ID.")
        child.sendline(companyID)
        print(f"✅ PASS: Entered Company ID '{companyID}'.")
        # * are part of the error message so need to escape them in the regex
        # Pick up database error
        child.expect(re.escape(f'*** ERROR *** (1366'))        
        print("✅ PASS: Detected invalid DOB.")
        validate_menu_top_level(child)
        child.sendline('x')
    except pexpect.TIMEOUT:
        print("❌ FAIL: Timed out waiting for expected text.")
        print(f"Output before timeout:\n{child.before}")
    except Exception as e:
        print(f"❌ FAIL: An error occurred: {e}")
    finally:
        child.close(force=True)

#----------------------------------------------------------------------------------------
# Test Cases: Menu 3 : Check New Attendee Exists by Fetching
#----------------------------------------------------------------------------------------

def test_add_new_attendee_check_if_exists(attendeeID:str,name:str,DOB:str,gender:str,companyID:str):
    print("\n--- Running Test: Option 3 (Add New Attendee - Check If Exists) ---")
    
    # Remember the -u flag to prevent Python buffering!
    child = start_program()
   
    try:
        # check if test attendee company ID is invalid before starting the test, if not print a warning that the test may not work as expected
        validate_menu_top_level(child)
        child.sendline('99001')
        print("✅ PASS: Selected Option 99001.")
        child.expect('Enter Attendee ID : ')
        child.sendline(str(attendeeID))
        #child.expect(f'Attendee Details For ID:')
        print(f"✅ PASS: Found attendee details header for ID {attendeeID}.")
        child.expect('----------------')
        print("✅ PASS: Found dashed line.")
        child.expect(f'Attendee ID: {str(attendeeID)}')
        print(f"✅ PASS: Found Attendee ID {attendeeID}.")
        child.expect(f'Name : {name}')
        print(f"✅ PASS: Found Name {name}.")
        child.expect(f'DOB : {DOB}')
        print(f"✅ PASS: Found DOB {DOB}.")
        child.expect(f'Gender : {gender}')
        print(f"✅ PASS: Found Gender {gender}.")
        child.expect(f'Company ID : {str(companyID)}')
        print(f"✅ PASS: Found Company ID {companyID}.")
        child.expect('----------------------------------------')

        validate_menu_top_level(child)
        child.sendline('x')
    except pexpect.TIMEOUT:
        print("❌ FAIL: Timed out waiting for expected text.")
        print(f"Output before timeout:\n{child.before}")
    except Exception as e:
        print(f"❌ FAIL: An error occurred: {e}")
    finally:
        child.close(force=True)



def test_add_new_attendee_delete(attendeeID:str):
    print("\n--- Running Test: Option 3 (Add New Attendee - Delete) ---")
    
    # Remember the -u flag to prevent Python buffering!
    child = start_program()
   
    try:
        # check if test attendee company ID is invalid before starting the test, if not print a warning that the test may not work as expected
        validate_menu_top_level(child)
        child.sendline('99002')
        print("✅ PASS: Selected Option 99002.")
        child.expect('Enter Attendee ID to delete :')
        print(f"✅ PASS: Prompted for Attendee ID to delete.")
        child.sendline(str(attendeeID))
        #child.expect(f'Attendee Details For ID:')
        child.sendline(str('y'))
        child.expect(f'successfully')
        print(f"✅ PASS: Attendee with ID {attendeeID} deleted successfully.")
        validate_menu_top_level(child)
        child.sendline('x')
    except pexpect.TIMEOUT:
        print("❌ FAIL: Timed out waiting for expected text.")
        print(f"Output before timeout:\n{child.before}")
    except Exception as e:
        print(f"❌ FAIL: An error occurred: {e}")
    finally:
        child.close(force=True)

# TODO Check Inserted Attendee by fetching
# TODO Check Delete Attendee and check deleted by fetching
#----------------------------------------------------------------------------------------
# Test View Rooms
#-----------------------------------------------------------------------------------------
def test_view_rooms():
    print("\n--- Running Test: Option 3 (Add New Attendee - Delete) ---")
    
    # Remember the -u flag to prevent Python buffering!
    child = start_program()
    

    try:
        validate_menu_top_level(child)
        child.sendline('6')
        print("✅ PASS: Selected Option 6.")
        child.expect('RoomID    | RoomName | Capacity')
        print("✅ PASS: Found room list header.")
        child.expect('1 | Main Hall  | ')
        print("✅ PASS: Found room 1.")
        child.expect('2 | Graph Lab  | 120')
        print("✅ PASS: Found room 2.")
        child.expect('3 | Cloud Suite  | 180')
        print("✅ PASS: Found room 3.")
        child.expect('4 | Innovation Room  | 90')
        print("✅ PASS: Found room 4.")
        child.expect('5 | Workshop Studio  | 60')
        print("✅ PASS: Found room 5.")
        child.expect('6 | Executive Lounge  | 40')
        print("✅ PASS: Found room 6.")
        index = child.expect('7 |')
        if index == 1:
            print("❌ FAIL: Unexpected room row found after room 6.")
        else:
            print("✅ PASS: No unexpected room rows found after room 6.")

        # Check return to main menu and exit
        validate_menu_top_level(child)
        child.sendline('x')
    except pexpect.TIMEOUT:
        print("❌ FAIL: Timed out waiting for expected text.")
        print(f"Output before timeout:\n{child.before}")
    except Exception as e:
        print(f"❌ FAIL: An error occurred: {e}")
    finally:
        child.close(force=True)

#----------------------------------------------------------------------------------------
# MAIN
#----------------------------------------------------------------------------------------
# Run the test
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiet", action="store_true",default=False, help="Run tests in quiet mode")
    args = parser.parse_args()
    quiet = args.quiet
    print("\n" + "="*50 + "\n")
    print("==  Starting CloudSprint Application Tests ==")
    print("\n" + "="*50 + "\n")
    test_reset_databases()
    #print("\n" + "="*50 + "\n")
    #test_exit_cleanly()
    #print("\n" + "="*50 + "\n")
    #test_exit_multiple_non_number_inputs()
    #print("\n" + "="*50 + "\n")
    #print("== test_view_speakers_positive ==")
    #print("\n" + "="*50 + "\n")
    #test_view_speakers_positive()
    #print("\n" + "="*50 + "\n")
    #print("== test_view_speakers_negative ==")
    #print("\n" + "="*50 + "\n")
    #test_view_speakers_negative()
    #print("\n" + "="*50 + "\n")
    #print("== test_view_attendees_by_company_positive ==")
    #print("\n" + "="*50 + "\n")
    #test_view_attendees_by_company_positive()
    #print("\n" + "="*50 + "\n")
    #print("== test_view_attendees_by_company_multiple ==")
    #print("\n" + "="*50 + "\n")
    #test_view_attendees_by_company_multiple()
    #print("\n" + "="*50 + "\n")
    #test_view_attendees_by_company_not_valid_company()
    #print("\n" + "="*50 + "\n")
    #print("== test_view_attendees_by_company_no_attendees ==")
    #print("\n" + "="*50 + "\n")
    #test_view_attendees_by_company_no_attendees()
    #print("\n" + "="*50 + "\n")
    #test_add_new_attendee_positive(attendeeID=121,name='Joe Kelly',DOB='1970-02-18',gender='Male',companyID='2')
    #print("\n" + "="*50 + "\n")
    #test_add_new_attendee_check_if_exists(attendeeID=121,name='Joe Kelly',DOB='1970-02-18',gender='Male',companyID='2')
    #print("\n" + "="*50 + "\n")
    #test_add_new_attendee_delete(attendeeID=121)
    #print("\n" + "="*50 + "\n")
    #test_add_new_attendee_negative_existing(attendeeID=121,name='Joe Kelly',DOB='1970-02-18',gender='Male',companyID='2')
    #print("\n" + "="*50 + "\n")
    #test_add_new_attendee_negative_existing(attendeeID=121,name='Joe Bon',DOB='1970-12-18',gender='Male',companyID='2')
    #print("\n" + "="*50 + "\n")
    #test_add_new_attendee_negative_existing(attendeeID=101,name='Joe Kelly',DOB='1970-12-18',gender='Male',companyID='2')
    #print("\n" + "="*50 + "\n")
    #test_add_new_attendee_negative_invalid_gender(attendeeID=122,name='Jane Doe',DOB='1980-05-10',gender='Unknown',companyID='2')
    #print("\n" + "="*50 + "\n")
    #test_add_new_attendee_negative_invalid_company_id(attendeeID=122,name='Jane Doe',DOB='1980-05-10',gender='Female',companyID='999')
    #print("\n" + "="*50 + "\n")
    #test_add_new_attendee_negative_invalid_attendee_id(attendeeID='abc',name='Jane Doe',DOB='1980-05-10',gender='Female',companyID='2')
    #print("\n" + "="*50 + "\n")
    #test_add_new_attendee_negative_invalid_dob(attendeeID='abc',name='Jane Doe',DOB='ttttt-05-10',gender='Female',companyID='2')
    #
    #--------------------------------------------------------------------------------------------
    #print("\n" + "="*50 + "\n")
    #print("== test_view_rooms ==")
    #print("\n" + "="*50 + "\n")
    test_view_rooms()
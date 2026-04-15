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
        child.expect('Session Details For : {}')
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
# MAIN
#----------------------------------------------------------------------------------------
# Run the test
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiet", action="store_true",default=False, help="Run tests in quiet mode")
    args = parser.parse_args()
    quiet = args.quiet


    #test_exit_cleanly()
    #print("\n" + "="*50 + "\n")
    #test_exit_multiple_non_number_inputs()
    #print("\n" + "="*50 + "\n")
    #test_view_speakers_positive()
    #print("\n" + "="*50 + "\n")
    #test_view_speakers_negative()
    #print("\n" + "="*50 + "\n")
    #test_view_attendees_by_company_positive()
    #print("\n" + "="*50 + "\n")
    #test_view_attendees_by_company_multiple()
    #print("\n" + "="*50 + "\n")
    #test_view_attendees_by_company_not_valid_company()
    #print("\n" + "="*50 + "\n")
    #test_view_attendees_by_company_no_attendees()
    #print("\n" + "="*50 + "\n")
    #test_add_new_attendee_positive(attendeeID=121,name='Joe Kelly',DOB='1970-02-18',gender='Male',companyID='2')
    print("\n" + "="*50 + "\n")
    test_add_new_attendee_negative_existing(attendeeID=121,name='Joe Kelly',DOB='1970-02-18',gender='Male',companyID='2')
    print("\n" + "="*50 + "\n")
    test_add_new_attendee_negative_existing(attendeeID=121,name='Joe Bon',DOB='1970-12-18',gender='Male',companyID='2')
    print("\n" + "="*50 + "\n")
    test_add_new_attendee_negative_existing(attendeeID=101,name='Joe Kelly',DOB='1970-12-18',gender='Male',companyID='2')
    
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
import time

start_time = time.time()

LOGIN_LINES = open("LoginInfo", 'r').readlines()
for i, line in enumerate(LOGIN_LINES):
    LOGIN_LINES[i] = line.strip()

#Login info
usernameString = LOGIN_LINES[0]
passwordString = LOGIN_LINES[1]

#Course Selection (Summer = 202005, Fall = 202009, Winter = 202101)
course_term = "202005"
course_subject = "ECON"
course_number = "209"
course_section = "001"
course_crn = "492"

#Set options for driver
chrome_options = Options()
chrome_options.add_argument("--headless")

#Start driver using preset options
driver = webdriver.Chrome("/Applications/chromedriver", options=chrome_options)

def login():

    driver.get('https://horizon.mcgill.ca/pban1/twbkwbis.P_WWWLogin')

    element = WebDriverWait(driver, 10).until(EC.title_is("User Login"))

    #username = driver.find_element_by_id("mcg_un")
    username = driver.find_element_by_xpath("//body/div[3]/table/tbody/tr/td[3]/form/table/tbody/tr/td[2]/input")
    username.clear()
    username.send_keys(usernameString)

    #password = driver.find_element_by_id("mcg_pw")
    password = driver.find_element_by_xpath("//body/div[3]/table/tbody/tr/td[3]/form/table/tbody/tr[2]/td[2]/input")
    password.clear()
    password.send_keys(passwordString)

    #driver.find_element_by_id("mcg_un_submit").click()
    driver.find_element_by_xpath("//body/div[3]/table/tbody/tr/td[3]/form/table/tbody/tr[3]/td[2]/input").click()

    element = WebDriverWait(driver, 10).until(EC.title_is("Main Menu"))
    print("Successfully Logged In")

def getCourseSeats(term, subject, number, section):

    driver.get('https://horizon.mcgill.ca/pban1/bwskfcls.p_sel_crse_search')

    element = WebDriverWait(driver, 10).until(EC.title_is("Select Term"))

    #term_selection = Select(driver.find_element_by_name("p_term"))
    term_selection = Select(driver.find_element_by_xpath("//body/div[3]/form/table/tbody/tr/td/select"))
    term_selection.select_by_value(term)

    #submit_button1 = driver.find_element_by_xpath("//input[@type='submit' and @value='Submit']")
    submit_button1 = driver.find_element_by_xpath("//body/div[3]/form/input[3]")
    submit_button1.click()

    element = WebDriverWait(driver, 10).until(EC.title_is("Look Up Course Sections"))

    #subject_selection = Select(driver.find_element_by_xpath("//select[@name='sel_subj']"))
    subject_selection = Select(driver.find_element_by_xpath("//body/div[3]/form/table/tbody/tr/td[2]/select"))
    subject_selection.select_by_value(subject)

    #submit_button2 = driver.find_element_by_xpath("//input[@type='submit' and @value='Course Search']")
    submit_button2 = driver.find_element_by_xpath("//body/div[3]/form/input[17]")
    submit_button2.click()

    element = WebDriverWait(driver, 10).until(EC.url_matches("https://horizon.mcgill.ca/pban1/bwskfcls.P_GetCrse"))

    #course_number_child = driver.find_element_by_xpath("//input[@name='SEL_CRSE' and @value='" + course_number + "']")
    course_number_element = driver.find_element_by_xpath("//td[text()='" + number + "']")
    course_number_container = course_number_element.find_element_by_xpath("..")
    course_number_submit = course_number_container.find_element_by_css_selector("input[value='View Sections']")
    course_number_submit.click()

    rows = driver.find_elements_by_xpath("//body/div[3]/form/table/tbody/tr")
    for i in range(2, len(rows)):
        cols = rows[i].find_elements_by_tag_name("td")
        #Find the correct row
        if len(cols) >= 5 and cols[4].text == section:
            #Find the correct column
            print("Remaining Seats (" + term + ", " + subject + number + " Section " + section + "): " + cols[12].text)
            return
    print(term + ", " + subject + number + " Section " + section + " could not be found.")

def registerForCourse(term, crn):
    driver.get('https://horizon.mcgill.ca/pban1/bwskfreg.P_AltPin')

    element = WebDriverWait(driver, 10).until(EC.title_is("Select Term"))

    # term_selection = Select(driver.find_element_by_name("p_term"))
    term_selection = Select(driver.find_element_by_name("term_in"))
    term_selection.select_by_value(term)

    # submit_button1 = driver.find_element_by_xpath("//input[@type='submit' and @value='Submit']")
    submit_button1 = driver.find_element_by_xpath("//input[@type='submit' and @value='Submit']")
    submit_button1.click()

    element = WebDriverWait(driver, 10).until(EC.title_is("Quick Add or Drop Course Sections"))

    crn_input = driver.find_element_by_xpath("//body/div[3]/form/table[3]//input[@id='crn_id1']")
    crn_input.send_keys(crn)
    crn_input.send_keys(Keys.RETURN)

    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//table[@summary='This layout table is used to present Registration Errors.']")))

    rows = driver.find_elements_by_xpath("//table[@summary='Current Schedule']/tbody/tr")
    for i in range(1, len(rows)):
        col = rows[i].find_elements_by_class_name("dddefault")[2]
        if col.text == crn:
            print("Registered for course.")
            return True
    print("Could not register for course.")
    return False



def highlight(element):
    """Highlights a Selenium webdriver element"""
    driver = element._parent
    def apply_style(s):
        driver.execute_script("arguments[0].setAttribute('style', arguments[1])", element, s)
    orignal_style = element.get_attribute('style')
    apply_style("border: 4px solid red")
    if (element.get_attribute("style")!=None):
        time.sleep(5)
    apply_style(orignal_style)


login()
registerForCourse(course_term, course_crn)
#getCourseSeats(course_term, course_subject, course_number, course_section)
#print(str(time.time()-start_time) + " seconds.")
#getCourseSeats("202101", "COMP", "424", "001")

#print(str(time.time()-start_time) + " seconds.")


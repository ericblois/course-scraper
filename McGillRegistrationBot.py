from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from webdriver_manager.chrome import ChromeDriverManager
import time
import smtplib, ssl
import email

class McGillRegistrationBot:

    def __init__(self, courses):
        # Set options for driver
        self.chrome_options = Options()
        #self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--window-size=1920,1080")

        self.waitTime = 10

        # Start driver using preset options
        #self.driver = webdriver.Chrome("/Applications/chromedriver", options=self.chrome_options)
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.implicitly_wait(self.waitTime)

        LOGIN_LINES = open("LoginInfo", 'r').readlines()
        for i, line in enumerate(LOGIN_LINES):
            LOGIN_LINES[i] = line.strip()

        # Login info
        self.usernameString = LOGIN_LINES[0]
        self.passwordString = LOGIN_LINES[1]

        self.courses = list(courses)

        self.server = smtplib.SMTP_SSL('smtp.gmail.com')

        self.fromaddr = "bloisserver@gmail.com"
        self.toaddr = "ericblois291@gmail.com"
        self.msg = email.message.EmailMessage()
        self.msg['From'] = self.fromaddr
        self.msg['To'] = self.toaddr
        self.msg.set_content("Your course scraper has attempted to register for a course on Minerva.")

    def start(self):
        lastTime = time.time()
        while len(self.courses) > 0:
            for courseInfo in self.courses:
                term = courseInfo["term"]
                subject = courseInfo["subject"]
                number = courseInfo["number"]
                section = courseInfo["section"]

                seats = self.getCourseSeatsVSB(term,subject,number,section)
                if int(seats[0]) == 0:
                    continue
                else:
                    boolean = self.registerForCourse(term, seats[1])
                    if boolean:
                        self.courses.remove(courseInfo)

            if time.time() - lastTime < 15:
                time.sleep(time - lastTime)
                lastTime = time.time()



    #Login to Minerva
    def login(self):
        self.driver.get('https://horizon.mcgill.ca/pban1/twbkwbis.P_WWWLogin')

        element = WebDriverWait(self.driver, self.waitTime).until(EC.title_is("User Login"))

        # username = driver.find_element_by_id("mcg_un")
        username = self.driver.find_element_by_xpath("//body/div[3]/table/tbody/tr/td[3]/form/table/tbody/tr/td[2]/input")
        username.clear()
        username.send_keys(self.usernameString)

        # password = driver.find_element_by_id("mcg_pw")
        password = self.driver.find_element_by_xpath("//body/div[3]/table/tbody/tr/td[3]/form/table/tbody/tr[2]/td[2]/input")
        password.clear()
        password.send_keys(self.passwordString)

        # driver.find_element_by_id("mcg_un_submit").click()
        self.driver.find_element_by_xpath("//body/div[3]/table/tbody/tr/td[3]/form/table/tbody/tr[3]/td[2]/input").click()

        element = WebDriverWait(self.driver, self.waitTime).until(EC.title_is("Main Menu"))
        print("Successfully Logged In")

    def getCourseSeatsVSB(self, term, subject, number, section):

        # driver.get('https://vsb.mcgill.ca/vsb/criteria.jsp')
        self.driver.get(
            "https://vsb.mcgill.ca/vsb/criteria.jsp?access=0&lang=en&tip=1&page=results&scratch=0&term=" + term + "&sort=none&filters=iiiiiiiii&bbs=&ds=&cams=Distance_Downtown_Macdonald_Off-Campus&locs=any&isrts=")

        element = WebDriverWait(self.driver, self.waitTime).until(EC.presence_of_element_located((By.TAG_NAME, "title")))

        if self.driver.title == "User Login":
            self.login()
            self.driver.get(
                "https://vsb.mcgill.ca/vsb/criteria.jsp?access=0&lang=en&tip=1&page=results&scratch=0&term=" + term + "&sort=none&filters=iiiiiiiii&bbs=&ds=&cams=Distance_Downtown_Macdonald_Off-Campus&locs=any&isrts=")

        element = WebDriverWait(self.driver, self.waitTime).until(EC.presence_of_element_located(
            (By.XPATH, "//body/div/div[2]/div[3]/div/table/tbody/tr/td/div[3]/div[9]/div[3]/input")))

        print("Found term " + term)

        input_box = self.driver.find_element_by_xpath(
            "//body/div/div[2]/div[3]/div/table/tbody/tr/td/div[3]/div[9]/div[3]/input")
        input_box.send_keys(subject + number)

        input_box.send_keys(Keys.RETURN)

        element = WebDriverWait(self.driver, self.waitTime).until(EC.presence_of_element_located((By.CLASS_NAME, "dropdownSelect")))

        print("Found course " + subject + number)

        section_select = self.driver.find_element_by_xpath(
            "//body/div/div[2]/div[3]/div/table/tbody/tr/td/div[3]/div[10]/div[3]/div[2]/div[10]//select")
        section_select.click()

        options = self.driver.find_elements_by_xpath(
            "//body/div/div[2]/div[3]/div/table/tbody/tr/td/div[3]/div[10]/div[3]/div[2]/div[10]//select/option")
        for option in options:
            if section in option.text:
                option.click()

        element = WebDriverWait(self.driver, self.waitTime).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".seatText, .fullText")))

        print("Found section " + section)

        element = WebDriverWait(self.driver, self.waitTime).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".crn_value")))

        crn_number = self.driver.find_element(By.CSS_SELECTOR, ".crn_value")

        print("Found CRN " + crn_number.text)

        try:
            remaining_seats = self.driver.find_element(By.CSS_SELECTOR, ".seatText")
            return (remaining_seats.text, crn_number.text)
        except NoSuchElementException:
            print("Course is full")
            return ("0", crn_number.text)

    #Register for a course
    def registerForCourse(self, term, crn):

        self.driver.get('https://horizon.mcgill.ca/pban1/bwskfreg.P_AltPin')

        while True:
            element = WebDriverWait(self.driver, self.waitTime).until(EC.presence_of_element_located((By.TAG_NAME, "title")))

            if self.driver.title == "User Login":
                self.login()
                self.driver.get('https://horizon.mcgill.ca/pban1/bwskfreg.P_AltPin')
            elif self.driver.title == "Quick Add or Drop Course Sections":
                self.driver.delete_all_cookies()
                self.driver.get('https://horizon.mcgill.ca/pban1/bwskfreg.P_AltPin')
            elif self.driver.title == "Select Term":
                break

        # term_selection = Select(driver.find_element_by_name("p_term"))
        term_selection = Select(self.driver.find_element_by_name("term_in"))
        term_selection.select_by_value(term)

        # submit_button1 = driver.find_element_by_xpath("//input[@type='submit' and @value='Submit']")
        submit_button1 = self.driver.find_element_by_xpath("//input[@type='submit' and @value='Submit']")
        submit_button1.click()

        element = WebDriverWait(self.driver, self.waitTime).until(EC.title_is("Quick Add or Drop Course Sections"))

        try:
            crn_input = self.driver.find_element_by_xpath("//body/div[3]/form//input[@id='crn_id1']")
        except (NoSuchElementException, TimeoutException):
            print("Course registration is closed currently.")
            return False
        crn_input.send_keys(crn)
        crn_input.send_keys(Keys.RETURN)

        # Next, log in to the server
        self.server.login("bloisserver@gmail.com", "sythdlimptgeespq")

        self.msg['Subject'] = "Attempt To Register For Course " + crn
        self.server.send_message(self.msg)

        try:
            element = WebDriverWait(self.driver, self.waitTime).until(EC.presence_of_element_located(
            (By.XPATH, "//table[@summary='This layout table is used to present Registration Errors.']")))
            print("Could not register for course.")
            return False
        except TimeoutException:
            print("Registered for course.")
            return True


    #Get seats in a course using Minerva
    def getCourseSeatsMinerva(self, term, subject, number, section):

        self.driver.get('https://horizon.mcgill.ca/pban1/bwskfcls.p_sel_crse_search')

        element = WebDriverWait(self.driver, self.waitTime).until(EC.title_is("Select Term"))

        # term_selection = Select(driver.find_element_by_name("p_term"))
        term_selection = Select(self.driver.find_element_by_xpath("//body/div[3]/form/table/tbody/tr/td/select"))
        term_selection.select_by_value(term)

        # submit_button1 = driver.find_element_by_xpath("//input[@type='submit' and @value='Submit']")
        submit_button1 = self.driver.find_element_by_xpath("//body/div[3]/form/input[3]")
        submit_button1.click()

        element = WebDriverWait(self.driver, self.waitTime).until(EC.title_is("Look Up Course Sections"))

        # subject_selection = Select(driver.find_element_by_xpath("//select[@name='sel_subj']"))
        subject_selection = Select(self.driver.find_element_by_xpath("//body/div[3]/form/table/tbody/tr/td[2]/select"))
        subject_selection.select_by_value(subject)

        # submit_button2 = driver.find_element_by_xpath("//input[@type='submit' and @value='Course Search']")
        submit_button2 = self.driver.find_element_by_xpath("//body/div[3]/form/input[17]")
        submit_button2.click()

        element = WebDriverWait(self.driver, self.waitTime).until(EC.url_matches("https://horizon.mcgill.ca/pban1/bwskfcls.P_GetCrse"))

        # course_number_child = driver.find_element_by_xpath("//input[@name='SEL_CRSE' and @value='" + course_number + "']")
        course_number_element = self.driver.find_element_by_xpath("//td[text()='" + number + "']")
        course_number_container = course_number_element.find_element_by_xpath("..")
        course_number_submit = course_number_container.find_element_by_css_selector("input[value='View Sections']")
        course_number_submit.click()

        rows = self.driver.find_elements_by_xpath("//body/div[3]/form/table/tbody/tr")
        for i in range(2, len(rows)):
            cols = rows[i].find_elements_by_tag_name("td")
            # Find the correct row
            if len(cols) >= 5 and cols[4].text == section:
                # Find the correct column
                print("Remaining Seats (" + term + ", " + subject + number + " Section " + section + "): " + cols[
                    12].text)
                return
        print(term + ", " + subject + number + " Section " + section + " could not be found.")

    def highlight(self, element):
        """Highlights a Selenium webdriver element"""
        driver = element._parent

        def apply_style(s):
            driver.execute_script("arguments[0].setAttribute('style', arguments[1])", element, s)

        orignal_style = element.get_attribute('style')
        apply_style("border: 4px solid red")
        if (element.get_attribute("style") != None):
            time.sleep(5)
        apply_style(orignal_style)
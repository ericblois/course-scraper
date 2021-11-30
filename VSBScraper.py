from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
import time

start_time = time.time()

#Course Selection (Summer = 202005, Fall = 202009, Winter = 202101)
course_term = "202101"
course_subject = "COMP"
course_number = "424"
course_section = "001"

#Set options for driver
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920,1080")

#Start driver using preset options
driver = webdriver.Chrome("/Applications/chromedriver", options=chrome_options)
driver.implicitly_wait(10)

def getCourseSeats(term, subject, number, section):

    #driver.get('https://vsb.mcgill.ca/vsb/criteria.jsp')
    driver.get("https://vsb.mcgill.ca/vsb/criteria.jsp?access=0&lang=en&tip=1&page=results&scratch=0&term=" + course_term + "&sort=none&filters=iiiiiiiii&bbs=&ds=&cams=Distance_Downtown_Macdonald_Off-Campus&locs=any&isrts=")

    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//body/div/div[2]/div[3]/div/table/tbody/tr/td/div[3]/div[9]/div[3]/input")))

    print("Found term " + course_term)

    input_box = driver.find_element_by_xpath("//body/div/div[2]/div[3]/div/table/tbody/tr/td/div[3]/div[9]/div[3]/input")
    input_box.send_keys(course_subject + course_number)

    input_box.send_keys(Keys.RETURN)

    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "dropdownSelect")))

    print("Found course " + course_subject + course_number)

    section_select = driver.find_element_by_xpath("//body/div/div[2]/div[3]/div/table/tbody/tr/td/div[3]/div[10]/div[3]/div[2]/div[10]//select")
    section_select.click()
    select = Select(section_select)

    try:
        select.select_by_visible_text("Lec " + course_section)
    except NoSuchElementException:
        print("Could not find unfilled lecture")

    try:
        select.select_by_visible_text("Lec " + course_section + " (Full)")
    except NoSuchElementException:
        print("Could not find unfilled lecture")

    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".seatText, .fullText")))

    print("Found section " + course_section)

    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".crn_value")))

    crn_number = driver.find_element(By.CSS_SELECTOR, ".crn_value")

    print("Found CRN " + crn_number.text)

    try:
        remaining_seats = driver.find_element(By.CSS_SELECTOR, ".seatText")
        return (remaining_seats.text, crn_number.text)
    except NoSuchElementException:
        print("Course is full")
        return ("0", crn_number.text)

print(getCourseSeats(course_term, course_subject, course_number, course_section))
print(time.time()-start_time)
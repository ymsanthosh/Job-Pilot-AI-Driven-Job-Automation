import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
import urllib

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach",True)
url = "https://www.linkedin.com/jobs/search/"
service = Service(executable_path='/usr/local/bin/chromedriver')
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)
driver.get(url)
time.sleep(3)
from pymongo import MongoClient
from selenium.webdriver.support import expected_conditions as EC

client=MongoClient("YOUR_MONOGDB_ATLAS_LINK")
db=client['jobpilot']
collection_resume=db['parsed']
collection_job=db['job']
collection_applied=db['applied']


username = "LINKEDIN_USERNAME"
password = "LINKEDIN_PASSWORD"

signinbutton = driver.find_element(By.CLASS_NAME,value="nav__button-secondary")
signinbutton.click()
time.sleep(3)

usernameinpt = driver.find_element(By.ID,value="username")
passwordinpt = driver.find_element(By.ID,value="password")

usernameinpt.send_keys(username)
passwordinpt.send_keys(password)

signinbutton = driver.find_element(By.CLASS_NAME,value="btn__primary--large")
signinbutton.click()

time.sleep(20)

driver.get("https://www.linkedin.com/jobs/search/?currentJobId=4001346933&f_AL=true&f_E=1%2C2%2C3&geoId=102713980&keywords=software%20engineer%2C%20Data%20science&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true")

companyname = []
titlename = []
joblinks = []
roles = []
requirements = []

time.sleep(5)
# Find company name, title, and job links, and append them to the respective lists


# job_cards = driver.find_elements(by=By.CSS_SELECTOR, value=".job-card-container--clickable")
list_container = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "scaffold-layout__list-container"))
    )
job_cards = list_container.find_elements(By.TAG_NAME, "li")
print(len(job_cards))
for job_card in job_cards:
    try:
        job_card.click()
        time.sleep(3)

        company_name_elem = WebDriverWait(driver,2).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "job-details-jobs-unified-top-card__company-name"))
        )
        company_name = company_name_elem.text.strip()
        print("job-company", company_name)

        job_title_elem = WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located((By.XPATH, "//h1[@class='t-24 t-bold inline']"))
        )
        job_title = job_title_elem.text.strip()
        print("job title", job_title)

        a_tag_elem = job_title_elem.find_element(By.XPATH, ".//a")
        application_url = a_tag_elem.get_attribute("href")
        print("link", application_url)

        job_details_div = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "job-details"))
        )
        job_details_text = job_details_div.text.strip()
        print("job details",job_details_text)

        companyname.append(company_name)
        titlename.append(job_title)
        joblinks.append(application_url)
        requirements.append(job_details_text)

    except Exception as e:
        print(e)
        continue

df = pd.DataFrame({
    "company": companyname,
    "title": titlename,
    "joblinks": joblinks,
    "location": "Bengaluru",
    "requirements": requirements
})

job_data = []
for index, row in df.iterrows():
    job_entry = {
        "title": row['title'],
        "company": row['company'],
        "job_url": row['joblinks'],
        "description": row['requirements'],
        "site": "linkedin",
        "location":"Bengaluru"
    }
    job_data.append(job_entry)

collection_job.insert_many(job_data)

# Close the driver
driver.quit()
print("saved in mongo")



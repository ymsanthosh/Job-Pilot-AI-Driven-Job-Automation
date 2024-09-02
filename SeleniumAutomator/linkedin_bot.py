# linkedin_bot.py

import math
import time
import random
import os
from . import utils
from . import constants
from . import config
import pickle
import hashlib
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import google.generativeai as genai
from pymongo import MongoClient
import urllib
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import json
from bson import ObjectId, json_util
import datetime

API_KEY = "AIzaSyBLFd5ZNytadTutYj1HsrWoXYwgZvS2BuE"
genai.configure(api_key=API_KEY)

client = MongoClient("mongodb+srv://user:" + urllib.parse.quote("fitpulse") +
                     "@cluster0.urlcyfn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['jobpilot']
collection_resume = db['parsed']
collection_job = db['job']
collection_applied = db['applied']


def parse_json(data):
    return json.loads(json_util.dumps(data))


class Application:
    def __init__(self, email, title, role, date, url):
        self.email = email,
        self.title = title,
        self.role = role,
        self.date = date,
        self.url = url

    def save(self):
        collection_applied.insert_one({
            'email': self.email,
            'title': self.title,
            'role': self.role,
            'date': self.date,
            'url': self.url
        })


class Linkedin:
    def __init__(self):
        service = Service(executable_path='/usr/local/bin/chromedriver')
        self.driver = webdriver.Chrome(service=service, options=utils.chromeBrowserOptions())
        self.cookies_dir = os.path.join(os.getcwd(), 'cookies')
        self.cookies_path = os.path.join(self.cookies_dir, f"{self.getHash(config.email)}.pkl")
        # Ensure the cookies directory exists
        if not os.path.exists(self.cookies_dir):
            os.makedirs(self.cookies_dir)
        self.driver.get('https://www.linkedin.com')
        self.loadCookies()
        if not self.isLoggedIn():
            self.driver.get("https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin")
            utils.prYellow("🔄 Trying to log in Linkedin...")
            try:
                self.driver.find_element(By.ID, "username").send_keys(config.email)
                time.sleep(2)
                self.driver.find_element(By.ID, "password").send_keys(config.password)
                time.sleep(2)
                self.driver.find_element(By.XPATH, '//button[@type="submit"]').click()
                time.sleep(5)
            except:
                utils.prRed(
                    " Couldn't log in Linkedin by using Chrome. Please check your Linkedin credentials on config files ")
            self.saveCookies()

    def getHash(self, string):
        return hashlib.md5(string.encode('utf-8')).hexdigest()

    def loadCookies(self):
        if os.path.exists(self.cookies_path):
            cookies = pickle.load(open(self.cookies_path, "rb"))
            self.driver.delete_all_cookies()
            for cookie in cookies:
                self.driver.add_cookie(cookie)

    def saveCookies(self):
        pickle.dump(self.driver.get_cookies(), open(self.cookies_path, "wb"))

    def isLoggedIn(self):
        self.driver.get('https://www.linkedin.com/feed')
        try:
            self.driver.find_element(By.XPATH, '//*[@id="ember14"]')
            return True
        except:
            pass
        return False

    def applyJobs(self, url,email):
        try:
            print("Starting to APPLY .........")
            self.driver.get(url)
            time.sleep(random.uniform(1, constants.botSpeed))
            easyApplybutton = self.easyApplyButton()
            if easyApplybutton:
                easyApplybutton.click()
                time.sleep(random.uniform(1, constants.botSpeed))
                try:
                    self.chooseResume()
                    self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Submit application']").click()
                    time.sleep(random.uniform(1, constants.botSpeed))
                    print("submit button clicked")
                    currdate = datetime.date.today()
                    currdate=str(currdate)
                    job_data = collection_job.find_one({"job_url": url})
                    job_data = parse_json(job_data)
                    job_title = job_data.get('company')
                    job_role = job_data.get('title')
                    data_put = Application(email=email, title=job_role, role=job_title, date=currdate, url=url)
                    data_put.save()
                    lineToWrite = str(url) + " Applied"
                    self.displayWriteResults(lineToWrite)
                except:
                    try:
                        self.driver.find_element(By.CSS_SELECTOR,
                                                 "button[aria-label='Continue to next step']").click()
                        time.sleep(random.uniform(1, constants.botSpeed))
                        self.chooseResume()
                        print("Next button clicked")
                        comPercentage = self.driver.find_element(By.XPATH,
                                                                 'html/body/div[3]/div/div/div[2]/div/div/span').text
                        percenNumber = int(comPercentage[:comPercentage.index("%")])
                        currdate = datetime.date.today()
                        currdate = str(currdate)
                        job_data = collection_job.find_one({"job_url": url})
                        job_data = parse_json(job_data)
                        job_title = job_data.get('company')
                        job_role = job_data.get('title')
                        result = self.applyProcess(percenNumber, url)
                        data_put = Application(email=email, title=job_title, role=job_role, date=currdate, url=url)
                        data_put.save()
                        print(result)
                        self.displayWriteResults(lineToWrite)
                    except Exception as e:
                        self.chooseResume()
                        print(e)
                        lineToWrite = " | " + "*  Cannot apply to this Job! " + str(url)
                        self.displayWriteResults(lineToWrite)
                        return False
            else:
                lineToWrite = " | " + "*  Already applied! Job: " + str(url)
                self.displayWriteResults(lineToWrite)
                return True
        except Exception as e:
            print(f"Error applying for job: {e}")
            return False

    def chooseResume(self):
        try:
            wait = WebDriverWait(self.driver, 3)
            file_input = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[type='file']")
                )
            )
            resume_path = os.path.abspath(os.path.join(os.getcwd(), './uploads', 'santhosh.pdf'))
            print("Resume path:", resume_path)
            if not os.path.exists(resume_path):
                raise FileNotFoundError(f"Resume file not found: {resume_path}")
            file_input.send_keys(resume_path)
            print("Resume uploaded successfully")
            time.sleep(2)  # Adjust as needed
            next_button = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@class, 'artdeco-button--primary')]")
                )
            )
            next_button.click()
            time.sleep(2)

            select_questions = {}
            try:
                text_labels = self.driver.find_elements(By.XPATH, "//label[contains(@class, 'artdeco-text-input--label')]")
                for label in text_labels:
                    try:
                        question_id = label.get_attribute("for")
                        first_hyphen_index = question_id.rfind('-')
                        substring = question_id[first_hyphen_index + 1:]
                        question_additional_info = "THE ANSWER MUST BE OF " + substring + "TYPE"
                        question = label.text.strip()
                        temp = (question, "", question_additional_info)
                        select_questions[question_id] = temp
                    except NoSuchElementException as e:
                        print(f"Error processing question '{question}': {e}")
            except NoSuchElementException as e:
                print(f"Error finding text input labels: {e}")
            try:
                select_labels = self.driver.find_elements(By.XPATH, "//label[contains(@class, 'fb-dash-form-element__label')]")
                for label in select_labels:
                    try:
                        spans = label.find_elements(By.TAG_NAME, 'span')
                        question_text_parts = [span.text.strip() for span in spans if span.text.strip()]
                        question_text = ' '.join(question_text_parts)
                        question_id = label.get_attribute("for")
                        question = label.text.strip()
                        if(len(question_text)<len(question)): question=question_text
                        select_element = self.driver.find_element(By.ID, question_id)
                        select = Select(select_element)
                        options = [option.text.strip() for option in select.options if option.text.strip()]
                        options.pop(0)
                        temp = (question, options, "")
                        select_questions[question_id] = temp
                    except NoSuchElementException as e:
                        print(f"Error processing question '{question}': {e}")

            except NoSuchElementException as e:
                print(f"Error finding text input labels: {e}")
            try:
                fieldsets = self.driver.find_elements(By.XPATH,
                                                 "//fieldset[@data-test-form-builder-radio-button-form-component='true']")
                for fieldset in fieldsets:
                    legend = fieldset.find_element(By.TAG_NAME, 'legend')
                    spans = legend.find_elements(By.TAG_NAME, 'span')
                    question_text_parts = [span.text.strip() for span in spans if span.text.strip()]
                    question = ' '.join(question_text_parts)
                    question_text = legend.text.strip()
                    if (len(question) < len(question_text)): question_text = question
                    question_id = fieldset.get_attribute("id")
                    options = []
                    option_divs = fieldset.find_elements(By.XPATH, ".//div[@data-test-text-selectable-option]")
                    for option_div in option_divs:
                        input_element = option_div.find_element(By.TAG_NAME, 'input')
                        option_value = input_element.get_attribute("value")
                        option_id=input_element.get_attribute("id")
                        options.append((option_value,option_id))
                    temp = (question_text, options, "")
                    select_questions[question_id] = temp
            except NoSuchElementException as e:
                print(f"Error finding text input labels: {e}")

            time.sleep(10)
            print("additional questions have been obtained")
            print(select_questions)
            email = "c19@bmsit.in"
            user = collection_resume.find_one({"email": email})
            user = parse_json(user)
            combined_input = f"Questions:\n{select_questions}\n\nResume:\n{user}"
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt2 = """
                       You are a skilled Resume scanner with a deep understanding of data science, full stack web development, software engineering, data structures, programming and its languages, big data engineering, DevOps, data analysis, and ATS functionality. 
                         You are given (question, options, additional_info). You have to evaluate the resume against the question and give an answer with respect to the additional info given. 
                         If the additional info specifies the answer to be in numeric, then please return the answer as a single integer without any text or additional formatting. 
                         
                          **If the answer cannot be found directly from the details provided:**
                            - Make a valid assumption based on your expertise and the context of the question.
                            - Ensure the assumption aligns with the required return type (numeric, text, option_id).
                            - **Never return "Not Found."** Instead, provide a reasonable default or assumed value.
                            
                         For the questions with options, just give {question_id: {question, option only}}. 
                         If the question is of radio button type, then the answer must be the option_id only, nothing else.
                         For the questions without options, give a text output in the form {question_id: {question, text_output}}. 
                         The output should be in JSON format with all entities in double quotes .
                       """

            response = model.generate_content([combined_input, prompt2])
            data = response.candidates[0].content.parts[0].text
            cleaned_json = data.replace('```json', '```').replace("```", "").replace('\n', '')
            print(cleaned_json)
            cleaned_json = json.loads(cleaned_json)

            for question_id, question_data in cleaned_json.items():
                question_text = list(question_data.keys())[0]
                answer = question_data[question_text]

                element = self.driver.find_element(By.ID, question_id)
                if element.tag_name == 'input':
                    element.send_keys(answer)

                elif element.tag_name == 'select':
                    select = Select(element)
                    select.select_by_visible_text(answer)
                elif element.tag_name == 'fieldset':
                    label = self.driver.find_element(By.XPATH, f"//label[@for='{answer}']")
                    label.click()

            print("Additional questions also answered")
            time.sleep(10)

        except Exception as e:
            utils.prRed(
                f" Resume or Additional Questions Error: {e}")

    def easyApplyButton(self):
        try:
            time.sleep(random.uniform(1, constants.botSpeed))
            button = self.driver.find_element(By.XPATH,
                                              "//div[contains(@class,'jobs-apply-button--top-card')]//button[contains(@class, 'jobs-apply-button')]")
            return button
        except:
            return False

    def applyProcess(self, percentage, offerPage):
        applyPages = math.floor(100 / percentage) - 2
        result = ""
        for _ in range(applyPages):
            self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Continue to next step']").click()

        self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Review your application']").click()
        time.sleep(random.uniform(1, constants.botSpeed))

        if not config.followCompanies:
            try:
                self.driver.find_element(By.CSS_SELECTOR, "label[for='follow-company-checkbox']").click()
            except:
                pass

        self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Submit application']").click()
        time.sleep(random.uniform(1, constants.botSpeed))

        result = "*  Just Applied to this job: " + str(offerPage)

        return result

    def displayWriteResults(self, lineToWrite: str):
        try:
            print(lineToWrite)
        except Exception as e:
            utils.prRed(" Error in DisplayWriteResults: " + str(e))

    def element_exists(self, parent, by, selector):
        return len(parent.find_elements(by, selector)) > 0

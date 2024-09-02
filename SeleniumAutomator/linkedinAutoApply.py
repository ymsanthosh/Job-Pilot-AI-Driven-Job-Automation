import math
import time, random, os
import utils, constants, config
import pickle, hashlib
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
from bson import ObjectId,json_util
import datetime
API_KEY="AIzaSyBLFd5ZNytadTutYj1HsrWoXYwgZvS2BuE"
genai.configure(api_key=API_KEY)
client=MongoClient("mongodb+srv://user:"+urllib.parse.quote("fitpulse")+"@cluster0.urlcyfn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db=client['jobpilot']
collection_resume=db['parsed']
collection_job=db['job']
collection_applied=db['applied']

def parse_json(data):
    return json.loads(json_util.dumps(data))

class Application:
    def __init__(self,email,title,role,date,url):
        self.email=email,
        self.title=title,
        self.role=role,
        self.date=date,
        self.url=url
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

    def applyJobs(self, urls):

        for url in urls:
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
                    currdate = datetime.date
                    email = ""

                    result = self.applyProcess(percenNumber, url)

                    lineToWrite = str(url) + "Applied"
                    self.displayWriteResults(lineToWrite)
                except:
                    try:
                        self.driver.find_element(By.CSS_SELECTOR,
                                                 "button[aria-label='Continue to next step']").click()
                        time.sleep(random.uniform(1, constants.botSpeed))
                        self.chooseResume()
                        comPercentage = self.driver.find_element(By.XPATH,
                                                                 'html/body/div[3]/div/div/div[2]/div/div/span').text
                        percenNumber = int(comPercentage[:comPercentage.index("%")])
                        currdate=datetime.date

                        result = self.applyProcess(percenNumber, url)

                        print(result)

                        self.displayWriteResults(lineToWrite)
                    except Exception:
                        self.chooseResume()
                        lineToWrite = " | " + "*  Cannot apply to this Job! " + str(url)
                        self.displayWriteResults(lineToWrite)
            else:
                lineToWrite =  + " | " + "*  Already applied! Job: " + str(url)
                self.displayWriteResults(lineToWrite)


    def chooseResume(self):
        try:
            wait = WebDriverWait(self.driver, 3)

            # Locate the file input element
            file_input = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[type='file']")
                )
            )
            resume_path = os.path.abspath(os.path.join(os.getcwd(), '../uploads', 'testing.pdf'))
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
                # Find all labels associated with text input fields
                text_labels = self.driver.find_elements(By.XPATH, "//label[contains(@class, 'artdeco-text-input--label')]")

                for label in text_labels:
                    try:
                        question_id = label.get_attribute("for")
                        first_hyphen_index = question_id.rfind('-')
                        substring = question_id[first_hyphen_index + 1:]
                        question_additional_info="THE ANSWER MUST BE OF " + substring + "TYPE"
                        question = label.text.strip()
                        temp =(question,"",question_additional_info)
                        select_questions[question_id]=temp
                    except NoSuchElementException as e:
                        print(f"Error processing question '{question}': {e}")

            except NoSuchElementException as e:
                print(f"Error finding text input labels: {e}")

            try:
                select_labels = self.driver.find_elements(By.XPATH, "//label[contains(@class, 'fb-dash-form-element__label')]")
                for label in select_labels:
                    try:
                        question_id=label.get_attribute("for")
                        question = label.text.strip()
                        select_element = self.driver.find_element(By.ID,question_id)
                        select = Select(select_element)
                        options = [option.text.strip() for option in select.options if option.text.strip()]
                        temp = (question,options,"")
                        select_questions[question_id] = temp
                    except NoSuchElementException as e:
                        print(f"Error processing question '{question}': {e}")

            except NoSuchElementException as e:
                print(f"Error finding text input labels: {e}")
            time.sleep(10)

            email = "rshreyas2003@gmail.com"
            user = collection_resume.find_one({"email": email})
            user = parse_json(user)
            combined_input = f"Questions:\n{select_questions}\n\nResume:\n{user}"
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt2 = """
                   You are a skilled Resume scanner with a deep understanding of data science, full stack web development, software engineering, data structures, programming and its languages, big data engineering, DevOps, data analysis, and ATS functionality. 
                    You are given (question, options, additional_info). You have to evaluate the resume against the question and give an answer with respect to the additional info given. 
                    If the additional info specifies the answer to be in numeric, then please return the answer as a single integer without any text or additional formatting. 
                    For the questions with options, just give {question_id: {question, option only}}. 
                    For the questions without options, give a text output in the form {question_id: {question, text_output}}. 
                    The output should be in JSON format with all entities in double quotes .

                   """
            response = model.generate_content([combined_input, prompt2])
            data = response.candidates[0].content.parts[0].text
            cleaned_json = data.replace('```json', '```').replace("```", "").replace('\n', '')
            print(cleaned_json)
            cleaned_json=json.loads(cleaned_json)

            for question_id, question_data in cleaned_json.items():
                question_text = list(question_data.keys())[0]  # Assuming there's only one question per ID
                answer = question_data[question_text]

                element = self.driver.find_element(By.ID, question_id)
                # Determine the type of element (input, select, etc.) and set the answer
                if element.tag_name == 'input':
                    element.send_keys(answer)
                elif element.tag_name == 'select':
                    select = Select(element)
                    select.select_by_visible_text(answer)

            time.sleep(2)


        except Exception as e:
            utils.prRed(
                f" No resume has been selected please add at least one resume to your LinkedIn account. Error: {e}")


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


urls_from_frontend = [
    "https://www.linkedin.com/jobs/search/?currentJobId=3946797490&eBP=CwEAAAGQ1i57Em0vvikDEDjKmY4e3Yzk1XqNosWHrA-9CZZa9-gG0X--QuG5GVQZjKu93G0tqMwRNAU25iQs31XhHA_KAy5SqflsjZpy9kW4ADUu7waPBPqN_w2GtOvXHvRz16m9Ms7ol30jatVMiXqBX4cTkLyrC09_6bf_LqCvFaI__8nNzT6ql6DBQ31UM5VW4tUG7WcU0XoxETHOZPBpFzyubmryvlFBhPM3wzzF02gefmta0EF6gmhbrmsPRL_364GvoDh7XEaDfGRlqMq7QScWgqAvwl6AzBB3FbsiXysBADnukOEttkwFuw-BryQq0qQBo3SiXuCplfdM3MmdVysRnfwRF-O4v0_4i71hXmy57VajbQVyq7Zr35KA2J-X4e4fvLpebBktXM4df_pK3q-nKkZc2ydC6LU0fxpWRRWU_gWaZmXyNlBVho5KJBB-iD6J0F6lLv5vBldNmqzHGFKSTMNIdw&f_AL=true&geoId=105214831&keywords=software%20engineer&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refId=XiW%2BeMsbLY1b3jaLlarh%2Fw%3D%3D&refresh=true&trackingId=UFGkdYHwuNUttcT6%2FaeSZg%3D%3D"
]

linkedin_bot = Linkedin()
linkedin_bot.applyJobs(urls_from_frontend)






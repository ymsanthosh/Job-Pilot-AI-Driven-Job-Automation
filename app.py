import json
import google.generativeai as genai
import os
from pypdf import PdfReader
import google.auth.transport
from google.oauth2 import id_token
from google_auth_oauthlib import flow
import pathlib
import requests
import cachecontrol
from flask import Flask, render_template,Response,session, abort, redirect, request,url_for,flash, jsonify
from bson import ObjectId,json_util
import urllib
from passlib.hash import pbkdf2_sha256
from flask_cors import CORS
from jobspy import scrape_jobs
from pymongo import MongoClient, collection
from markdownify import markdownify as md
import logging
from SeleniumAutomator.linkedin_bot import Linkedin
import time


API_KEY="AIzaSyBLFd5ZNytadTutYj1HsrWoXYwgZvS2BuE"
genai.configure(api_key=API_KEY)
client=MongoClient("mongodb+srv://user:"+urllib.parse.quote("fitpulse")+"@cluster0.urlcyfn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db=client['jobpilot']
collection_resume=db['parsed']
collection_job=db['job']
collection_applied=db['applied']
collection_user=db['user_login']

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
app=Flask(__name__)
CORS(app)


UPLOAD_FOLDER = 'uploads'  # Define the upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.secret_key = "gymx.ai"
GOOGLE_CLIENT_ID = "779029076357-ptsdvsj2nj777lkl1ne1eq1dg8esmfkg.apps.googleusercontent.com"
client_secret_file = os.path.join(pathlib.Path(__file__).parent,"client_secret.json")
client = ""

flow = flow.Flow.from_client_secrets_file(client_secrets_file=client_secret_file
,scopes=["https://www.googleapis.com/auth/userinfo.profile","https://www.googleapis.com/auth/userinfo.email","openid"],
redirect_uri="http://127.0.0.1:5000/callback")

class Resume:
    def __init__(self,name,email,password,github,linkedin,project,experience,technical,soft,education):
        self.name=name,
        self.email=email,
        self.password=password,
        self.github=github,
        self.linkedin=linkedin,
        self.project=project,
        self.experience=experience,
        self.technical=technical,
        self.soft=soft,
        self.education=education
    def save(self):
        collection_resume.insert_one({
            'name': self.name,
            'password': self.password,
            'email': self.email,
            'github': self.github,
            'linkedin': self.linkedin,
            'project': self.project,
            'experience': self.experience,
            'technical': self.technical,
            'soft': self.soft,
            'education': self.education,
        })
    @staticmethod
    def find_by_email(email):
        user_data = collection_resume.find_one({'email': email})
        if user_data:
            return Resume(
                email=user_data['email'],
                password=user_data['password'],
                name=user_data['name'],
                github=user_data['github'],
                linkedin=user_data['linkedin'],
                project=user_data['project'],
                experience=user_data['experience'],
                technical=user_data['technical'],
                soft=user_data['soft'],
                education=user_data['education']
            )
        return None

class Job:
    def __init__(self,company,title,domain,experience,techincal_req, other_req,education,salary,link):
        self.company = company,
        self.title = title,
        self.domain = domain,
        self.experience= experience,
        self.technical_req = techincal_req,
        self.other_req =other_req,
        self.education = education,
        self.salary = salary,
        self.link=link
    def save(self):
        collection_job.insert_one({
            'company': self.company,
            'title': self.title,
            'domain': self.domain,
            'experience': self.experience,
            'technical_req': self.technical_req,
            'other_req': self.other_req,
            'education': self.education,
            'salary': self.salary,
            'link': self.link
        })

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
@app.route('/',endpoint='homepage_endpoint')
def indexpage():
    return render_template('index.html')

@app.route('/signuppage', endpoint='signuppage_endpoint')
def loginpage():
    return render_template('login.html')

@app.route('/signup', methods=['POST'],endpoint='signup_endpoint')
def register():
    email = request.form['email_sign']
    password = request.form['password_sign']
    name=request.form['name']
    password_hash = pbkdf2_sha256.hash(password)
    session['email'] = email
    session['password_hash'] = password_hash
    session['name']=name
    collection_user.insert_one({"email":email,"password":password_hash,"name":name})
    return redirect("/dashboard")

@app.route('/callback', endpoint='callback_endpoint')
def callback():
    flow.fetch_token(authorization_response=request.url)
    if not session["state"] == request.args["state"]:
        abort(500) #state does not match
    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )
    client = id_info
    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")
    session["first_name"] = id_info.get("given_name")
    session["userphoto"] = id_info.get("picture")
    session["password"]=""
    return redirect("/dashboard")


@app.route('/manuallogin', methods=['POST'], endpoint='manual_login_endpoint')
def manual_login():
    email = request.form['email']
    password = request.form['password']
    user = collection_user.find_one({'email': email})
    user = parse_json(user)
    print(user)
    if user and pbkdf2_sha256.verify(password, user['password']):
        session['email'] = user['email']
        session['name'] = user['name']


        return redirect(url_for('dashboard_endpoint'))
    else:
        flash('Invalid email or password. Please try again.', 'error')
        return redirect(url_for('loginpage_endpoint'))

@app.route('/login', methods=['GET', 'POST'], endpoint='login_endpoint')
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)



@app.route('/loginpage', endpoint='loginpage_endpoint')
def loginpage():
    return render_template('login.html')


@app.route('/logout', endpoint='logout_endpoint')
def logout():
    session.clear()
    return redirect('/')


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('loginpage_endpoint'))
        else:
            return function()
    return wrapper


def parse_json(data):
    return json.loads(json_util.dumps(data))


@app.route('/dashboard',endpoint="dashboard_endpoint")
def dashboard_call():
    if 'email' not in session:
        return redirect(url_for('loginpage_endpoint'))
    email = session['email']
    user=collection_resume.find_one({"email": email})
    user = parse_json(user)
    applied_data = list(collection_applied.find({"email" : email}))
    print(applied_data)
    applied_data=parse_json(applied_data)
    print(applied_data)
    job_data = list(collection_job.find().limit(50))
    for job in job_data:
        job['_id'] = str(job['_id'])
    job_data=parse_json(job_data)
    return render_template('dashboard.html',user=user,job_data=job_data,applied_data=applied_data)

@app.route('/clearData', methods=['POST'])
def clear_data():
    try:
        logging.debug("Received request to clear data")
        email=session["email"]
        result=collection_resume.delete_many({"email":email})
        if result.deleted_count > 0:
            return jsonify({"message": "Data cleared successfully."}), 200
        else:
            return jsonify({"message": "No data found to delete."}), 404
    except Exception as e:
        logging.error("Error occurred while clearing data", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400

    if file:
        session['file_name'] = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        try:
            parseResume(file_path)
            return jsonify({'message': 'File successfully uploaded and parsed'}), 200
        except Exception as e:
            print(e)
            return jsonify({'error': str(e)}), 500


@app.route('/applyjob', endpoint='autoapply_endpoint')
def autoapply():
    job_data = collection_job.find({"site":"linkedin"})
    job_data = parse_json(job_data)
    count=0
    not_eligible={}
    res=False
    try:
        for job in job_data:
            job_url = job.get('job_url')
            job_description = job.get('description')
            applied_data = list(collection_applied.find({"email": session['email'], "url": job_url}))
            if (len(applied_data) != 0): continue
            if(count==1):
                break
            matching_details = gemini_matcher(job_description)
            print(matching_details)
            matching_details=json.loads(matching_details)
            print(matching_details)
            percentage = matching_details.get('percentage')
            if not isinstance(percentage, int):
                number_str = percentage.replace('%', '')
                percentage = int(number_str)

            if percentage >= 50:
                print("above 50")
                linkedin_bot = Linkedin()
                res=linkedin_bot.applyJobs(url=str(job_url), email=str(session['email']))
                applied_data=list(collection_applied.find({"email":session['email'],"url":job_url}))
                if(len(applied_data)!=0):
                    count=count+1

            else:
                print("below 50")
                not_eligible[job_url]=matching_details
        if(res) : return jsonify({'Successfully Applied!'}),200
        else : return jsonify({'Couldnt Apply!'}),200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def parseResume(file_path):
    reader = PdfReader(file_path)
    page = reader.pages[0]
    data = page.extract_text()
    prompt = '''
          You are an skilled Resume scanner with a deep understanding of computer science, data science, Full stack Web development, Big Data Engineering, DEVOPS,Data Analyst, ATS functionality, You are given with resume and your job is to extract the following information from the resume with atmost accuracy and precision.
          If any Data is not found then assign it with "Not Found".:
         1. name
         2. email_id
         3. github_portfolio
         4. linkedin_id
         5. projects with project_number and explanation of the project
         6. employment_details along with company_details and responsibilities
         7. technical_skills
         8. soft_skills
         9. education with degree, institution, gpa

         All the above information should be presented in JSON format for storing in MongoDb with the column names as specified above.)
         '''
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("calling GEMINI for Parsing")
    response = model.generate_content(prompt + data)
    print("Response generated from GEMINI")
    data = response.candidates[0].content.parts[0].text
    cleaned_json = data.replace('```json', '```').replace("```", "").replace('\n', '')
    data_put = json.loads(cleaned_json)
    data_put['email'] = session['email']
    existing = collection_resume.find_one({"email": session['email']})
    print("Inserting in Mongo")
    if(existing) :
        collection_resume.replace_one({"email":session['email']},data_put)
    else :
        collection_resume.insert_one(data_put)


def gemini_matcher(job_description):
    if 'email' not in session:
        return redirect(url_for('loginpage_endpoint'))
    email = session['email']
    user=collection_resume.find_one({"email": email})
    user = parse_json(user)
    combined_input = f"Job Description:\n{job_description}\n\nResume:\n{user}"
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt2 = """
       You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science, Full stack Web development, Big Data Engineering, DEVOPS,Data Analyst,  and ATS functionality, 
       your task is to evaluate the resume against the provided job description. give me the percentage of match in INTEGER(Numeric) form if the resume matches
       the job description. Return The data in Json Format for "percentage","Missing Keywords","Feedback". No other explaination required
       """
    response = model.generate_content([combined_input, prompt2])
    data = response.candidates[0].content.parts[0].text
    cleaned_json = data.replace('```json', '```').replace("```", "").replace('\n', '')
    return cleaned_json

def job_scraper_admin():
    jobs = scrape_jobs(
        site_name=["linkedin", "glassdoor"],
        search_term="software engineer",
        location="bengaluru",
        results_wanted=20,
        easy_apply=True,
        country_glassdoor='india',  # only needed for Glassdoor
        linkedin_fetch_description=True  # Get full description, direct job URL, company industry and job level (slower)
    )

    print(f"Found {len(jobs)} jobs")
    print("Columns in jobs DataFrame:", jobs.columns)
    print(jobs[['site']].value_counts())


    job_data = []
    for index, row in jobs.iterrows():
        if row.get('description'):
            description_html = row['description']
            description_md = md(description_html)
        else:
            description_md = None

        job_entry = {
            "title": row.get('title'),
            "company": row.get('company'),
            "location": row.get('location'),
            "description": description_md,
            "job_url": row.get('job_url'),
            "site": row.get('site')
        }

        print(job_entry)
        job_data.append(job_entry)

    collection_job.insert_many(job_data)
    print(f"Inserted {len(job_data)} jobs into MongoDB")

if __name__ == '__main__':
    app.run()

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
from pymongo import MongoClient
from markdownify import markdownify as md
from SeleniumAutomator.linkedin_bot import Linkedin

client=MongoClient("mongodb+srv://user:"+urllib.parse.quote("fitpulse")+"@cluster0.urlcyfn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db=client['jobpilot']
collection_resume=db['parsed']
collection_job=db['job']
collection_applied=db['applied']

def job_scraper_admin():

    jobs = scrape_jobs(
        site_name=["linkedin"],
        location='bengaluru',
        search_term="software",
        results_wanted=30,
        easy_apply=True
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

job_scraper_admin()
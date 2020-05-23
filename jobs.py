#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests
from urllib import parse
from datetime import datetime, timedelta
import base64
import hashlib
from ago import human
from langdetect import detect
import config

# Load config
site_name = config.site_name.lower()
keyword_list = config.keyword_list
country_blacklist = config.country_blacklist
language_whitelist = config.language_whitelist
strict_search = config.strict_search

get_job_details = False

jobs_list = []


def scrape_jobs(keyword):

    us_states = ['AK', 'AL', 'AR', 'AS', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'GU', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MP',
                 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UM', 'UT', 'VA', 'VI', 'VT', 'WA', 'WI', 'WV', 'WY']
    keywords_escaped = parse.quote(keyword).lower()
    url = 'https://www.'+config.site_name+'.com/jobs/search/?distance=25&geoId=92000000&keywords=' + \
        keywords_escaped+'&location=Worldwide'

    # Set request headers
    headers = requests.utils.default_headers()
    headers.update(
        {'User Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0'})

    # Get request
    print(f"Getting {url}")
    req = requests.get(url, headers)
    soup = BeautifulSoup(req.content, 'html.parser')

    jobs = soup.findAll("div", {"class": "job-result-card__contents"})
    jobs = soup.findAll("li", {
                        "class": "result-card"})

    for job in jobs:
        this_job = {}
        this_job["title"] = job.select_one(
            'h3', {"class": "result-card__title"}).contents[0]
        print(f"Getting {this_job['title']}")
        try:
            url = job.select(
                'a', {"class": "result-card__full-card-link"}, href=True)
            this_job["url"] = url[0]["href"]
            this_job["company_url"] = url[1]["href"]
        except:
            pass
        try:
            details = (job.select(
                'a', {"class": "result-card__full-card-link"}))
            this_job["company"] = details[1].text
        except:
            this_job["company"] = "Unknown"

        hash_string = this_job["company"] + this_job["title"]
        this_job["hash"] = hashlib.sha1(
            hash_string.encode('utf-8')).hexdigest()[:8]

        this_job["location"] = job.select(
            'span', {"class": "job-result-card__location"})[1].text

        state = this_job["location"].split(",")[-1].strip()
        if state in us_states:
            this_job["country"] = 'USA'
        else:
            this_job["country"] = state

        time = job.select_one('time')
        if 'new' in time["class"][0]:
            badge_string = " <span class='badge badge-secondary'>New</span>"
            this_job["is_new"] = True
            this_job["title"] += badge_string
        else:
            this_job["is_new"] = False

        this_job["time"] = time["datetime"]

        year = int(this_job["time"].split("-")[0])
        month = int(this_job["time"].split("-")[1])
        day = int(this_job["time"].split("-")[2])

        job_date = datetime(year=year, month=month, day=day)
        this_job["timedelta"] = human(job_date, 1)

        try:
            this_job["desc"] = job.select_one(
                'p', {"class": "job-result-card__snippet"}).text
        except:
            pass

        if get_job_details:
            this_job["long_desc"] = scrape_details(this_job["url"])

        filter_job(this_job)

        if this_job["country"] not in country_blacklist:
            jobs_list.append(this_job)

    return jobs_list


def scrape_details(url):
    headers = requests.utils.default_headers()
    headers.update(
        {'User Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0'})

    req = requests.get(url, headers, timeout=1)
    soup = BeautifulSoup(req.content, 'html.parser')
    long_desc = soup.find(
        'div', {"class": "description__text description__text--rich"})

    return long_desc


def scrape_all(keyword_list):
    jobs = []
    for keyword in keyword_list:
        keyword_jobs = scrape_jobs(keyword)
        jobs.extend(keyword_jobs)

    no_duplicates = []
    for job in jobs:
        if job not in no_duplicates:
            no_duplicates.append(job)

    jobs = no_duplicates

    # sort by new
    jobs = sorted(jobs, key=lambda k: k['time'], reverse=True)

    return jobs


def filter_job(job):
    """
    Take a dictionary and filter based on criteria
    """
    if "desc" in job:
        language = str(detect(job["desc"]))
    else:
        language = str(detect(job["title"]))
    # print(language)
    if job["country"] not in country_blacklist and language in language_whitelist:
        if strict_search:
            for keyword in keyword_list:
                keyword = keyword.lower()
                job_title = job["title"].lower()
                if keyword in job_title:
                    jobs_list.append(job)
        else:
            jobs_list.append(job)


def create_html(jobs):
    output_filename = "output.html"
    html_content = ""
    for job in jobs:
        with open("template_job.html") as job_file:
            job_content = job_file.read()
            job_content = replace_from_dict(job_content, job)

            html_content += job_content

    with open("template_page.html") as page_file:
        page = page_file.read()
        page_populated = page.replace("%DATA%", html_content)
        datetime_string = datetime.now().strftime("%d %b %Y at %I:%M %p")
        page_populated = page_populated.replace(
            "%datetime%", datetime_string)

    output_file = open(output_filename, "w+")
    output_file.write(page_populated)
    print(f"Jobs written to {output_filename}")


def main():
    all_jobs = scrape_all(keyword_list)

    create_html(all_jobs)


def replace_from_dict(text, dictionary):
    for key in dictionary.keys():
        replace_string = "%" + key + "%"
        text = text.replace(replace_string, str(dictionary[key]))

    return text


if __name__ == "__main__":
    main()

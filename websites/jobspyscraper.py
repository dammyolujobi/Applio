from jobspy import scrape_jobs
import json
from dataclasses import dataclass


job_store = []

@dataclass
class JobListing:
    title: str
    company: str
    description: str
    date: str
    job_url: str
    company_url: str

async def scrape(role:str,location_of_job:str,country:str = "Nigeria"):
    jobs = scrape_jobs(
        site_name=["indeed", "linkedin", "zip_recruiter", "google"], # "glassdoor", "bayt", "naukri", "bdjobs"
        search_term=role,
        google_search_term=f"{role} in {location_of_job} Since Yesterday",
        location=location_of_job,
        results_wanted=40,
        hours_old=72,
        country_indeed=country,
        
        # linkedin_fetch_description=True # gets more info such as description, direct job url (slower)
        # proxies=["208.195.175.46:65095", "208.195.175.45:65095", "localhost"],
    )
    
    job_structured = json.loads(jobs.to_json(orient="records",date_format="iso"))

    for job in job_structured:
        job_store.append(JobListing(
            title = job["title"],
            company= job["company"],
            description=job["description"],
            date = job["date_posted"],
            job_url=job["job_url"],
            company_url=job["job_url_direct"]
        ))
    
    
    return job_store
    
    
import csv
from jobspy import scrape_jobs
from fastapi import APIRouter,Depends
from router.user import get_current_user

router = APIRouter(
    tags=["Scraper"]
)

@router.get("/scrape")
async def scrape(role:str,location_of_job:str,country,user:dict = Depends(get_current_user)):
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
    
    return jobs
from fastapi import APIRouter
from fastapi import APIRouter,Depends
from router.user import get_current_user
from websites.apple import scrape_apple_jobs
from websites.jobberman import scrape_jobberman
from websites.jobmag import scrape_myjobmag
from websites.jobspyscraper import scrape
router= APIRouter(
    tags=["Aggregator"]
)


@router.post("/aggregate")
async def aggregate_result(role:str,location_of_job:str,current_user = Depends(get_current_user)):
    
    jobberman = await scrape_jobberman(role,location_of_job)
    jobmag = await scrape_myjobmag(role,location_of_job)
    jobspy = await scrape(role,location_of_job)
    apple = await scrape_apple_jobs(role)

    combined_result =jobmag + jobspy + jobberman

    return {
        "Jobs In Nigeria":combined_result,
        "Work at Apple" : apple,
        "Number of Jobs Found" : len(combined_result + apple)
    }
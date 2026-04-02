from jobspy import scrape_jobs
import json
from dataclasses import dataclass
from typing import Optional


@dataclass
class JobListing:
    title: str
    company: Optional[str]
    description: Optional[str]
    date: Optional[str]
    job_url: str
    company_url: Optional[str]


def is_relevant(title: str, role: str) -> bool:
    title_lower = title.lower()
    # Split the role into individual words and check if ANY appear in the title
    # e.g. "graphic designer" → ["graphic", "designer"]
    role_keywords = role.lower().split()
    return any(kw in title_lower for kw in role_keywords)


async def scrape(role: str, location: str, country: str = "nigeria") -> list[JobListing]:
    jobs = scrape_jobs(
        site_name=["indeed", "linkedin", "zip_recruiter", "google"],
        search_term=role,
        google_search_term=f"{role} jobs in {location} Nigeria",
        location=location,
        results_wanted=40,
        hours_old=72,
        country_indeed=country,
    )

    job_structured = json.loads(jobs.to_json(orient="records", date_format="iso"))

    seen_urls = set()
    job_store = []

    for job in job_structured:
        title = job.get("title") or ""
        url = job.get("job_url") or ""

        if url in seen_urls:
            continue
        seen_urls.add(url)

        if not is_relevant(title, role):
            continue

        job_store.append(JobListing(
            title=title,
            company=job.get("company"),
            description=job.get("description"),
            date=job.get("date_posted"),
            job_url=url,
            company_url=job.get("job_url_direct"),
        ))

    return job_store

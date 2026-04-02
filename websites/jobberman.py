import requests
import json
import re
from bs4 import BeautifulSoup
from dataclasses import dataclass

BASE_URL = "https://www.jobberman.com"

@dataclass
class JobListing:
    title: str
    company: str
    description: str
    date: str
    job_url: str
    company_url: str

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

async def scrape_jobberman(keyword: str, location: str) -> list[JobListing]:
    response = requests.get(
        f"{BASE_URL}/jobs/{location.lower()}",
        params={"q": keyword},
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []


    cards = soup.find_all(attrs={"data-cy": "listing-cards-components"})

    for card in cards:
        title_tag = card.find(attrs={"data-cy": "listing-title-link"})
        title = title_tag.get_text(strip=True) if title_tag else ""
        job_url = title_tag["href"] if title_tag and title_tag.has_attr("href") else ""

  
        company_tag = card.find("a", href=lambda h: h and "/company/" in h)
        company = company_tag.get_text(strip=True) if company_tag else ""
        company_url = company_tag["href"] if company_tag else ""

        # Short description / snippet
        desc_tag = card.find("p")  # Usually the first <p> is a snippet
        description = desc_tag.get_text(strip=True) if desc_tag else ""

       
        time_tag = card.find("time")
        date = time_tag.get_text(strip=True) if time_tag else ""

        jobs.append(JobListing(
            title=title,
            company=company,
            description=description,
            date=date,
            job_url=job_url,
            company_url=company_url,
        ))

    return jobs



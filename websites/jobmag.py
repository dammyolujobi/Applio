import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass

BASE_URL = "https://www.myjobmag.com"

@dataclass
class JobListing:
    title: str
    company: str
    description: str
    date: str
    job_url: str
    company_url: str


def scrape_myjobmag(keyword: str, location: str) -> list[JobListing]:
    response = requests.get(
        f"{BASE_URL}/search/jobs",
        params={
            "q": keyword,
            "location": location,
            "location-sinput": location
        },
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.select("li.job-list-li")

    listings = []

    for card in cards:
        
        title_tag = card.select_one("li.job-info h2 a")
        title     = title_tag.get_text(strip=True) if title_tag else None
        job_url   = BASE_URL + title_tag["href"] if title_tag else None

       
        logo_link   = card.select_one("li.job-logo a")
        company_url = BASE_URL + logo_link["href"] if logo_link else None

        
        logo_img = card.select_one("li.job-logo img")
        company  = logo_img["alt"] if logo_img else None

    
        desc_tag    = card.select_one("li.job-desc")
        description = desc_tag.get_text(strip=True) if desc_tag else None

        # Date
        date_tag = card.select_one("li#job-date")
        date     = date_tag.get_text(strip=True) if date_tag else None

        if title:  # skip malformed cards
            listings.append(JobListing(
                title=title,
                company=company,
                description=description,
                date=date,
                job_url=job_url,
                company_url=company_url
            ))

    return listings


# Usage
jobs = scrape_myjobmag("backend developer", "Lagos")
for job in jobs:
    print(job)
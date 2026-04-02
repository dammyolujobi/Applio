import requests
import json
import re
from bs4 import BeautifulSoup
from dataclasses import dataclass
import re

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

    with open("results.txt","w",encoding="utf-8") as file:
                  file.write(response.text)
    jobs = []

    
    cards = soup.find_all(attrs={"data-cy": "listing-cards-components"})
    
    for card in cards:
        title_tag = card.find(attrs={"data-cy": "listing-title-link"})
        title = title_tag.get_text(strip=True) if title_tag else ""
        job_url = title_tag["href"] if title_tag and title_tag.has_attr("href") else ""

  
        company_tag = card.find("p",class_ = "text-sm text-blue-700 text-loading-animate inline-block mt-3")
        company = company_tag.get_text(strip=True) if company_tag else ""


        
        desc_tag = card.find("p", class_="text-sm font-normal text-gray-700 md:text-gray-500 md:pl-5")
        description = desc_tag.get_text(strip=True) if desc_tag else ""
       
        date_tag = card.find("p", class_="text-sm font-normal text-gray-700 text-loading-animate")
        date = date_tag.get_text(strip=True) if date_tag else ""

        jobs.append(JobListing(
            title=title,
            company=company,
            description=description,
            date=date,
            job_url=job_url,
            company_url="",
        ))

    return jobs


# scrape_jobberman("backend","lagos")

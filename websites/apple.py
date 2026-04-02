import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
import re
import json
BASE_URL = "https://jobs.apple.com"


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

async def scrape_apple_jobs(keyword:str):
    response = requests.get(f"{BASE_URL}/search",
                            params={"search":keyword},
                            headers=headers,
                            timeout=10)
    
    jobs = []

    response.raise_for_status()
    soup = BeautifulSoup(response.text,"html.parser")
    
    script_tag = soup.find("script", string= re.compile("__staticRouterHydrationData"))
    raw = script_tag.string

    json_str = re.search(r'JSON\.parse\("(.+)"\);$', raw, re.DOTALL).group(1)

    json_str = json_str.encode().decode('unicode_escape')

    data = json.loads(json_str)

    main_section = data["loaderData"]["search"]["searchResults"]

    for section in range(0,len(main_section)):

        description = main_section[section]["jobSummary"]
        title = main_section[section]["postingTitle"]
        date = main_section[section]["postingDate"]
        id = main_section[section]["id"]
        transformed_posting_title = main_section[section]["transformedPostingTitle"]

        # team_code = main_section[section]["team"]["teamCode"]
        job_url = f"https://jobs.apple.com/en-us/details/{id}/{transformed_posting_title}"
        
        jobs.append(
            JobListing(
                title=title,
                company="Apple",
                description=description,
                date=date,
                job_url=job_url,
                company_url="apple.com",
            )
        )

    return jobs
    
    

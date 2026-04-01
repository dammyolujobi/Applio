import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass

BASE_URL = "https://jobs.apple.com/"

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
def scrape_apple_jobs(keyword:str,location:str = None):
    response = requests.get(f"{BASE_URL}/search",
                            params={"search":keyword},
                            headers=headers,
                            timeout=10)
    
    response.raise_for_status()
    soup = BeautifulSoup(response.text,"html.parser")

    with open("result.txt","w",encoding="utf-8") as file:
        file.write(response.text)

scrape_apple_jobs("backend")
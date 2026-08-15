from jobspy import scrape_jobs
import json
from typing import Optional, List, Dict, Any
import asyncio

def is_relevant(title: str, role: str) -> bool:
    title_lower = title.lower()
    role_keywords = role.lower().split()
    return any(kw in title_lower for kw in role_keywords)

async def scrape_with_details(role: str, location: str, country: str = "nigeria") -> List[Dict[str, Any]]:
    """
    Scrape jobs from multiple platforms using jobspy with error handling
    Returns a list of job dictionaries
    """
    try:
        jobs_df = scrape_jobs(
            site_name=["indeed", "linkedin", "zip_recruiter", "google"],
            search_term=role,
            google_search_term=f"{role} jobs in {location} Nigeria",
            location=location if location else "Nigeria",
            results_wanted=40,
            hours_old=72,
            country_indeed=country,
        )
        
        if jobs_df.empty:
            return []
        
        job_structured = json.loads(jobs_df.to_json(orient="records", date_format="iso"))
        
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
            
            job_store.append({
                "title": title,
                "company": job.get("company"),
                "description": job.get("description"),
                "date_posted": job.get("date_posted"),
                "job_url": url,
                "job_url_direct": job.get("job_url_direct"),
                "location": job.get("location"),
                "interval": job.get("interval"),
                "job_type": job.get("job_type"),
                "source": "jobspy"
            })
        
        return job_store
    
    except Exception as e:
        print(f"Error in jobspy scraper: {e}")
        return []

# Keep the old function name for backward compatibility
scrape = scrape_with_details

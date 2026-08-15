from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import hashlib
import json
from schemas.schema import (
    JobFilter, JobSort, PaginationParams, JobListing, JobDetail,
    AggregatedJobsResponse, SearchHistory
)
from router.user import get_current_user, log_user_activity
from utils.setup import (
    job_cache_collection, search_history_collection, user_activity_collection,
    admin_stats_collection
)
from websites.apple import scrape_apple_jobs
from websites.jobberman import scrape_jobberman
from websites.jobmag import scrape_myjobmag
from websites.jobspyscraper import scrape_with_details

router = APIRouter(
    tags=["Aggregator"]
)

# Cache TTL in seconds
CACHE_TTL = 3600  # 1 hour

def generate_cache_key(role: str, location: str, filters: dict = None) -> str:
    """Generate a unique cache key based on search parameters"""
    key_data = f"{role}:{location}:{json.dumps(filters or {}, sort_keys=True)}"
    return hashlib.md5(key_data.encode()).hexdigest()

def get_cached_results(cache_key: str) -> Optional[List[dict]]:
    """Retrieve cached job results if not expired"""
    cached = job_cache_collection.find_one({
        "_id": cache_key,
        "expires_at": {"$gt": datetime.utcnow()}
    })
    if cached:
        return cached.get("jobs", [])
    return None

def cache_results(cache_key: str, jobs: List[dict], ttl: int = CACHE_TTL):
    """Cache job results with expiration"""
    job_cache_collection.update_one(
        {"_id": cache_key},
        {
            "$set": {
                "jobs": jobs,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(seconds=ttl)
            }
        },
        upsert=True
    )

def filter_jobs(jobs: List[JobListing], filters: JobFilter) -> List[JobListing]:
    """Apply filters to job listings"""
    filtered = jobs
    
    if filters.job_type:
        filtered = [j for j in filtered if j.job_type == filters.job_type.value]
    
    if filters.experience_level:
        filtered = [j for j in filtered if j.experience_level == filters.experience_level.value]
    
    if filters.min_salary or filters.max_salary:
        def salary_match(job):
            if not job.salary:
                return False
            # Simple salary parsing - can be enhanced
            return True
        filtered = [j for j in filtered if salary_match(j)]
    
    if filters.company:
        filtered = [j for j in filtered if filters.company.lower() in (j.company or "").lower()]
    
    if filters.location:
        filtered = [j for j in filtered if filters.location.lower() in (j.location or "").lower()]
    
    return filtered

def sort_jobs(jobs: List[JobListing], sort_by: JobSort) -> List[JobListing]:
    """Sort job listings"""
    reverse = sort_by.order == "desc"
    
    if sort_by.field == "date":
        return sorted(jobs, key=lambda x: x.date or "", reverse=reverse)
    elif sort_by.field == "salary":
        # Would need proper salary parsing
        return jobs
    elif sort_by.field == "relevance":
        return jobs
    
    return jobs

def paginate_jobs(jobs: List[JobListing], page: int, page_size: int) -> tuple:
    """Paginate job listings"""
    total = len(jobs)
    total_pages = (total + page_size - 1) // page_size
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    paginated = jobs[start_idx:end_idx]
    
    return paginated, {
        "total_count": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }

@router.post("/aggregate", response_model=AggregatedJobsResponse)
async def aggregate_jobs(
    job_filter: JobFilter,
    sort: JobSort = JobSort(),
    pagination: PaginationParams = PaginationParams(),
    use_cache: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """
    Aggregate jobs from multiple sources with filtering, sorting, and pagination
    """
    # Generate cache key
    cache_key = generate_cache_key(
        job_filter.role, 
        job_filter.location or "", 
        job_filter.model_dump(exclude_unset=True)
    )
    
    # Try to get cached results
    cached_jobs = None
    if use_cache:
        cached_jobs = get_cached_results(cache_key)
    
    if cached_jobs:
        # Convert cached dicts back to JobListing objects
        jobs = [JobListing(**j) for j in cached_jobs]
    else:
        # Scrape from all sources with error handling
        all_jobs = []
        
        # Jobberman (Nigeria-focused)
        try:
            jobberman_jobs = await scrape_jobberman(job_filter.role, job_filter.location or "Nigeria")
            for job in jobberman_jobs:
                all_jobs.append(JobListing(
                    title=job.title,
                    company=job.company,
                    description=job.description,
                    date=job.date,
                    job_url=job.job_url,
                    company_url=job.company_url,
                    location=job_filter.location or "Nigeria",
                    source="jobberman"
                ))
        except Exception as e:
            print(f"Jobberman scraper failed: {e}")
        
        # MyJobMag (Nigeria-focused)
        try:
            jobmag_jobs = await scrape_myjobmag(job_filter.role, job_filter.location or "Nigeria")
            for job in jobmag_jobs:
                all_jobs.append(JobListing(
                    title=job.title,
                    company=job.company,
                    description=job.description,
                    date=job.date,
                    job_url=job.job_url,
                    company_url=job.company_url,
                    location=job_filter.location or "Nigeria",
                    source="myjobmag"
                ))
        except Exception as e:
            print(f"MyJobMag scraper failed: {e}")
        
        # JobSpy (Indeed, LinkedIn, etc.)
        try:
            jobspy_jobs = await scrape_with_details(job_filter.role, job_filter.location or "Nigeria")
            for job in jobspy_jobs:
                all_jobs.append(JobListing(
                    title=job.get("title", ""),
                    company=job.get("company", ""),
                    description=job.get("description"),
                    date=job.get("date_posted"),
                    job_url=job.get("job_url", ""),
                    company_url=job.get("job_url_direct"),
                    location=job.get("location"),
                    salary=job.get("interval"),
                    job_type=job.get("job_type"),
                    source="jobspy"
                ))
        except Exception as e:
            print(f"JobSpy scraper failed: {e}")
        
        # Apple Jobs (global, ignores location)
        try:
            apple_jobs = await scrape_apple_jobs(job_filter.role)
            for job in apple_jobs:
                all_jobs.append(JobListing(
                    title=job.title,
                    company=job.company,
                    description=job.description,
                    date=job.date,
                    job_url=job.job_url,
                    company_url=job.company_url,
                    location="Global",
                    source="apple"
                ))
        except Exception as e:
            print(f"Apple scraper failed: {e}")
        
        # Remove duplicates based on job URL
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job.job_url not in seen_urls:
                seen_urls.add(job.job_url)
                unique_jobs.append(job)
        
        jobs = unique_jobs
        
        # Cache the results
        if jobs:
            cache_results(cache_key, [j.model_dump() for j in jobs])
    
    # Apply filters
    filtered_jobs = filter_jobs(jobs, job_filter)
    
    # Apply sorting
    sorted_jobs = sort_jobs(filtered_jobs, sort)
    
    # Apply pagination
    paginated_jobs, pagination_info = paginate_jobs(
        sorted_jobs, 
        pagination.page, 
        pagination.page_size
    )
    
    # Log search activity
    if current_user:
        await log_user_activity(current_user["email"], "search", {
            "role": job_filter.role,
            "location": job_filter.location,
            "results_count": len(paginated_jobs)
        })
        
        # Save to search history
        search_history_collection.insert_one({
            "user_email": current_user["email"],
            "query": job_filter.role,
            "location": job_filter.location,
            "filters": job_filter.model_dump(exclude_unset=True),
            "timestamp": datetime.utcnow()
        })
    
    # Update admin stats
    admin_stats_collection.update_one(
        {},
        {
            "$inc": {"total_searches": 1},
            "$set": {"last_updated": datetime.utcnow()}
        },
        upsert=True
    )
    
    return AggregatedJobsResponse(
        jobs=paginated_jobs,
        **pagination_info,
        filters_applied=job_filter.model_dump(exclude_unset=True)
    )

@router.get("/jobs/{job_id}", response_model=JobDetail)
async def get_job_details(
    job_id: str,
    source: str = Query(..., description="Source of the job (jobberman, myjobmag, jobspy, apple)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed information about a specific job
    """
    # This would ideally fetch the full job description from the source
    # For now, we'll return a placeholder that can be enhanced
    
    job_detail = JobDetail(
        job_id=job_id,
        title="Software Engineer",
        company="Tech Company",
        description="Full job description would be fetched from source...",
        job_url=f"https://example.com/job/{job_id}",
        location="Lagos, Nigeria",
        salary="$50,000 - $80,000",
        job_type="full_time",
        experience_level="mid",
        source=source,
        requirements=[
            "Bachelor's degree in Computer Science or related field",
            "3+ years of experience in software development",
            "Proficiency in Python, JavaScript, or similar languages"
        ],
        benefits=[
            "Health insurance",
            "Remote work options",
            "Professional development budget"
        ],
        remote_option=True
    )
    
    # Log view activity
    await log_user_activity(current_user["email"], "view_job", {
        "job_id": job_id,
        "source": source
    })
    
    return job_detail

@router.get("/stats")
async def get_aggregation_stats(current_user: dict = Depends(get_current_user)):
    """Get statistics about job aggregations"""
    stats = {
        "cache_size": job_cache_collection.count_documents({}),
        "sources": ["jobberman", "myjobmag", "jobspy", "apple"],
        "last_updated": datetime.utcnow()
    }
    return stats

@router.delete("/cache")
async def clear_cache(
    role: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Clear cached job results"""
    if role:
        # Clear cache for specific role
        result = job_cache_collection.delete_many({})
        return {"message": f"Cleared {result.deleted_count} cache entries for role: {role}"}
    else:
        # Clear all cache
        result = job_cache_collection.delete_many({})
        return {"message": f"Cleared {result.deleted_count} cache entries"}

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from utils.setup import (
    user_collection, 
    saved_jobs_collection, 
    job_alerts_collection, 
    applications_collection,
    search_history_collection,
    user_activity_collection
)
from typing import Annotated, Optional, List
from datetime import datetime, timedelta
from jose import JWTError
from schemas.schema import (
    User, UserUpdate, PasswordChange, SavedJob, JobAlert, 
    Application, SearchHistory, TokenResponse, RefreshTokenRequest
)
from utils.auth import (
    create_access_token, create_refresh_token, 
    verify_access_token, verify_refresh_token,
    hash_password, verify_password
)
import bcrypt

router = APIRouter(
    prefix="/users",
    tags=["User"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    payload = verify_access_token(token)
    if payload is None:
        raise credentials_exception
    
    email = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    user = user_collection.find_one({"email": email})
    if user is None:
        raise credentials_exception
    
    return user

async def log_user_activity(email: str, action: str, details: dict = None):
    activity = {
        "user_email": email,
        "action": action,
        "details": details or {},
        "timestamp": datetime.utcnow()
    }
    user_activity_collection.insert_one(activity)

@router.post("/register", response_model=dict)
async def register_user(user: User):
    # Check if email already exists
    if user_collection.find_one({"email": user.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_pw = hash_password(user.password)
    
    user_data = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "password": hashed_pw,
        "phone": None,
        "location": None,
        "bio": None,
        "skills": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active": True
    }
    
    user_collection.insert_one(user_data)
    
    access_token = create_access_token({"email": user.email})
    refresh_token = create_refresh_token({"email": user.email})
    
    await log_user_activity(user.email, "register", {"source": "api"})
    
    return {
        "message": "Successfully registered",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/login", response_model=TokenResponse)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = user_collection.find_one({"email": form_data.username})
    
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    access_token = create_access_token({"email": user["email"]})
    refresh_token = create_refresh_token({"email": user["email"]})
    
    await log_user_activity(user["email"], "login", {"ip": "unknown"})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=60
    )

@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    payload = verify_refresh_token(request.refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    email = payload.get("sub")
    user = user_collection.find_one({"email": email})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    new_access_token = create_access_token({"email": email})
    new_refresh_token = create_refresh_token({"email": email})
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=60
    )

@router.get("/me")
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    user_data = {
        "first_name": current_user.get("first_name"),
        "last_name": current_user.get("last_name"),
        "email": current_user.get("email"),
        "phone": current_user.get("phone"),
        "location": current_user.get("location"),
        "bio": current_user.get("bio"),
        "skills": current_user.get("skills", []),
        "created_at": current_user.get("created_at")
    }
    return user_data

@router.put("/me")
async def update_user_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    update_data = user_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    user_collection.update_one(
        {"email": current_user["email"]},
        {"$set": update_data}
    )
    
    await log_user_activity(current_user["email"], "update_profile", update_data)
    
    return {"message": "Profile updated successfully"}

@router.post("/change-password")
async def change_password(
    password_change: PasswordChange,
    current_user: dict = Depends(get_current_user)
):
    if not verify_password(password_change.current_password, current_user["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    if len(password_change.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters"
        )
    
    hashed_new_password = hash_password(password_change.new_password)
    
    user_collection.update_one(
        {"email": current_user["email"]},
        {"$set": {"password": hashed_new_password, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Password changed successfully"}

# Saved Jobs Endpoints
@router.post("/saved-jobs")
async def save_job(
    saved_job: SavedJob,
    current_user: dict = Depends(get_current_user)
):
    saved_job.user_email = current_user["email"]
    saved_job.saved_at = datetime.utcnow()
    
    # Check if already saved
    existing = saved_jobs_collection.find_one({
        "user_email": current_user["email"],
        "job_id": saved_job.job_id
    })
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job already saved"
        )
    
    saved_jobs_collection.insert_one(saved_job.model_dump())
    await log_user_activity(current_user["email"], "save_job", {"job_id": saved_job.job_id})
    
    return {"message": "Job saved successfully"}

@router.get("/saved-jobs")
async def get_saved_jobs(current_user: dict = Depends(get_current_user)):
    jobs = list(saved_jobs_collection.find({"user_email": current_user["email"]}))
    for job in jobs:
        job["_id"] = str(job["_id"])
    return {"saved_jobs": jobs, "count": len(jobs)}

@router.delete("/saved-jobs/{job_id}")
async def unsave_job(job_id: str, current_user: dict = Depends(get_current_user)):
    result = saved_jobs_collection.delete_one({
        "user_email": current_user["email"],
        "job_id": job_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved job not found"
        )
    
    return {"message": "Job removed from saved list"}

# Job Alerts Endpoints
@router.post("/alerts")
async def create_job_alert(
    alert: JobAlert,
    current_user: dict = Depends(get_current_user)
):
    alert.user_email = current_user["email"]
    alert.is_active = True
    
    alert_id = job_alerts_collection.insert_one(alert.model_dump()).inserted_id
    
    await log_user_activity(current_user["email"], "create_alert", {
        "role_keywords": alert.role_keywords
    })
    
    return {"message": "Job alert created", "alert_id": str(alert_id)}

@router.get("/alerts")
async def get_job_alerts(current_user: dict = Depends(get_current_user)):
    alerts = list(job_alerts_collection.find({"user_email": current_user["email"]}))
    for alert in alerts:
        alert["_id"] = str(alert["_id"])
    return {"alerts": alerts}

@router.put("/alerts/{alert_id}")
async def update_job_alert(
    alert_id: str,
    is_active: bool,
    current_user: dict = Depends(get_current_user)
):
    result = job_alerts_collection.update_one(
        {"_id": alert_id, "user_email": current_user["email"]},
        {"$set": {"is_active": is_active}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    return {"message": "Alert updated successfully"}

@router.delete("/alerts/{alert_id}")
async def delete_job_alert(alert_id: str, current_user: dict = Depends(get_current_user)):
    result = job_alerts_collection.delete_one({
        "_id": alert_id,
        "user_email": current_user["email"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    return {"message": "Alert deleted successfully"}

# Applications Tracking Endpoints
@router.post("/applications")
async def track_application(
    application: Application,
    current_user: dict = Depends(get_current_user)
):
    application.user_email = current_user["email"]
    application.applied_date = datetime.utcnow()
    
    app_id = applications_collection.insert_one(application.model_dump()).inserted_id
    
    await log_user_activity(current_user["email"], "apply", {
        "job_id": application.job_id,
        "company": application.company
    })
    
    return {"message": "Application tracked", "application_id": str(app_id)}

@router.get("/applications")
async def get_applications(
    current_user: dict = Depends(get_current_user),
    status_filter: Optional[str] = None
):
    query = {"user_email": current_user["email"]}
    if status_filter:
        query["status"] = status_filter
    
    apps = list(applications_collection.find(query))
    for app in apps:
        app["_id"] = str(app["_id"])
    
    return {"applications": apps, "count": len(apps)}

@router.put("/applications/{app_id}")
async def update_application(
    app_id: str,
    status: str,
    notes: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    update_data = {"status": status}
    if notes:
        update_data["notes"] = notes
    
    result = applications_collection.update_one(
        {"_id": app_id, "user_email": current_user["email"]},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    return {"message": "Application updated successfully"}

# Search History
@router.post("/search-history")
async def log_search(
    search: SearchHistory,
    current_user: dict = Depends(get_current_user)
):
    search.user_email = current_user["email"]
    search.timestamp = datetime.utcnow()
    
    search_history_collection.insert_one(search.model_dump())
    
    return {"message": "Search logged"}

@router.get("/search-history")
async def get_search_history(
    current_user: dict = Depends(get_current_user),
    limit: int = 20
):
    searches = list(search_history_collection.find(
        {"user_email": current_user["email"]}
    ).sort("timestamp", -1).limit(limit))
    
    for search in searches:
        search["_id"] = str(search["_id"])
    
    return {"search_history": searches}

from fastapi import APIRouter,Depends,HTTPException,status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from utils.setup import user_collection
from typing import Annotated
from jose import JWTError
from jose import jwt
from utils.auth import create_access_token,create_refresh_token,auth_password
from schemas.schema import User
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
router = APIRouter(
    prefix="/users",
    tags=["User"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

@router.get("/create_user")
async def create_user(user:User = Depends()):
    password = user.password.encode('utf-8')
    password = bcrypt.hashpw(password,bcrypt.gensalt()).decode('utf-8')

    check_email = user_collection.find_one(user.email)

    if check_email is not None:
        return JSONResponse({"error":"Email Already Registered"},status_code=400)
    
    user_collection.update_one(
        {"email":user.email},
        {"$set": {
            "first_name":user.first_name,
            "last_name":user.last_name,
            "email":user.email,
            "password":password
        }},
        upsert=True
    )
    access_token = create_access_token([user.first_name,user.last_name,user.email])

    return JSONResponse({"content":"Successfully Registered","access_token":access_token},status_code=200)

@router.post("/login")
async def login(login: Annotated[OAuth2PasswordRequestForm, Depends()]):
    confirmed_email = user_collection.find_one({"email": login.username})

    if not confirmed_email:
        return JSONResponse(
            content={"detail": "Invalid Email or Password"},
            status_code=400
        )

    if auth_password(login.password, confirmed_email["password"]):
        user_name = confirmed_email["first_name"]
        return {
            "access_token": create_access_token(user_name),
            "refresh_token": create_refresh_token(user_name)
        }

    return JSONResponse(
        content={"detail": "Invalid Email or Password"},
        status_code=400
    )
        
@router.post("/get_current_user")
async def get_current_user(token:str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return payload["sub"]
    
    except JWTError: 
        raise credentials_exception


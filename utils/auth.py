import datetime
from datetime import datetime,timezone,timedelta
from jose import jwt
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET_KEY  = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES =  24 * 60
REFRESH_TOKEN_EXPIRE_MINUTES = 24 * 60

def create_access_token(subject: dict, expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.now(timezone.utc) + expires_delta
    else:
        expires_delta = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = ({"exp": expires_delta,"sub":str(subject)})
    encode_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encode_jwt

def create_refresh_token(subject:dict, expires_delta:int = None)-> str:
    if expires_delta is not None:
        expires_delta = datetime.now(timezone.utc) + expires_delta
    else:
        expires_delta = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    
    to_encode = ({"exp": expires_delta,"sub":str(subject)})
    encode_jwt = jwt.encode(to_encode,JWT_REFRESH_SECRET_KEY,ALGORITHM)
    
    return encode_jwt

def auth_password(password,stored_password:str):
    unhashed_password = bcrypt.checkpw(password.encode('utf-8'),stored_password.encode('utf-8'))
    if unhashed_password:
        return True
    else:
        return "Invalid password"


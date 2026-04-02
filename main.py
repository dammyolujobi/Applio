from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import user,aggregator
import uvicorn

app = FastAPI()

app.include_router(user.router)
app.include_router(aggregator.router)

app.add_middleware( 
    CORSMiddleware,
    allow_origins="http://localhost:3000",
    allow_credentials=["*"],
    allow_headers=["*"],
    allow_methods=["*"]
)



if __name__ == "__main__":
    uvicorn.run(app = "main:app",host="0.0.0.0",port=8000,reload=True)
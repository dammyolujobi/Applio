from fastapi import FastAPI
from router import user,aggregator
import uvicorn

app = FastAPI()

app.include_router(user.router)
app.include_router(aggregator.router)



if __name__ == "__main__":
    uvicorn.run(app = "main:app",host="0.0.0.0",port=8000,reload=True)
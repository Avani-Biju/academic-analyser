from fastapi import FastAPI
from app.api.upload import router as upload_router
from app.api.match import router as match_router

app = FastAPI(title="Academic Analyzer API")

app.include_router(upload_router)
app.include_router(match_router)
@app.get("/")
def read_root():
    return {"status": "Academic Analyzer API Running"}
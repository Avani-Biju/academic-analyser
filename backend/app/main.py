from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.upload import router as upload_router
from app.api.match import router as match_router
from app.api.courses import router as courses_router
from app.config import load_environment
from app.database.database import engine, Base

load_environment()

# Initialize the database tables (No Alembic for now)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Academic Analyzer API")

# CORS middleware - allow Angular dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200", "http://localhost:4201"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, prefix="/api")
app.include_router(match_router, prefix="/api")
app.include_router(courses_router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "Academic Analyzer API Running"}

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from scraper import job_scraper
from gemini import resume_generator
from models import JobDetails 
from fastapi.middleware.cors import CORSMiddleware
import json

allowed_origins = ["https://genresume-ai.vercel.app","localhost"]
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # List of allowed origins
    allow_credentials=False,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "Welcome to the Job Scraper API!"}


@app.get("/jobs")
async def get_jobs(skill: str | None = Query(description="Skill to search for", default="React"),
                   location: str | None = Query(description="Location to search in", default="Chennai"),
                   experience: int | None = Query(description="Work Experience", default=1)):
    """
    API endpoint to scrape job listings.
    - skill: The skill or keyword to search for.
    - location: The location to search in.
    - experience: Years of work experience.
    """
    try:
        job_listings = await job_scraper(skill=skill, location=location, experience=experience)
        return {"total_jobs": len(job_listings["indeed"]) + len(job_listings["linkedin"]), 
                "indeed_jobs": job_listings["indeed"], 
                "linkedin_jobs": job_listings["linkedin"]}
    except Exception as e:
        return {"error": f"Error scraping job listings: {str(e)}"}


@app.post("/generate_resume")
async def generate_resume(job_details: JobDetails):
    """
    Endpoint to generate a resume based on the given input.
    """
    # print(job_details)
    try:
        prompt = json.dumps(job_details.dict(),separators=(',', ':'),indent=4)
        result = resume_generator(prompt)
        
        return {"generated_resume": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating resume: {str(e)}")

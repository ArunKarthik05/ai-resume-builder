from fastapi import FastAPI, Query
from scraper import job_scrapper  # Import the scraper function

app = FastAPI()

@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "Welcome to the Job Scraper API!"}


@app.get("/jobs")
def get_jobs(skill: str|None = Query(description="Skill to search for",default="React"),
             location: str|None = Query(description="Location to search in",default="Chennai"),
             pages: int|None = Query(description="Number of pages to scrape",default="1"),
             experience : int|None = Query(description="Work Experience",default="1")
             ):
    """
    API endpoint to scrape job listings.
    - skill: The skill or keyword to search for.
    - location: The location to search in.
    - pages: Number of pages to scrape (10 jobs per page).
    """
    try:
        job_listings = job_scrapper(skill=skill, location=location, pages=pages,experience=experience)
        return {"total_jobs": len(job_listings), "jobs": job_listings}
    except Exception as e:
        return {"error": str(e)}
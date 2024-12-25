from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from bs4 import BeautifulSoup
import random
import time
import urllib.parse


async def simulate_human_behavior(page, min_time=2, max_time=4):
    """Simulate human-like delays and scrolling."""
    time.sleep(random.uniform(min_time, max_time))
    for _ in range(random.randint(2, 6)):
        await page.mouse.wheel(0, random.randint(300, 500))
        time.sleep(random.uniform(min_time, max_time))


async def extract_jobs_from_indeed(page, target_url):
    """Extract job postings from Indeed."""
    print(f"Navigating to Indeed URL: {target_url}")
    await page.goto(target_url)
    await simulate_human_behavior(page)

    try:
        await page.wait_for_selector(".job_seen_beacon", timeout=10000)
    except Exception as e:
        print(f"Error waiting for Indeed jobs to load: {e}")
        return []

    # Parse page content
    page_content = await page.content()
    soup = BeautifulSoup(page_content, 'html.parser')
    job_cards = soup.select(".job_seen_beacon")
    print(f"Found {len(job_cards)} job cards on Indeed.")

    # Extract job details
    jobs = []
    for card in job_cards:
        title_tag = card.select_one("h2.jobTitle a")
        company_tag = card.select_one("[data-testid='company-name']")
        location_tag = card.select_one("[data-testid='text-location']")

        job_link = title_tag['href'] if title_tag else None
        title = title_tag.get_text(strip=True) if title_tag else None
        company = company_tag.get_text(strip=True) if company_tag else None
        location = location_tag.get_text(strip=True) if location_tag else None

        if title or company or location:
            jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "job_link": f"https://www.indeed.com{job_link}" if job_link else None
            })

    return jobs


async def extract_jobs_from_linkedin(page, context, target_url):
    """Extract job postings from LinkedIn."""
    print(f"Navigating to LinkedIn URL: {target_url}")
    await page.goto(target_url)
    await simulate_human_behavior(page)

    # Check if login is required
    sign_in_button = page.locator('a.nav__button-secondary:has-text("Sign in")')
    if await sign_in_button.is_visible():
        print("Login required. Proceeding to login...")
        await sign_in_button.click()
        await simulate_human_behavior(page)
        await page.fill('input[name="session_key"]', "20tucs033@skct.edu.in")
        await page.fill('input[name="session_password"]', "Dhamo@123")
        await page.locator('button.btn__primary--large:has-text("Sign in")').click()
        await simulate_human_behavior(page)

    # Open a new tab for LinkedIn search
    new_tab = await context.new_page()
    await new_tab.goto(target_url)
    await simulate_human_behavior(new_tab)

    # Parse page content
    page_content = await new_tab.content()
    soup = BeautifulSoup(page_content, 'html.parser')
    job_cards = soup.select("li.ember-view")
    print(f"Found {len(job_cards)} job cards on LinkedIn.")

    # Extract job details
    jobs = []
    for card in job_cards:
        title_tag = card.select_one(".job-card-container__link span[aria-hidden='true']")
        company_tag = card.select_one(".artdeco-entity-lockup__subtitle span")
        location_tag = card.select_one(".artdeco-entity-lockup__subtitle span")

        job_link = card.select_one(".job-card-container__link")['href'] if title_tag else None
        title = title_tag.get_text(strip=True) if title_tag else None
        company = company_tag.get_text(strip=True) if company_tag else None
        location = location_tag.get_text(strip=True) if location_tag else None

        if title or company or location:
            jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "job_link": f"https://www.linkedin.com{job_link}" if job_link else None
            })

    await new_tab.close()
    return jobs


async def job_scraper(skill: str, location: str, experience: int):
    target_indeed_url = f"https://www.indeed.com/jobs?q={urllib.parse.quote(skill)}&l={urllib.parse.quote(location)}"
    target_linkedin_url = f"https://www.linkedin.com/jobs/{urllib.parse.quote(skill)}-jobs-{urllib.parse.quote(location)}"

    print(f"Skill: {skill}, Location: {location}, Experience: {experience}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            viewport={"width": random.randint(1024, 1920), "height": random.randint(768, 1080)},
            user_agent=f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(90, 130)}.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await stealth_async(page)

        # Initialize job lists
        indeed_jobs, linkedin_jobs = [], []

        try:
            # Extract jobs from Indeed
            indeed_jobs = await extract_jobs_from_indeed(page, target_indeed_url)
        except Exception as e:
            print(f"Error scraping Indeed: {str(e)}")

        try:
            # Extract jobs from LinkedIn
            linkedin_jobs = await extract_jobs_from_linkedin(page, context, target_linkedin_url)
        except Exception as e:
            print(f"Error scraping LinkedIn: {str(e)}")

        # Close browser
        await browser.close()

        # Check if both failed
        if not indeed_jobs and not linkedin_jobs:
            raise Exception("Scraping failed for both sources.")

        return {"indeed": indeed_jobs, "linkedin": linkedin_jobs}

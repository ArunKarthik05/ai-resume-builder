import requests
from bs4 import BeautifulSoup

def job_scrapper(skill: str, location: str, pages: int, experience: int):
    """
    Scrapes TimesJobs for job listings based on skill, location, and experience.
    - skill: The skill or keyword to search for.
    - location: The location to search in.
    - pages: Number of pages to scrape.
    - experience: The experience filter (e.g., 0-3 years).
    """
    base_url = "https://www.timesjobs.com/candidate/job-search.html"
    jobs = []
    pageNo = 1

    for page in range(pages):
        params = {
            'searchType': 'personalizedSearch',
            'from': 'submit',
            'searchTextSrc': 'ft',
            'txtKeywords': skill,
            'txtLocation': location,
            'cboWorkExp1': experience,
            'postWeek' : 60,
            'sequence': pageNo,
            'startPage': 1
        }

        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            print(f"Failed to fetch page {page + 1}: {response.status_code}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all job cards on the page
        job_cards = soup.find_all('li', class_="clearfix job-bx wht-shd-bx")[:10]

        for job in job_cards:  # Process only the first 10 jobs on the page
            header = job.find('h2', class_='heading-trun')
            title = header.find("a").text.strip() if header else "N/A"
            link = header.find('a')['href'] if header else "N/A"
            company = job.find('h3', class_='joblist-comp-name').text.strip() if job.find('h3', class_='joblist-comp-name') else "N/A"
            summary = job.find('li', class_='job-description__').text.strip() if job.find('li', class_='job-description__') else "N/A"
            
            footer = job.find('ul', class_='top-jd-dtl mt-16 clearfix')
            location = footer.find('li', class_='srp-zindex location-tru').text.strip() if footer and footer.find('li', class_='srp-zindex location-tru') else "N/A"
            experience = footer.find_all('li')[1].text.strip() if footer and len(footer.find_all('li')) > 1 else "N/A"
            salary = footer.find_all('li')[2].text.strip() if footer and len(footer.find_all('li')) > 2 else "N/A"
            
            detailed_info = get_apply_link_details(link)
            jobs.append({
                "job_title": title,
                "company": company,
                "summary": summary,
                "location": location,
                "experience": experience,
                "salary": salary,
                "link": link if link else "N/A",
                "detailed_info" : detailed_info
            })
            pageNo += 1

    return jobs

import requests
from bs4 import BeautifulSoup

def get_apply_link_details(link: str):
    response = requests.get(link)
    
    if response.status_code != 200:
        print(f"Failed to fetch page: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract Job Description
    job_description = soup.find('div', class_='jd-desc job-description-main')
    if job_description:
        job_description_text = job_description.get_text(strip=True)
    else:
        job_description_text = "Job description not available"
    
    # Extract Key Details
    key_details = soup.find('div', class_='job-basic-info')
    key_details_dict = {}
    if key_details:
        key_detail_items = key_details.find_all('li', class_='clearfix')
        for item in key_detail_items:
            label = item.find('label')
            detail = item.find('span', class_='basic-info-dtl')
            if label and detail:
                key = label.get_text(strip=True)
                # Remove colon at the end of the key if present
                if key.endswith(":"):
                    key = key[:-1]
                key_details_dict[key] = detail.get_text(strip=True)
    
    # Extract Key Skills
    skills = soup.find('div', class_='jd-sec job-skills clearfix')
    skills_list = []
    if skills:
        skill_tags = skills.find_all('span', class_='jd-skill-tag')
        for skill in skill_tags:
            skills_list.append(skill.get_text(strip=True))
    
    # Extract Job Posted By
    job_posted_by = soup.find('div', class_='jd-hiring-comp')
    company_name = ""
    if job_posted_by:
        company_name_tag = job_posted_by.find('span', class_='basic-info-dtl')
        if company_name_tag:
            company_name = company_name_tag.get_text(strip=True)
    
    return {
    'job_description': job_description_text,
    'key_details': key_details_dict,
    'skills': skills_list,
    'job_posted_by': company_name
    }




from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import json
import yaml
from argparse import ArgumentParser
import selenium
from selenium.common.exceptions import NoSuchElementException, NoSuchDriverException

DEFAULT_URL = ('https://www.glassdoor.com/fake-url')

parser = ArgumentParser()
parser.add_argument('-u', '--url',
                    help='URL of the company\'s Glassdoor interview page.',
                    default=DEFAULT_URL)
parser.add_argument('--headless',
                    help='Run in headless mode',
                    default=False,
                    action='store_true')
args = parser.parse_args()

interviews_url = args.url

service = None

def get_driver(url=None):
    # Set up Selenium options
    options = Options()
    options.add_argument("--start-maximized")
    if args.headless:
        options.add_argument("--headless")  # Uncomment for headless mode
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    
    global service
    try:
        driver = webdriver.Chrome(options=options, service=service)
    except NoSuchDriverException:
        from install_chromedriver import get_service
        service = get_service()
        driver = webdriver.Chrome(options=options, service=service)
    wait = WebDriverWait(driver, 15)

    if url:
        driver.get(url)

    return driver, wait

def get_interviews_from_page(driver, wait):
    # Wait for the container to be present
    container = wait.until(
        EC.presence_of_element_located((By.XPATH, '//div[@data-test="InterviewList"]'))
    )
    # Find all divs with data-brandviews starting with "MODULE:n=interview-reviews"
    try:
        interview_divs = container.find_elements(
            By.XPATH,
            './/div[starts-with(@data-brandviews, "MODULE:n=interview-reviews")]'
            )[::2] # the divs are duplicated, so we need to skip every other one
    except (selenium.common.exceptions.TimeoutException, selenium.common.exceptions.NoSuchElementException):
        print("No interview review divs found")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

    print(f"Found {len(interview_divs)} interview review divs")
    interview_data = []
    for div in interview_divs:
        optional_divs = div.find_elements(By.XPATH, './/div[contains(@class, "text-with-icon")]')
        location = None
        for optional_div in optional_divs:
            if optional_div.find_elements(By.CSS_SELECTOR, 'svg[class="icon_Icon__ptI3R"]'):
                if not location:
                    # print('location', div.text.strip())
                    location = optional_div.text.strip()
        interview_position = div.find_elements(By.TAG_NAME, "h3")[0].text
        span_elements = div.find_elements(By.TAG_NAME, "span")
        published_date = span_elements[0].text
        candidate = span_elements[1].text
        is_offer_received = span_elements[2].text
        interview_experience = span_elements[3].text
        interview_difficulty = span_elements[4].text

        p_elements = div.find_elements(By.TAG_NAME, "p")
        application_process = p_elements[1].text
        interview_review = p_elements[3].text
        question_elements = div.find_elements(By.CSS_SELECTOR, 'div.interview-details_interviewText__YH2ZO > p')
        interview_questions = [question_element.get_attribute('textContent') for question_element in question_elements]
        print(published_date)
        print(interview_questions)
        
        try:
            helpful_count = div.find_element(By.CSS_SELECTOR, 'div[data-test="review-helpful-count"]').text
        except NoSuchElementException:
            helpful_count = 0
       

        interview_data.append({
            "interview_position": interview_position,
            "location": location,
            "published_date": published_date,
            "candidate": candidate,
            "is_offer_received": is_offer_received,
            "interview_experience": interview_experience,
            "interview_difficulty": interview_difficulty,
            "application_process": application_process,
            "interview_review": interview_review,
            "interview_questions": interview_questions,
            "helpful_count": helpful_count
        })
        # print(interview_data[-1])
    return interview_data

def get_all_interviews():
    all_interviews = []
    url_base = interviews_url[:-4]
    page = 1
    while True:
        full_url = url_base + f'_P{page}.htm'
        print(f"Getting interviews from {full_url}")
        driver, wait = get_driver(full_url)
        interviews_data = get_interviews_from_page(driver, wait)
        if len(interviews_data) == 0:
            break
        all_interviews.extend(interviews_data)
        page += 1
        driver.quit()

    return all_interviews

def save_interviews(interviews):
    df = pd.DataFrame(interviews)
    df.to_csv('interviews.csv', index=False)


if __name__ == "__main__":
    interviews = get_all_interviews()
    save_interviews(interviews)
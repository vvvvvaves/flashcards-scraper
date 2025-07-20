import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

def get_driver(url):
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)
    wait = WebDriverWait(driver, 30)

    driver.get(url)
    return driver, wait

def get_reviews_from_page(driver, wait):
    reviews_list = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="ReviewsFeed"]')))
    reviews = reviews_list.find_elements(By.XPATH, './/li')
    print(len(reviews))
    return reviews



def get_all_reviews(url):
    all_reviews = []
    url_base = url[:-4]
    page = 1
    while True:
        full_url = url_base + f'_P{page}.htm'
        print(f"Getting reviews from {full_url}")
        driver, wait = get_driver(full_url)
        reviews_data = get_reviews_from_page(driver, wait)
        driver.quit()
        if len(reviews_data) == 0:
            break
        all_reviews.extend(reviews_data)
        page += 1
    return all_reviews

if __name__ == "__main__":
    url = 'https://www.glassdoor.com/Reviews/ActiveFence-Reviews-E4077549.htm'
    all_reviews = get_all_reviews(url)
    print(len(all_reviews))


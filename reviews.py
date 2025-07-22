from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time
from argparse import ArgumentParser
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd
from bs4 import BeautifulSoup
import datetime
import logging
from logging.handlers import RotatingFileHandler

DEFAULT_URL = ('https://www.glassdoor.com/fake-url')
DEFAULT_FILEPATH = 'reviews.csv'

parser = ArgumentParser()
parser.add_argument('-u', '--url',
                    help='URL of the company\'s Glassdoor reviews page.',
                    default=DEFAULT_URL)
parser.add_argument('-f', '--filepath',
                    help='Path to save the reviews.',
                    default=DEFAULT_FILEPATH)
parser.add_argument('--hide-window',
                    help='Hide the browser window by positioning it out of screen.',
                    action='store_true',
                    default=False)
parser.add_argument('--proxy',
                    help='Proxy server address (e.g., http://user:pass@host:port)',
                    default=None)
args = parser.parse_args()

reviews_url = args.url
hide_window = args.hide_window
x_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"><path fill="currentColor" fill-rule="evenodd" d="M18.299 5.327a1.5 1.5 0 0 1 0 2.121l-4.052 4.051 4.052 4.053a1.5 1.5 0 0 1-2.121 2.121l-4.053-4.052-4.051 4.052a1.5 1.5 0 0 1-2.122-2.121l4.052-4.053-4.052-4.051a1.5 1.5 0 1 1 2.122-2.121l4.05 4.051 4.054-4.051a1.5 1.5 0 0 1 2.12 0"></path></svg>'
line_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"><rect width="17.461" height="3" x="3.395" y="10" fill="currentColor" fill-rule="evenodd" rx="1.5"></rect></svg>'
check_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"><path fill="currentColor" fill-rule="evenodd" d="m8.835 17.64-3.959-3.545a1.19 1.19 0 0 1 0-1.735 1.326 1.326 0 0 1 1.816 0l3.058 2.677 7.558-8.678a1.326 1.326 0 0 1 1.816 0 1.19 1.19 0 0 1 0 1.736l-8.474 9.546a1.326 1.326 0 0 1-1.815 0"></path></svg>'
circle_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"><circle cx="12" cy="12" r="7.5" fill="none" stroke="currentColor" stroke-width="3"></circle></svg>'
predefined_svg_elements = {
    "X": x_svg,
    "Line": line_svg,
    "Check": check_svg,
    "Circle": circle_svg
}

def svg_matches(element, svg_str):
    try:
        outer_html = element.get_attribute('outerHTML')
        return ''.join(outer_html.split()) == ''.join(svg_str.split())
    except Exception:
        return False

def visualize_cursor(driver):
    enable_cursor = """
        function enableCursor() {
            var seleniumFollowerImg = document.createElement("img");
            seleniumFollowerImg.setAttribute('src', 'data:image/png;base64,'
            + 'iVBORw0KGgoAAAANSUhEUgAAABQAAAAeCAQAAACGG/bgAAAAAmJLR0QA/4ePzL8AAAAJcEhZcwAA'
            + 'HsYAAB7GAZEt8iwAAAAHdElNRQfgAwgMIwdxU/i7AAABZklEQVQ4y43TsU4UURSH8W+XmYwkS2I0'
            + '9CRKpKGhsvIJjG9giQmliHFZlkUIGnEF7KTiCagpsYHWhoTQaiUUxLixYZb5KAAZZhbunu7O/PKf'
            + 'e+fcA+/pqwb4DuximEqXhT4iI8dMpBWEsWsuGYdpZFttiLSSgTvhZ1W/SvfO1CvYdV1kPghV68a3'
            + '0zzUWZH5pBqEui7dnqlFmLoq0gxC1XfGZdoLal2kea8ahLoqKXNAJQBT2yJzwUTVt0bS6ANqy1ga'
            + 'VCEq/oVTtjji4hQVhhnlYBH4WIJV9vlkXLm+10R8oJb79Jl1j9UdazJRGpkrmNkSF9SOz2T71s7M'
            + 'SIfD2lmmfjGSRz3hK8l4w1P+bah/HJLN0sys2JSMZQB+jKo6KSc8vLlLn5ikzF4268Wg2+pPOWW6'
            + 'ONcpr3PrXy9VfS473M/D7H+TLmrqsXtOGctvxvMv2oVNP+Av0uHbzbxyJaywyUjx8TlnPY2YxqkD'
            + 'dAAAAABJRU5ErkJggg==');
            seleniumFollowerImg.setAttribute('id', 'selenium_mouse_follower');
            seleniumFollowerImg.setAttribute('style', 'position: absolute; z-index: 99999999999; pointer-events: none; left:0; top:0');
            document.body.appendChild(seleniumFollowerImg);
            document.onmousemove = function (e) {
            document.getElementById("selenium_mouse_follower").style.left = e.pageX + 'px';
            document.getElementById("selenium_mouse_follower").style.top = e.pageY + 'px';
            };
        };

        enableCursor();
    """

    driver.execute_script(enable_cursor)


def get_driver(url, proxy=None):
    import undetected_chromedriver as uc
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')
    driver = uc.Chrome(options=options)
    if hide_window:
        driver.set_window_position(-10000,0)

    wait = WebDriverWait(driver, 15)

    driver.get(url)
    # visualize_cursor(driver)
    return driver, wait

def random_xy_click(driver):
    import random
    x = random.randint(0, 500)
    y = random.randint(0, 500)
    driver.execute_script(f"document.elementFromPoint({x}, {y}).click();")
    return driver

def random_move(driver):
    import random
    x = random.randint(0, 500)
    y = random.randint(0, 500)
    actions = ActionChains(driver)
    actions.move_by_offset(x, y).perform()
    return driver

def random_sleep(driver):
    import random
    time.sleep(random.random() * 3)
    return driver

def simulate_human_interaction(driver):
    import random
    actions = [random_xy_click, random_move, random_sleep]
    random.shuffle(actions)
    for func in actions:
        func(driver)
    return driver

def get_driver_with_retry(url):
    for i in range(3):
        try:
            driver, wait = get_driver(url)
            simulate_human_interaction(driver)
            wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="ReviewsFeed"]')))
            return driver, wait
        except TimeoutException as e:
            logger.error(f"Error getting driver: {e}, retrying for the {i+1} time...")
            driver.quit()
            time.sleep(1)
    raise TimeoutException("Failed to get driver")

def get_reviews_from_page(driver, wait):
    # Wait for ReviewsFeed as before
    reviews_list = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="ReviewsFeed"]')))
    html = reviews_list.get_attribute('outerHTML')
    soup = BeautifulSoup(html, 'html.parser')
    reviews_data = []
    review_elements = driver.find_elements(By.XPATH, '//div[@id="ReviewsFeed"]//li')

    def get_review_title(review_static):
        return review_static.find('h3').get_text(strip=True) if review_static.find('h3') else None
    
    def get_employee_status_and_location(review_static):
        divs = review_static.find_all('div', class_="text-with-icon_TextWithIcon__5ZZqT")
        employee_status = None
        location = None
        for div in divs:
            if div.find('svg', class_='icon_Icon__ptI3R'):
                if not location:
                    location = div.get_text(strip=True)
            else:
                if not employee_status:
                    employee_status = div.get_text(strip=True)
        return employee_status, location
    
    def get_pros_cons(review_static):
        p_elements = review_static.find_all('p')
        pros = p_elements[1].get_text(strip=True) if len(p_elements) > 1 else None
        cons = p_elements[3].get_text(strip=True) if len(p_elements) > 3 else None
        return pros, cons
    
    def get_spans_data(review_static):
        spans = review_static.find_all('span')
        rating = spans[0].get_text(strip=True) if len(spans) > 0 else None
        date = spans[1].get_text(strip=True) if len(spans) > 1 else None
        position = spans[3].get_text(strip=True) if len(spans) > 3 else None
        return rating, date, position
    
    def get_helpful_count(review_static):
        helpful_div = review_static.find('div', attrs={'data-test': 'review-helpful-count'})
        return helpful_div.get_text(strip=True) if helpful_div else 0
    
    def get_subratings(review_dynamic, driver):
            # Subratings popup (Selenium only)
        subrating_map = {
            "life_balance": None,
            "culture_values": None,
            "diversity_inclusion": None,
            "career_opportunities": None,
            "comp_benefits": None,
            "senior_management": None,
        }
        try:
            subratings_container = review_dynamic.find_element(By.XPATH, ".//div[contains(@class, 'review-rating_ratingContainer__sQ_4_')]")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", subratings_container)
            time.sleep(0.5)
            actions = ActionChains(driver)
            actions.move_to_element(subratings_container).perform()
            time.sleep(0.5)
            driver.execute_script("var ev = new MouseEvent('mouseover', {bubbles: true}); arguments[0].dispatchEvent(ev);", subratings_container)
            try:
                popup = subratings_container.find_element(By.TAG_NAME, "aside")
                subratings = popup.find_elements(By.CSS_SELECTOR, "div[class='review-rating_subRating__0Q_Z0']")
            except NoSuchElementException:
                subratings = []
            for subrating_key, subrating_div in zip(subrating_map.keys(), subratings):
                count = 5 - subrating_div.get_attribute('innerHTML').count('RatingStarOutline')
                subrating_map[subrating_key] = count
        except Exception:
            pass
        return subrating_map
    
    def get_svg_map(review_dynamic):
        svgs = review_dynamic.find_elements(By.CSS_SELECTOR, '.review-details_experienceContainer__2W06X svg')
        svg_map = {
            "recommend": svgs[0],
            "ceo_approval": svgs[1],
            "business_outlook": svgs[2]
        }
        return svg_map
    
    def get_recommend(svg_map):
        for rating_value, svg_value in predefined_svg_elements.items():
            if svg_matches(svg_map["recommend"], svg_value):
                return rating_value
        return None
    
    def get_ceo_approval(svg_map):
        for rating_value, svg_value in predefined_svg_elements.items():
            if svg_matches(svg_map["ceo_approval"], svg_value):
                return rating_value
        return None
    
    def get_business_outlook(svg_map):
        for rating_value, svg_value in predefined_svg_elements.items():
            if svg_matches(svg_map["business_outlook"], svg_value):
                return rating_value
        return None
    
    
    for idx, (review_static, review_dynamic) in enumerate(zip(soup.find_all('li'), review_elements)):
        # Parse static fields with BeautifulSoup
        review_title = get_review_title(review_static)
        employee_status, location = get_employee_status_and_location(review_static)
        pros, cons = get_pros_cons(review_static)
        rating, date, position = get_spans_data(review_static)
        helpful_count = get_helpful_count(review_static)
        subrating_map = get_subratings(review_dynamic, driver)
        
        # Get SVGs
        svg_map = get_svg_map(review_dynamic)
        svg_map["recommend"] = get_recommend(svg_map)
        svg_map["ceo_approval"] = get_ceo_approval(svg_map)
        svg_map["business_outlook"] = get_business_outlook(svg_map)


        reviews_data.append({
            "review_title": review_title,
            "employee_status": employee_status,
            "location": location,
            "pros": pros,
            "cons": cons,
            "rating": rating,
            "date": date,
            "position": position,
            "recommend": svg_map["recommend"],
            "ceo_approval": svg_map["ceo_approval"],
            "business_outlook": svg_map["business_outlook"],
            "life_balance": subrating_map["life_balance"],
            "culture_values": subrating_map["culture_values"],
            "diversity_inclusion": subrating_map["diversity_inclusion"],
            "career_opportunities": subrating_map["career_opportunities"],
            "comp_benefits": subrating_map["comp_benefits"],
            "senior_management": subrating_map["senior_management"],
            "helpful_count": helpful_count,
        })
        # logger.info(reviews_data[-1])
    return reviews_data

def get_all_reviews(url):
    all_reviews = []
    url_base = url[:-4]
    page = 1
    while True:
        full_url = url_base + f'_P{page}.htm'
        logger.info(f"Getting reviews from {full_url}")
        try:
            driver, wait = get_driver_with_retry(full_url)
        except TimeoutException as e:
            logger.error(f"Could not get driver for {full_url}, skipping...")
            page += 1
            continue
        reviews_data = get_reviews_from_page(driver, wait)
        driver.quit()
        if len(reviews_data) == 0:
            break
        all_reviews.extend(reviews_data)
        page += 1
    return all_reviews

def save_reviews(reviews, filepath):
    dataFrame = pd.DataFrame(reviews)
    dataFrame.to_csv(filepath, index=False)
    logger.info(f'Saved to {filepath}')

if __name__ == "__main__":
    start_timestamp = datetime.datetime.now()
    # Set up logging to both console and file
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(log_formatter)
    logger.addHandler(ch)

    # File handler with rotation
    fh = RotatingFileHandler('reviews.log', maxBytes=1_000_000, backupCount=5)
    fh.setLevel(logging.INFO)
    fh.setFormatter(log_formatter)
    logger.addHandler(fh)

    logger.info(f'Args: {args}')
    logger.info(f'Started at {start_timestamp.strftime("%Y/%m/%d %H:%M:%S")}')

    all_reviews = get_all_reviews(args.url)
    save_reviews(all_reviews, args.filepath)
    end_timestamp = datetime.datetime.now()
    logger.info(f'Finished at {end_timestamp.strftime("%Y/%m/%d %H:%M:%S")}')
    logger.info(f'Total time: {(end_timestamp - start_timestamp).total_seconds()} seconds')

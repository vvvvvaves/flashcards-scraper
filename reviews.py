import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from argparse import ArgumentParser
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd

DEFAULT_URL = ('https://www.glassdoor.com/fake-url')

parser = ArgumentParser()
parser.add_argument('-u', '--url',
                    help='URL of the company\'s Glassdoor reviews page.',
                    default=DEFAULT_URL)
parser.add_argument('--hide-window',
                    help='Hide the browser window by positioning it out of screen.',
                    action='store_true',
                    default=False)
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

def inject_custom_cursor_and_hover(driver):
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

def get_driver(url):
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)
    if hide_window:
        driver.set_window_position(-10000,0)

    wait = WebDriverWait(driver, 15)

    driver.get(url)
    inject_custom_cursor_and_hover(driver)
    return driver, wait

def get_driver_with_retry(url):
    for i in range(3):
        try:
            driver, wait = get_driver(url)
            wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="ReviewsFeed"]')))
            return driver, wait
        except TimeoutException as e:
            print(f"Error getting driver: {e}, retrying for the {i+1} time...")
            time.sleep(1)
    raise TimeoutException("Failed to get driver")

def get_reviews_from_page(driver, wait):
    # TODO: Handle timeout exception for when the bot does not pass the captcha
    reviews_list = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="ReviewsFeed"]')))
    reviews = reviews_list.find_elements(By.XPATH, './/li')
    reviews_data = []
    for review in reviews:
        review_title = review.find_elements(By.XPATH, './/h3')[0].text
        divs = review.find_elements(By.XPATH, './/div[contains(@class, "text-with-icon")]')
        employee_status = None
        location = None
        for div in divs:
            if div.find_elements(By.CSS_SELECTOR, 'svg[class="icon_Icon__ptI3R"]'):
                if not location:
                    location = div.text.strip()
            else:
                if not employee_status:
                    employee_status = div.text.strip()

        p_elements = review.find_elements(By.XPATH, './/p')
        pros = p_elements[1].text
        cons = p_elements[3].text
        spans = review.find_elements(By.XPATH, './/span')
        rating = spans[0].text
        date = spans[1].text
        position = spans[3].text
        review_details = review.find_element(By.XPATH, './/div[@class="review-details_experienceContainer__2W06X"]')
        svgs = review_details.find_elements(By.CSS_SELECTOR, 'svg')


        svg_map = {
            "recommend": svgs[0],
            "ceo_approval": svgs[1],
            "business_outlook": svgs[2]
        }
        for rating_type, actual_svg in svg_map.items():
            for rating_value, svg_value in predefined_svg_elements.items():
                if svg_matches(actual_svg, svg_value):
                    svg_map[rating_type] = rating_value
                    break
        
        for key, value in svg_map.items():
            if value not in predefined_svg_elements.keys():
                svg_map[key] = None

        # Re-inject custom cursor in case of navigation or reload
        inject_custom_cursor_and_hover(driver)
        subratings_container = review.find_element(By.XPATH, ".//div[contains(@class, 'review-rating_ratingContainer__sQ_4_')]")
        # Scroll the element into view before hovering
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", subratings_container)
        time.sleep(0.5)
        # Hover over the caret div using ActionChains
        actions = ActionChains(driver)
        actions.move_to_element(subratings_container).perform()
        time.sleep(0.5)  # Give time for hover effect
        # Fallback: trigger mouseover event via JavaScript
        driver.execute_script("var ev = new MouseEvent('mouseover', {bubbles: true}); arguments[0].dispatchEvent(ev);", subratings_container)
        try:
            popup = subratings_container.find_element(By.TAG_NAME, "aside")
            subratings = popup.find_elements(By.CSS_SELECTOR, "div[class='review-rating_subRating__0Q_Z0']")
        except NoSuchElementException:
            subratings = []
        subrating_map = {
            "life_balance": None,
            "culture_values": None,
            "diversity_inclusion": None,
            "career_opportunities": None,
            "comp_benefits": None,
            "senior_management": None,
        }
        for subrating_key, subrating_div in zip(subrating_map.keys(), subratings):
            count = 5 - subrating_div.get_attribute('innerHTML').count('RatingStarOutline')
            subrating_map[subrating_key] = count

        try:
            helpful_count = review.find_element(By.CSS_SELECTOR, 'div[data-test="review-helpful-count"]').text
        except NoSuchElementException:
            helpful_count = 0

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
        print(reviews_data[-1])
    return reviews_data

def get_all_reviews(url):
    all_reviews = []
    url_base = url[:-4]
    page = 1
    while True:
        full_url = url_base + f'_P{page}.htm'
        print(f"Getting reviews from {full_url}")
        try:
            driver, wait = get_driver_with_retry(full_url)
        except TimeoutException as e:
            print(f"Could not get driver for {full_url}, skipping...")
            page += 1
            continue
        reviews_data = get_reviews_from_page(driver, wait)
        driver.quit()

        if len(reviews_data) == 0:
            break
        all_reviews.extend(reviews_data)
        page += 1
    return all_reviews

def save_reviews(reviews):
    dataFrame = pd.DataFrame(reviews)
    dataFrame.to_csv('reviews.csv', index=False)

if __name__ == "__main__":
    url = 'https://www.glassdoor.com/Reviews/ActiveFence-Reviews-E4077549.htm'
    all_reviews = get_all_reviews(url)
    save_reviews(all_reviews)
    print(len(all_reviews))


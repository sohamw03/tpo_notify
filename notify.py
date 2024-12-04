from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
import os
load_dotenv()

def setup_driver():
    # Initialize Chrome driver
    options = webdriver.ChromeOptions()
    # Add any additional options if needed
    # options.add_argument('--headless')  # Uncomment to run in headless mode
    driver = webdriver.Chrome(options=options)
    return driver

def login(driver, url, username, password):
    try:
        driver.get(url)

        # Wait for login form elements to be present (adjust selectors as needed)
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "input-15"))  # Replace with actual ID
        )
        password_field = driver.find_element(By.ID, "input-18")  # Replace with actual ID

        # Enter credentials
        username_field.send_keys(username)
        password_field.send_keys(password)

        # Click login button
        login_button = driver.find_element(By.CSS_SELECTOR, "form.v-form>button.logi")  # Replace with actual selector
        login_button.click()

        return True
    except TimeoutException:
        print("Timeout while trying to log in")
        return False

def navigate_and_extract(driver):
    try:
        # Wait for and click the desired tab
        tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/apply_company']>div.v-list-item"))  # Replace with actual selector
        )
        tab.click()

        card_data = []
        # Check if there are no companies
        temp_data = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".v-alert__content")))
        if "No Schedule Company Found." in temp_data.text:
            card_data.append(temp_data.text)

        else:
            card_data.append("Companies found")
            # Wait for cards to load
            # cards = WebDriverWait(driver, 10).until(
            #     EC.presence_of_all_elements_located((By.CLASS_NAME, "card-class"))  # Replace with actual card class
            # )

            # Extract information from cards
            # for card in cards:
            #     data = {
            #         'title': card.find_element(By.CLASS_NAME, "title").text,  # Replace with actual selectors
            #         'description': card.find_element(By.CLASS_NAME, "description").text,
            #         # Add more fields as needed
            #     }
            #     card_data.append(data)

        return card_data
    except TimeoutException:
        print("Timeout while trying to extract card information")
        return []

def main():
    driver = setup_driver()
    try:
        website_url = os.getenv("URL", "")
        username = os.getenv("U", "")
        password = os.getenv("P", "")

        if login(driver, website_url, username, password):
            card_data = navigate_and_extract(driver)
            print("Extracted data:", card_data)
        else:
            print("Login failed")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
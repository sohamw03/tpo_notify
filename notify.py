from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
import os, json
from pymongo import MongoClient
import resend
load_dotenv()

def setup_driver():
    # Initialize Chrome driver
    options = webdriver.ChromeOptions()
    # Add any additional options if needed
    options.add_argument('--headless')  # Uncomment to run in headless mode
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)
    return driver

def setup_db():
    client = MongoClient(os.getenv("MONGO_URI", ""))
    db = client["tpo-notify-database"]
    return db.companies

def clear_collection(collection):
    collection.delete_many({})

def get_existing_data(collection):
    return list(collection.find({}, {'_id': 0}))

def update_collection(collection, new_data):
    clear_collection(collection)
    if new_data and not isinstance(new_data[0], str) and not len(new_data) == 1:
        collection.insert_many(new_data)

def send_email(card_data):
    from datetime import datetime
    resend.api_key = os.getenv('RESEND_API_KEY', '')

    # Add timestamp with only hour and minute
    timestamp = datetime.now().strftime("%H:%M")

    if len(card_data) == 1 and isinstance(card_data[0], str):
        subject = f"TPO Update: No Companies Available [{timestamp}]"
        html_content = """
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #e74c3c;">TPO Status Update</h2>
            <p style="color: #7f8c8d; font-size: 16px;">All company listings have been cleared.</p>
        </div>
        """
    else:
        subject = f"TPO Update: New Companies Available [{timestamp}]"
        companies_html = ""
        for company in card_data:
            companies_html += f"""
            <div style="background: #f9f9f9; padding: 15px; margin-bottom: 15px; border-radius: 5px; border-left: 4px solid #2ecc71;">
                <h3 style="color: #2ecc71; margin: 0 0 10px 0;">{company['title']}</h3>
                <p style="color: #34495e; margin: 5px 0;">{company['description']}</p>
                <div style="display: flex; color: #7f8c8d; font-size: 14px; margin-top: 10px;">
                    <span style="margin-right: 15px;">📋 {company['type']}</span>
                    <span>🗓️ {company['date']}</span>
                </div>
            </div>
            """

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2ecc71;">New Companies Posted</h2>
            <p style="color: #7f8c8d; margin-bottom: 20px;">The following companies have been posted:</p>
            {companies_html}
            <p style="color: #95a5a6; font-size: 12px; margin-top: 20px;">
                This is an automated notification from TPO Portal
            </p>
        </div>
        """

    params = {
        "from": "TPO Notifications <notifications@resend.dev>",
        "to": os.getenv("EMAIL", ""),
        "subject": subject,
        "html": html_content
    }

    try:
        resend.Emails.send(params)
        print("Email notification sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

def check_and_notify(collection, card_data):
    existing_data = get_existing_data(collection)

    # Case 1: No companies found (clear message)
    if len(card_data) == 1 and isinstance(card_data[0], str):
        if existing_data:  # Only notify if there were companies before
            clear_collection(collection)
            send_email(card_data)
        return

    # Case 2: New or updated companies
    if existing_data != card_data:
        update_collection(collection, card_data)
        send_email(card_data)

def login(driver, url, username, password):
    try:
        driver.get(url)

        # Wait for login form elements to be present (adjust selectors as needed)
        username_field = WebDriverWait(driver, 5).until(
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

def logout(driver):
    try:
        profile_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#app > div > header > div.v-toolbar__content > div.text-center > button"))
        )
        profile_button.click()

        logout_button = driver.find_element(By.CSS_SELECTOR, "#app > div.v-menu__content.theme--light.v-menu__content--fixed.menuable__content__active > div > div.v-card__actions > button[title='logout']")
        logout_button.click()

        # Stall for a few seconds to keep browser open
        driver.implicitly_wait(5)
    except TimeoutException:
        print("Timeout while trying to log out")

def navigate_and_extract(driver):
    try:
        # Wait for and click the desired tab
        tab = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/apply_company']>div.v-list-item"))  # Replace with actual selector
        )
        tab.click()

        card_data = []
        try:
            # Check if there are no companies
            temp_data = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".v-alert__content")))
            if temp_data.is_displayed() and "No Schedule Company Found." in temp_data.text:
                card_data.append(temp_data.text)
        except Exception as e:
            print("No alert found")

        # Wait for cards to load
        cards = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#app > div > main > div > div > div > div:nth-child(2) > div:nth-child(1) > *"))
        )

        # Extract information from cards
        for card in cards:
            data = {
                'title': card.find_element(By.CLASS_NAME, "v-card__title").text,
                'description': card.find_element(By.CLASS_NAME, "v-card__subtitle").text,
                'type': card.find_element(By.CSS_SELECTOR, "v-card-body > div > div:nth-child(1)").text,
                'date': card.find_element(By.CSS_SELECTOR, "v-card-body > div > div:nth-child(2)").text
            }
            card_data.append(data)

        return card_data

    except Exception as e:
        print("Error while trying to extract card information:")
        return []

def main():
    driver = setup_driver()
    try:
        website_url = os.getenv("URL", "")
        username = os.getenv("U", "")
        password = os.getenv("P", "")

        if login(driver, website_url, username, password):
            collection = setup_db()
            card_data = navigate_and_extract(driver)
            check_and_notify(collection, card_data)
            print("Extracted data:\n", json.dumps(card_data, indent=2))
            logout(driver)
        else:
            print("Login failed")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
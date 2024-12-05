from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    return webdriver.Chrome(options=options)

def interact_with_website(driver):
    try:
        # Navigate to the website
        driver.get("https://sanjeevani-blush.vercel.app/")

        # Find and fill the input
        input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body > main > div.chatbot_chatbot_frame__xYBIk > div > div.chatbot_input_section__bXGgn > form > input[type=text]"))
        )
        input_field.send_keys("Hi there!")

        # Click the send button
        send_button = driver.find_element(By.CSS_SELECTOR, "body > main > div.chatbot_chatbot_frame__xYBIk > div > div.chatbot_input_section__bXGgn > form > button")
        send_button.click()
        print("Sent 'Hi there!'")

        # Wait for 30 seconds
        time.sleep(30)

        # Click the image
        img_element = driver.find_element(By.CSS_SELECTOR, "body > main > div.aside_aside__kI2H1 > div.aside_aside_lower__9LX65 > section > div.embla__viewport > div > div:nth-child(2) > div > img")
        img_element.click()
        print("Clicked the image")

        # Wait for 30 seconds
        time.sleep(30)

        driver.refresh()
        print("--------------------")

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    driver = setup_driver()
    try:
        while True:
            interact_with_website(driver)
    except KeyboardInterrupt:
        print("\nScript terminated by user")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
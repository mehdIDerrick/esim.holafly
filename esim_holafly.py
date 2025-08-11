from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import csv
import os

# Chrome options for CI (headless + no-sandbox)
options = Options()
# Use new headless mode where available
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

# If you want to force using system chromium (installed via apt):
chrome_bin = os.environ.get("CHROME_BIN")
if chrome_bin:
    options.binary_location = chrome_bin

# Use webdriver-manager to automatically download matching chromedriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://esim.holafly.com/")

# Allow some time for the page to load
time.sleep(3)

try:
    # Locate the "View all destinations" button using class name
    button = driver.find_element(By.CLASS_NAME, "hf-green-rounded-cta")

    # Scroll to the button and click it
    actions = ActionChains(driver)
    actions.move_to_element(button).click().perform()
    print("Button clicked successfully!")

    # Wait a moment for the new content to load
    time.sleep(8)

    # Scroll down to the end of the page until it stops loading new content
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(10)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("Reached the end of the page.")
            break
        last_height = new_height
        time.sleep(2)

    # Locate product elements by CSS selector after loading all content
    products = driver.find_elements(By.CSS_SELECTOR, "li.product")

    # Prepare data to be written into CSV
    product_data = []

    for product in products:
        try:
            name = product.find_element(By.CLASS_NAME, "woocommerce-loop-product__title").text
        except Exception:
            name = ""
        try:
            price = product.find_element(By.CLASS_NAME, "price").text
        except Exception:
            price = ""

        product_data.append([name, price])

    # Write data to CSV with ";" as the delimiter
    with open("product_data.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(["Name", "Price"])
        writer.writerows(product_data)

    print("Data saved to product_data.csv successfully!")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

def web_driver():
    """Set up and return the WebDriver instance."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1200")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def scrape_product_details(driver, url):
    """Scrape product details from the given URL."""
    product_name = "N/A"
    price = "N/A"
    try:
        print(f"Navigating to the URL: {url}")
        driver.get(url)
        time.sleep(10)  # Wait for page to load

        product_name = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//h1[@class='font-semibold text-lg']"))
        ).text.strip()

        price = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='content-width mx-auto px-3']"))
        ).text.strip()

    except Exception as e:
        print(f"Error scraping {url}: {e}")
    return product_name, price

# Load URLs from file
url_file = "url.txt"
if not os.path.exists(url_file):
    raise FileNotFoundError(f"{url_file} not found!")

with open(url_file, "r") as file:
    urls = [line.strip() for line in file if line.strip()]

if not urls:
    raise ValueError("No URLs found in the file!")

# Initialize WebDriver
driver = web_driver()

# Scrape product details for all URLs
product_details = []
for url in urls:
    product_name, price = scrape_product_details(driver, url)
    product_details.append((product_name, price, url))

# Close the WebDriver
driver.quit()

# Prepare the email content
sender_email = os.getenv("SENDER_EMAIL")
sender_password = os.getenv("SENDER_PASSWORD")
receiver_email = os.getenv("RECEIVER_EMAIL")

if not sender_email or not sender_password or not receiver_email:
    raise ValueError("Email credentials not found in environment variables.")

subject = "Amazon Product Details"
body = "Here are the product details:\n\n"
for product_name, price, url in product_details:
    body += f"Product: {product_name}\nPrice: {price}\nLink: {url}\n\n"

# Create the email
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject
message.attach(MIMEText(body, "plain"))

# Send the email
try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
    print("Email sent successfully!")
except Exception as e:
    print(f"Error sending email: {e}")

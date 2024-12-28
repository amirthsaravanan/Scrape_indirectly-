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

def web_driver():
    """Set up and return the WebDriver instance."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1200")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # Step 1: Open the website
    url = "https://buyhatke.com/"
    driver = web_driver()
    driver.get(url)

    # Step 2: Input the Amazon product URL
    amazon_url = "https://amzn.in/d/2atlNqL"
    search_bar = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "product-search-bar"))
    )
    search_bar.send_keys(amazon_url)
    search_bar.submit()

    # Step 3: Wait for the page to load
    time.sleep(30)

    # Step 4: Scrape the price details
    price = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.text-base.md\\:text-3xl.font-bold"))
    ).text

    low_price = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "p.text-sm.sm\\:text-lg.font-normal.leading-6"))
    ).text

    avg_price = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//p[contains(text(),'Average Price')]/.."))
    ).text

    print(f"Price: {price}")
    print(f"Low Price: {low_price}")
    print(f"Average Price: {avg_price}")

except Exception as e:
    print(f"An error occurred: {e}")
    price = low_price = avg_price = "N/A"

finally:
    driver.quit()

# Step 5: Email configuration
sender_email = os.getenv("SENDER_EMAIL")
sender_password = os.getenv("SENDER_PASSWORD")
receiver_email = os.getenv("RECEIVER_EMAIL")

if not sender_email or not sender_password or not receiver_email:
    raise ValueError("Email credentials not found in environment variables.")

subject = "BuyHatke Price Details"
body = (
    f"Product URL: {amazon_url}\n"
    f"Price: {price}\n"
    f"Low Price: {low_price}\n"
    f"Average Price: {avg_price}\n"
)

# Step 6: Send the email
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject
message.attach(MIMEText(body, "plain"))

try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
    print("Email sent successfully!")
except Exception as e:
    print(f"Error sending email: {e}")

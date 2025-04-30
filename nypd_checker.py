import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

load_dotenv()

# CONFIGURATION
CALENDLY_URL = "https://calendly.com/nypd_license_division/fingerprinting-appointment"
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN")
DATE_CUTOFF = datetime.strptime("2025-07-29", "%Y-%m-%d")
CHECK_INTERVAL = 60

driver_path = 'B:\\chromedriver.exe'

# Function to send push notification using Pushover
def send_pushover_notification(message):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": PUSHOVER_API_TOKEN,
            "user": PUSHOVER_USER_KEY,
            "message": message
        }
    )

# Function to check availability of appointments
def check_appointments():
    print("Checking for available appointments...")

    # Set up Selenium WebDriver with Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Set up WebDriver
    driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
    driver.get(CALENDLY_URL)

    # Wait for the page to load 
    time.sleep(5)

    try:
        # Get the page source
        page_source = driver.page_source

        # Check if the page contains the "No times in" message
        if "No times in" in page_source:
            print("No available slots for this month!")

        elif "- Times available" in page_source: 

            soup = BeautifulSoup(page_source, 'html.parser') 

            # Find all aria-labels with "- Times available"
            available_slots = soup.find_all(attrs={"aria-label": lambda x: x and "- Times available" in x})
            
            for slot in available_slots:
                label = slot["aria-label"]

                
                try:
                    month_day = label.split(',')[1].split('-')[0].strip() 
                    date_str = f"{month_day} 2025"
                    date_obj = datetime.strptime(date_str, "%B %d %Y")
   

                    # Check if the available slot is before the cutoff date
                    if date_obj <= DATE_CUTOFF:
                        print("Slot detected!")
                        print("Slot found:", label)
                        send_pushover_notification(f"NYPD fingerprinting slot open on {date_obj.strftime('%A %B %d, %Y')}!")
                except ValueError:
                    print(f"Could not parse date from: {label}")
        else:
            print("No recognizable slot or message found.")
            print(page_source.encode('ascii', errors='ignore').decode())

    except Exception as e:
        print(f"Error occurred: {e}")

    # Close the browser after checking
    driver.quit()


# Run in loop to check continuously
while True:
    try:
        check_appointments()
    except Exception as e:
        print(f"Error checking: {e}")
    time.sleep(CHECK_INTERVAL)

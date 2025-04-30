
import os
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

import requests
import time
from bs4 import BeautifulSoup

CALENDLY_URL = "https://calendly.com/nypd_license_division/fingerprinting-appointment"
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN")
CHECK_INTERVAL = 60  # in seconds

def send_pushover_notification(message):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": PUSHOVER_API_TOKEN,
            "user": PUSHOVER_USER_KEY,
            "message": message
        }
    )

def check_appointment():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(CALENDLY_URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    if "No times are currently available" not in soup.text:
        print("Slot detected!")
        send_pushover_notification("🚨 NYPD Fingerprinting slot is OPEN! Book now!")
    else:
        print("No slot available yet.")

# Run repeatedly (manually click the cell to run)
while True:
    try:
        check_appointment()
    except Exception as e:
        print(f"Error checking: {e}")
    time.sleep(CHECK_INTERVAL)

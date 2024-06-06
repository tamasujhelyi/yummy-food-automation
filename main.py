from email.message import EmailMessage
import os
import re
import smtplib

from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
sender_email = os.environ["sender_email"]
sender_email_app_password = os.environ["sender_email_app_password"]
recipient_email = os.environ["recipient_email"]
url = os.environ["url"]

# Variables for scraping
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
yummy_food_regex = re.compile(r"jalapeno|chili|császárok|gomba", re.IGNORECASE)

# Check if all required environment variables are loaded
if not all([sender_email, sender_email_app_password, recipient_email, url]):
    raise EnvironmentError("One or more environment variables are missing.")

def send_food_email(email_subject: str, email_body: str = "") -> None:
    """
    Create and send the automated email to a Gmail address.

    Args:
        email_subject (str): The subject of the email.
        email_body (str): The text content of the email.
    """

    # Create the email message
    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = email_subject
    msg.set_content(email_body)

    # Try to send the email using Gmail's SMTP server
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls() # Start TLS encryption
            server.login(sender_email, sender_email_app_password) # Login to the SMTP server
            server.send_message(msg) # Send the email
        print("Email sent successfully.")
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {str(e)}")

def check_url_for_yummy_food(url: str) -> None:
    """
    Scrape the url for foods from the "yummy_food_regex" variable.
    Then send an email about the result by calling "send_food_email()".

    Args:
        url (str): The url to scrape.
    """

    # Try to check the URL for yummy foods
    try:
        headers = {"User-Agent": user_agent}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # Create a list for storing foods we're interested in
            yummy_foods = []
            # Create a soup object from the scraped page
            soup = BeautifulSoup(response.text, "html.parser")

            # Get all foods from the scraped page
            em_tags = soup.find_all("em")
            for em_tag in em_tags:
                content = em_tag.decode_contents()
                foods_on_menu = content.split("<br/>")
                foods_on_menu = [BeautifulSoup(food_on_menu, "html.parser").get_text(strip=True) for food_on_menu in foods_on_menu]

                # Add matching food items to the "yummy_foods" list
                for food_on_menu in foods_on_menu:
                    if re.search(yummy_food_regex, food_on_menu):
                        yummy_foods.append(food_on_menu)

            # Send an email with yummy foods listed if yummy foods are found
            if yummy_foods:
                yummy_foods_in_email = "\n".join(yummy_foods)
                send_food_email("Yummy food's available! ^^", yummy_foods_in_email)
            # Otherwise send a different email if yummy foods are not available
            else:
                send_food_email(email_subject="No yummy food today. :(")

        # Send an email if the request was not successful
        else:
            send_food_email(email_subject=f"Failed to retrieve the page. Status code: {response.status_code}")

    # Send an email if there was a request exception
    except requests.RequestException as e:
        send_food_email(email_subject=f"An error occurred: {str(e)}")


if __name__ == "__main__":
    # Run the check_url_for_yummy_food function with the provided URL
    check_url_for_yummy_food(url)

import requests
import re
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

login_url = "https://service.handyvertrag.de/public/login_check"
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

session = requests.Session()
session.headers.update(headers)

def get_login_page():
    response = session.get(login_url, headers=headers)
    response.raise_for_status()
    return response.text

def extract_token(html):
    soup = BeautifulSoup(html, 'html.parser')
    token_element = soup.find('input', {'name': 'UserLoginType[_token]'})
    if token_element:
        return token_element.get('value')
    else:
        raise ValueError("Token not found in the login page")

def login(username, password, token):
    payload = {
        'UserLoginType[alias]': username,
        'UserLoginType[password]': password,
        'UserLoginType[_token]': token
    }
    response = session.post(login_url, data=payload, headers=headers)
    response.raise_for_status()
    return response.text

def extract_data_usage(html):
    soup = BeautifulSoup(html, 'html.parser')
    html_text = soup.get_text()

    data_usage_pattern = re.compile(r'Datenverbrauch\s+(\d+,\d+ MB)\s+von (\d+,\d+ GB) verbraucht', re.IGNORECASE)
    match = data_usage_pattern.search(html_text)

    if match:
        used_data = match.group(1)
        total_data = match.group(2)
    return used_data, total_data


try:
    login_page_html = get_login_page()
    token = extract_token(login_page_html)
    logged_in_html = login(username, password, token)
    used_data, total_data = extract_data_usage(logged_in_html)
    print("Data Usage:")
    print(f"Used: {used_data}")
    print(f"Total: {total_data}")

    
except requests.exceptions.RequestException as e:
    print("An error occurred during the request:", e)
except ValueError as e:
    print("An error occurred while extracting information:", e)


import requests
import pandas as pd
import os
from dotenv import load_dotenv


def fetch_data(url: str, headers: dict[str, str], timeout = 10):
    response = requests.get(url, headers = headers, timeout = 10)
    data = ""
    try:
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as e:
        print("HTTP error:", e)
    except ValueError:
        print("Invalid JSON")
    return data

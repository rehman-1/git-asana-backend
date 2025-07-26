
import requests
from app.asana.config import ASANA_ACCESS_TOKEN

headers = {
    "Authorization": f"Bearer {ASANA_ACCESS_TOKEN}"
}

def get(endpoint, params=None):
    url = f"https://app.asana.com/api/1.0/{endpoint}"
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()
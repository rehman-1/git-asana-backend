
import os
from dotenv import load_dotenv

load_dotenv()

ASANA_ACCESS_TOKEN = os.getenv("ASANA_ACCESS_TOKEN")
ASANA_WORKSPACE_ID = os.getenv("ASANA_WORKSPACE_ID")
ASANA_PROJECT_ID = os.getenv("ASANA_PROJECT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CACHE_DIR = "cache"


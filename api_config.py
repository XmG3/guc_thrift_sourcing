import os
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("EBAY_APP_ID")
CERT_ID = os.getenv("EBAY_CERT_ID")
DEV_ID = os.getenv("EBAY_DEV_ID")
OAUTH_TOKEN = os.getenv("EBAY_OAUTH_TOKEN")

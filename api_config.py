import os
from dotenv import load_dotenv

load_dotenv("keys.env")

APP_ID = os.getenv("EBAY_APP_ID")
CERT_ID = os.getenv("EBAY_CERT_ID")
DEV_ID = os.getenv("EBAY_DEV_ID")
OAUTH_TOKEN = os.getenv("EBAY_OAUTH_TOKEN")

#debugging
print("APP_ID loaded:", APP_ID[:10] + "..." if APP_ID else "None")
print("CERT_ID loaded:", CERT_ID[:10] + "..." if CERT_ID else "None")
print("DEV_ID loaded:", DEV_ID[:10] + "..." if DEV_ID else "None")
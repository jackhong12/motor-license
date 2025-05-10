import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_RECV = os.getenv("EMAIL_RECV")

SIGNUP_ID = os.getenv("SIGNUP_ID")
SIGNUP_BIRTH = os.getenv("SIGNUP_BIRTH")
SIGNUP_NAME = os.getenv("SIGNUP_NAME")
SIGNUP_PHONE = os.getenv("SIGNUP_PHONE")
SIGNUP_EMAIL = os.getenv("SIGNUP_EMAIL")

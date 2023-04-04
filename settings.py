import os

DEBUG = True

SECRET_KEY = os.getenv("SECRET_KEY")

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
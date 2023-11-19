import os

from dotenv import load_dotenv


load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

URL = os.getenv("URL")
TOKEN = os.getenv("TOKEN")


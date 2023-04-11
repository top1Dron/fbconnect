import base64
import json
import logging
import urllib
from pprint import pformat

import requests
from fastapi import FastAPI, HTTPException, Request
from messengerapi import SendApi
from pyfacebook import GraphAPI

import settings


logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": settings.SECRET_KEY, "token": settings.VERIFY_TOKEN}


@app.get("/webhook")
def hook_from_facebook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    # Checks if a token and mode is in the query string of the request
    if mode and token:

        # Checks the mode and token sent is correct
        if mode == "subscribe" and token == settings.VERIFY_TOKEN:
            print("WEBHOOK_VERIFIED")
            return int(challenge)
        else:
            raise HTTPException(status_code=403, detail="Authorization for webhook failed")
    return {}


@app.post("/webhook")
async def hook_to_facebook(request: Request):
    logger.info("Got new message - %s", pformat(await request.json()))
    return await request.json()


@app.get("/long-lived-token")
async def get_long_lived_access_token():
    response = requests.get(
        f'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id={settings.APP_ID}&client_secret={settings.APP_SECRET}&fb_exchange_token={settings.PAGE_ACCESS_TOKEN}',
    )
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=401, detail="Not authorized")


@app.get("/token")
async def get_access_token():
    response = requests.get(
        f'https://graph.facebook.com/oauth/access_token?grant_type=client_credentials&client_id={settings.APP_ID}&client_secret={settings.APP_SECRET}&fb_exchange_token={settings.PAGE_ACCESS_TOKEN}',
    )
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=401, detail="Not authorized")


@app.post("/send-message")
async def send_message(recipient_id: int, message: str):
    headers = {'content-type':  'application/json'}
    data = {
        "recipient": {
            "id": str(recipient_id)
        },
        "messaging_type": "RESPONSE",
        "message": {
            "text": message,
        },
        "access_token": f"{settings.LONG_LIVED_USER_ACCESS_TOKEN}"
    }
    response = requests.post(
        f"https://graph.facebook.com/v16.0/{int(settings.PAGE_ID)}/messages", data=json.dumps(data), headers=headers
    )
    if response.status_code == 200:
        return response.json()
    raise HTTPException(response.status_code, response.json())

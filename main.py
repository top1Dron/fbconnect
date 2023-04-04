import base64
import json
import logging
import urllib
from pprint import pformat

import requests
from fastapi import FastAPI, HTTPException, Request

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

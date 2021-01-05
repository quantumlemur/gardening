from os import environ
from time import time


import requests
from requests.exceptions import HTTPError
from twilio.rest import Client


try:
    response = requests.get("http://nuc/api/get_devices")
    response.raise_for_status()
    # access JSOn content
    devices = response.json()

    watering_phones = environ["NOTIFY_WATERING_PHONES"].split(":")
    status_phones = environ["NOTIFY_STATUS_PHONES"].split(":")

    # Your Account Sid and Auth Token from twilio.com/console
    # and set the environment variables. See http://twil.io/secure
    account_sid = environ["TWILIO_ACCOUNT_SID"]
    auth_token = environ["TWILIO_AUTH_TOKEN"]
    client = Client(account_sid, auth_token)

    thirsty_plants = [
        device["name"]
        for device in devices
        if device["calibrated_value"] and device["calibrated_value"] > 0.8
    ]
    if len(thirsty_plants) > 0:
        body = "\r\n".join(thirsty_plants)
        body = (
            f"We're thirsty:\r\n{body}"
            if len(thirsty_plants) > 1
            else f"I'm thirsty:\r\n{body}"
        )
        for phone in watering_phones:
            client.messages.create(
                body=body,
                from_="+12513192223",
                to=phone,
            )

    lowvolt_devices = [
        device["name"] for device in devices if device["volt"] and device["volt"] < 3600
    ]
    if len(lowvolt_devices) > 0:
        body = "\r\n".join(lowvolt_devices)
        body = (
            f"We need a battery change:\r\n{body}"
            if len(lowvolt_devices) > 1
            else f"I need a battery change:\r\n{body}"
        )
        for phone in status_phones:
            client.messages.create(
                body=body,
                from_="+12513192223",
                to=phone,
            )

    missing_devices = [
        device["name"]
        for device in devices
        if device["device_next_init"]
        and time() > (device["device_next_init"] + 60 * 30)
    ]
    if len(missing_devices) > 0:
        body = "\r\n".join(missing_devices)
        body = (
            f"We missed our last check-in. Please investigate:\r\n{body}"
            if len(missing_devices) > 1
            else f"I missed my last check-in. Please investigate:\r\n{body}"
        )
        for phone in status_phones:
            client.messages.create(
                body=body,
                from_="+12513192223",
                to=phone,
            )


except HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
except Exception as err:
    print(f"Other error occurred: {err}")

# os.system('google-chrome --headless --disable-gpu --screenshot --virtual-time-budget=10000 --window-size=550,2300 --hide-scrollbars http://localhost:3000/screenshot')

# coding=utf-8

import schedule
import time
import requests
import math
from twilio.rest import Client

def distance(lat, lng):
    return 364000 * math.sqrt((lat - 42.380268)**2 + (lng - -71.118363)**2)

# called at intervals
def job():
    # Find these values at https://twilio.com/user/account
    account_sid = "AC059cc06e86b53d22b9fabd5266605dc1"
    auth_token = "0e83a0732e76b12bbd5e5d904435a797"
    client = Client(account_sid, auth_token)

    stations = {}

    station_list = requests.get("https://gbfs.thehubway.com/gbfs/en/station_information.json")
    for station in station_list.json()["data"]["stations"]:
        if "SEAS" in station["name"]:
            stations[station["station_id"]] = {"name": station["name"],
                                                "dist" : distance(station["lat"], station["lon"]),
                                                "short": "SEAS"}
        elif "Harvard Law School" in station["name"]:
            stations[station["station_id"]] = {"name" : station["name"],
                                                "dist" : distance(station["lat"], station["lon"]),
                                                "short" : "HLS"}
        elif "Conway Park" in station["name"]:
            stations[station["station_id"]] = {"name" : station["name"],
                                                "dist" : distance(station["lat"], station["lon"]),
                                                "short" : "CNWY"}

    station_status = requests.get("https://gbfs.thehubway.com/gbfs/en/station_status.json")
    station_status = station_status.json()["data"]["stations"]

    for station in station_status:
        if station["station_id"] in stations.keys():
            stations[station["station_id"]]["docks"] = station["num_docks_available"]
            stations[station["station_id"]]["bikes"] = station["num_bikes_available"]
            stations[station["station_id"]]["status"] = station["is_renting"]

    text = u"🚲 " + time.strftime("%b %d %Y") + "\n"

    for station in stations.values():
        if station["status"] == 1 and station["bikes"] >= 1:
            text += u" ✅ "
        elif station["bikes"] == 0:
            text += u" ✴️ "
        else:
            text += u" 🆘 "

        text += station["short"] + " " + str(station["bikes"]) + "🚲 (" + str(station["docks"]) + ") |"

    message = client.api.account.messages.create(to="+16178172456",
                                                 from_="+16179776976",
                                                 body=text)

    return text

# When to run?
schedule.every().saturday.at("23:30").do(job)
schedule.every().saturday.at("00:00").do(job)
schedule.every().monday.at("6:30").do(job)
schedule.every().tuesday.at("6:30").do(job)
schedule.every().wednesday.at("6:30").do(job)
schedule.every().thursday.at("6:30").do(job)
schedule.every().friday.at("6:30").do(job)
schedule.every().saturday.at("8:45").do(job)
schedule.every().sunday.at("8:45").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)

#!/usr/bin/env python

from flask import Flask, jsonify
from requests import get
with open('steam.txt', 'r') as myfile:
    key = myfile.read()

app = Flask(__name__)

app.debug = True


@app.route("/get")
def get_BA():
    r = get("http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid=440&key=" +
            key + "&steamid=76561197962272442")
    rjs = r.json()
    rjs["playerstats"]["gameName"] = "Kekswichsen 3.0"
    ach_all = rjs["playerstats"]["achievements"]
    unlocked = 0
    for x in ach_all:
        if x["achieved"] == 1:
            unlocked = unlocked + 1
    rjs["private"] = {}
    rjs["private"]["Unlocked Achievements"] = unlocked
    return jsonify(rjs)


@app.route("/")
def test():
    return jsonify({1: "ein", 2: "schluessel", 3: "fuer", 4: "schloesser"})


@app.route("/games")
def list_Games():
    return jsonify({1: "quake", 2: "DotA"})


app.run()

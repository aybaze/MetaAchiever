#!/usr/bin/env python

from flask import Flask, jsonify
from requests import get
with open('steam.txt', 'r') as myfile:
    key = myfile.read()
import unlocked
import connect

app = Flask(__name__)

app.debug = True

@app.route("/get")
def display_unlocked_achievements():
    #hardcode for testing
    steam_id = 76561197962272442
    game_id = 440
    #
    list_of_achievements_per_game = connect.get_achievements_steam_single(steam_id, key, game_id)
    #number of unlocked achievements
    #count_of_unlocked_achievements = unlocked.count_unlocked_achievements(list_of_achievements_per_game)
    #list all unlocked achievements
    unlocked_achievements = unlocked.list_unlocked_achievements(list_of_achievements_per_game)
    return list_of_achievements_per_game
    #return unlocked_achievements


@app.route("/")
def test():
    return jsonify({1: "ein", 2: "schluessel", 3: "fuer", 4: "schloesser"})


@app.route("/games")
def list_Games():
    return jsonify({1: "quake", 2: "DotA"})

app.run()



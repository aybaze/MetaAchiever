#!/usr/bin/env python

from flask import Flask, jsonify
from pymodm import connect
from pymongo.errors import ServerSelectionTimeoutError

from common.achievement import Achievement

import unlocked
import data

# create a new Flask object
app = Flask(__name__)


def init_game_data():
    """Initializes game data

    TODO: this will later fetch game data from various sources, for now we just have a few hard-coded achievements to play around with
    """

    a = Achievement("some-id", "Some human-readable name",
                    "A short description", None, "Steam")
    a.save()


@app.route("/achievements")
def get_achievements():
    return jsonify([a.serialize() for a in Achievement.objects.all()])


@app.route("/achievements/unlocked")
def get_unlocked_achievements():
    # hardcode for testing
    steam_id = 76561197962272442
    game_id = 440

    list_of_achievements_per_game = data.get_achievements_steam_single(
        steam_id, key, game_id)
    # number of unlocked achievements
    count_of_unlocked_achievements = unlocked.count_unlocked_achievements(
        list_of_achievements_per_game)

    # list all unlocked achievements
    unlocked_achievements = unlocked.list_unlocked_achievements(
        list_of_achievements_per_game)

    return jsonify(unlocked_achievements)


@app.route("/")
def test():
    return jsonify({1: "ein", 2: "schluessel", 3: "fuer", 4: "schloesser"})


@app.route("/games")
def get_games():
    return jsonify({1: "quake", 2: "DotA"})


if __name__ == "__main__":
    # retrieve the Steam API key from our 'config' file
    with open('steam.txt', 'r') as myfile:
        key = myfile.read()

    # enable debugging for now
    app.debug = True

    try:
        # establish MongoDB connection with (almost) no timeout, so we fail (almost) immediately
        connect('mongodb://localhost:27017/MetaAchiever',
                serverSelectionTimeoutMS=1000)

        # some initialization of game data, achievements, ...
        init_game_data()
    except ServerSelectionTimeoutError:
        # Continue for now, so @ipec can play around 'offline'
        pass

    # start the REST API
    app.run()

#!/usr/bin/env python

from datetime import datetime

from flask import Flask, jsonify, make_response
from py2neo import Graph, Database

from common.model import Achievement, Game, Player

import unlocked
import data
import imports
import os

# create a new Flask object
app = Flask(__name__)


@app.route("/achievements")
def get_achievements() -> str:
    return jsonify([achievement.to_dict() for achievement in Achievement.select(graph)])


@app.route("/achievements/unlocked")
def get_unlocked_achievements() -> str:
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
def test() -> str:
    return jsonify({1: "ein", 2: "schluessel", 3: "fuer", 4: "schloesser"})


@app.route("/games")
def get_games() -> str:
    return jsonify([game.to_dict() for game in Game.select(graph)])


@app.route("/games/<id>/achievements")
def get_achievement_for_game(id) -> str:
    game: Game = Game.select(graph, id).first()

    if game is not None:
        return jsonify([achievement.to_dict() for achievement in game.achievements])
    else:
        return make_response('Game not found', 404)


@app.route("/players")
def get_players() -> str:
    return jsonify([player.to_dict() for player in Player.select(graph)])


if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        # retrieve the Steam API key from our 'config' file
        with open('steam.txt', 'r') as myfile:
            key = myfile.read()

        graph = Graph(username="neo4j", password="password")

        # some initialization of game data, achievements, ...
        imports.steam(76561197966228499, graph, key)  # biftheki
        imports.steam(76561197962272442, graph, key)  # oxisto
        imports.steam(76561197960824521, graph, key)  # ipec
        imports.steam(76561197960616970, graph, key)  # neo

    # start the REST API
    app.run(debug=True)

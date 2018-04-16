#!/usr/bin/env python

from multiprocessing import Process
import os

from flask import Flask, jsonify, make_response

from neomodel import config as neoconfig

import yaml
import unlocked
import data
import imports

from common.model import Achievement, Game, Player, to_dict

# create a new Flask object
app = Flask(__name__)


@app.route("/achievements")
def get_achievements() -> str:
    return jsonify([achievement.__dict__ for achievement in Achievement.nodes.all()])


@app.route("/achievements/unlocked")
def get_unlocked_achievements() -> str:
    # hardcode for testing
    steam_id = 76561197962272442
    game_id = 440

    list_of_achievements_per_game = data.get_achievements_steam_single(
        steam_id, cfg["steam"]["key"], game_id)
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
    return jsonify([to_dict(game) for game in Game.nodes.all()])


@app.route("/games/<int:app_id>/achievements")
def get_achievement_for_game(app_id) -> str:
    game: Game = Game.nodes.get_or_none(steam_app_id=app_id)

    if game is not None:
        return jsonify([to_dict(achievement) for achievement in game.achievements.all()])
    else:
        return make_response('Game not found', 404)


@app.route("/players")
def get_players() -> str:
    return jsonify([player.to_dict() for player in Player.nodes.all()])


def do_imports(cfg):
    neoconfig.DATABASE_URL = cfg["neo4j"]["uri"]

    # some initialization of game data, achievements, ...
    imports.steam(76561197966228499, cfg["steam"]["key"])  # biftheki
    imports.steam(76561197962272442, cfg["steam"]["key"])  # oxisto
    imports.steam(76561197960824521, cfg["steam"]["key"])  # ipec
    imports.steam(76561197960616970, cfg["steam"]["key"])  # neo

    print("Done with imports")


if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        # our default configuration
        default_cfg = {
            "neo4j": {
                "uri": "bolt://localhost:7687",
                "username": "neo4j",
                "password": "password"
            },
            "steam": {}
        }

        # load config file
        ymlfile = open("config.yml", "r")

        # merge default configuration with the one in the yaml file
        cfg = {**default_cfg, **yaml.load(ymlfile)}

        if "key" not in cfg["steam"]:
            print("Please provide a steam key.")
            exit(-1)

        neoconfig.DATABASE_URL = cfg["neo4j"]["uri"]

        # launch a seperate thread/process for imports
        print("Spawing imports process")
        p = Process(target=do_imports, args=(cfg,))
        p.start()

    # start the REST API
    app.run(debug=True)

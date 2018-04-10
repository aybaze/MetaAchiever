from py2neo import Graph
from requests import get

from common.model import Achievement, Game, Player


def steam(graph: Graph, key: str):
    # some hardcoded stuff for testing
    steam_id = 76561197962272442
    app_id = 440

    # Import player data
    response = get("http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=" +
                   str(key) + "&steamids=" + str(steam_id))
    player_details = response.json()
    player = Player()
    player.id = steam_id
    player.name = player_details["response"]["players"][0]["personaname"]

    # Check if already exists
    game = Game.select(graph, app_id).first()

    if game is not None:
        print("Game already exists in graph. Skipping import")
        return

    # Import general game data (HARDCODED TO TF2)
    response = get(
        "http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key=" + key + "&appid=" + str(app_id))
    game_details = response.json()

    game = Game()
    game.id = app_id
    game.name = game_details["game"]["gameName"]

    # Import achievements
    for a in game_details["game"]["availableGameStats"]["achievements"]:
        # fill an achievement from JSON
        achievement = Achievement()
        achievement.id = a["name"]
        achievement.name = a["displayName"]
        achievement.source = "Steam"
        achievement.description = a["description"]
        achievement.image_url = a["icon"]
        achievement.achieved_in = game
        # Put achievement into game
        game.achievements.add(achievement)

    # Put game into player
    player.games.add(game)

    # Push game to graph (save)
    graph.push(player)

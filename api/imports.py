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

<<<<<<< HEAD
    # Import all games with playtime > 0
    response = get("http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=" +
                   key + "&steamid=" + str(steam_ID) + "&format=json")
    all_games = response.json()

    # Put played games into list
    played_games = []
    for a in all_games["response"]["games"]:
        if a["playtime_forever"] > 0:
            played_games.append(a["appid"])

    # Obtain all achievements for a game and store into player
    for appid in played_games:
        game = steam_schema_for_game(appid, key, graph)
        if game != None:
            player.games.add(game)

    graph.push(player)


def steam_schema_for_game(appid: int, key: str, graph: Graph) -> Game:
    # Get game details for specific game
    response = get("http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key=" +
                   str(key) + "&appid=" + str(appid))
=======
    # Check if already exists
    game = Game.select(graph, app_id).first()

    if game is not None:
        print("Game already exists in graph. Skipping import")
        return

    # Import general game data (HARDCODED TO TF2)
    response = get(
        "http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key=" + key + "&appid=" + str(app_id))
>>>>>>> 8fb4a521b62b40254debb2452e7625d022e692a6
    game_details = response.json()

    # Skip game if no achievements or no gameName
    if "availableGameStats" not in game_details["game"]:
        return None
    if "achievements" not in game_details["game"]["availableGameStats"]:
        return None

    # Create Graph object for game
    game = Game()
<<<<<<< HEAD
    game.id = appid
=======
    game.id = app_id
>>>>>>> 8fb4a521b62b40254debb2452e7625d022e692a6
    game.name = game_details["game"]["gameName"]

    # Walk thru all achievements for game and save into game
    for a in game_details["game"]["availableGameStats"]["achievements"]:
        achievement = Achievement()
        achievement.id = a["name"]
        achievement.name = a["displayName"]
        achievement.source = "Steam"
        if "description" in a:
            achievement.description = a["description"]
        achievement.achieved_in = game
        game.achievements.add(achievement)

    return game

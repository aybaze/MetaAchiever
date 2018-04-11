from py2neo import Graph
from requests import get

from common.model import Achievement, Game, Player


def steam(graph: Graph, key: str):
    # some hardcoded stuff for testing
    steam_id = 76561197962272442

    # Import player data
    response = get("http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=" +
                   str(key) + "&steamids=" + str(steam_id))
    player_details = response.json()
    player = Player()
    player.id = steam_id
    player.name = player_details["response"]["players"][0]["personaname"]

    # Import all games with playtime > 0
    response = get("http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=" +
                   key + "&steamid=" + str(steam_id) + "&format=json")
    all_games = response.json()

    # Put played games into list
    for game_detail in all_games["response"]["games"]:
        # Obtain all achievements for a game and store into player if playtime is greater than 0
        if game_detail["playtime_forever"] > 0:
            app_id = game_detail["appid"]

            # Check, if game already exists
            game: Game = Game.select(graph, app_id).first()

            if game is not None:
                print("Game " + str(app_id) + " already found in graph")
            else:
                # Fetch from Steam
                game = steam_schema_for_game(app_id, key, graph)

            # Associate with player if we found valid game data
            if game != None:
                player.games.add(game)

                # Push the game
                graph.push(game)

    graph.push(player)


def steam_schema_for_game(app_id: int, key: str, graph: Graph) -> Game:
    print("Game " + str(app_id) + " not yet found in graph. Fetching from API...")

    # Get game details for specific game
    response = get("http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key=" +
                   str(key) + "&appid=" + str(app_id))
    game_details = response.json()

    # Skip game if no achievements or no gameName
    if "availableGameStats" not in game_details["game"]:
        return None
    if "achievements" not in game_details["game"]["availableGameStats"]:
        return None

    # Create Graph object for game
    game = Game()
    game.id = app_id
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

from py2neo import Graph, Relationship
from requests import get

from common.model import Achievement, Game, Player


def steam(steam_id: int, graph: Graph, key: str):
    # some hardcoded stuff for testing

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

    app_ids = {}
    # Put played games into list
    for game_detail in all_games["response"]["games"]:
        if game_detail["playtime_forever"] > 0:
            app_ids[game_detail["appid"]] = True

    # Retrieve all games, that are already in the graph
    nodes = graph.run(
        "MATCH (g:Game) WHERE g.id IN {app_ids} RETURN g", {'app_ids': list(app_ids.keys())})

    # Make sure, the player exists before we continue
    graph.push(player)

    # Loop through existing games
    for node in nodes:
        # Add it to the player
        graph.create(Relationship(player.__ogm__.node, "owns", node["g"]))

        # And remove it from the fetch list
        app_ids[node["g"]["id"]] = False

    for app_id, need_to_fetch in app_ids.items():
        if need_to_fetch:
            print("Game " + str(app_id) +
                  " not yet found in graph. Fetching from API...")

            # Fetch from Steam
            game = import_game(app_id, key)

            player.games.add(game)

            # Push the game
            graph.push(game)

    graph.push(player)


def import_game(app_id: str, key: str) -> Game:
    store_info = fetch_store_info(app_id)

    # Create Graph object for game
    game = Game()
    game.id = app_id

    if str(app_id) not in store_info or "data" not in store_info[str(app_id)]:
        print("Could not retrieve store information for " +
              str(app_id) + ". Flagging game as incomplete.")
        # Create a dummy game for incomplete data
        game.name = str(app_id)
        game.incomplete = True
    else:
        # Take name from store API
        game.name = store_info[str(app_id)]["data"]["name"]

    # Check, if the game incomplete or has achievements, otherwise, we're done now
    if game.incomplete is True or ("achievements" in store_info[str(app_id)]["data"] and store_info[str(app_id)]["data"]["achievements"]["total"] > 0):
        # Get schema for game
        schema = get_schema_for_game(app_id, key)
        print(schema)

        # If the schema also does not contain any name, we can only return now
        if "gameName" not in schema["game"]:
            return game

        # If its an incomplete game, at least try to find a name from the schema (although it might be a wierd test name)
        if game.incomplete is True:
            game.name = schema["game"]["gameName"]

            # If the name is valid, i.e. not a ValveTestAppName, we can take away the incomplete flag
            if game.name != ("ValveTestApp" + str(app_id)):
                print("Found a valid name for " + str(app_id) +
                      "Recovered from incomplete state.")
                game.incomplete = False

        # Walk thru all achievements for game and save into game
        for a in schema["game"]["availableGameStats"]["achievements"]:
            achievement = Achievement()
            achievement.id = a["name"]
            achievement.name = a["displayName"]
            achievement.source = "Steam"

            # Description is optional
            if "description" in a:
                achievement.description = a["description"]

            game.achievements.add(achievement)

    return game


def fetch_store_info(app_id: list) -> dict:
    query = "http://store.steampowered.com/api/appdetails?appids=" + \
        str(app_id) + "&filters=basic,achievements"
    response = get(query)

    return response.json()


def get_schema_for_game(app_id: int, key: str) -> dict:
    response = get("http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key=" +
                   key + "&appid=" + str(app_id))
    return response.json()

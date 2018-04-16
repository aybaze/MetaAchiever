from requests import get

from neomodel import NodeSet, db

from common.model import Achievement, Game, Player, to_dict

import logging
import sys

log: logging.Logger = logging.getLogger('import')
log.setLevel(logging.INFO)

ch = logging.StreamHandler(stream=sys.stdout)
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

log.addHandler(ch)


def steam(steam_id: int, key: str):
    # some hardcoded stuff for testing

    log.info("Starting import for player %d", steam_id)

    # Import player data
    response = get("http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=" +
                   str(key) + "&steamids=" + str(steam_id))
    player_details = response.json()

    player: Player = Player.get_or_create({
        'steam_id': steam_id,
        'name': player_details["response"]["players"][0]["personaname"]})[0]

    # Import all games with playtime > 0
    response = get("http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=" +
                   key + "&steamid=" + str(steam_id) + "&format=json")
    all_games = response.json()

    app_ids = {}
    # Put played games into list
    for game_detail in all_games["response"]["games"]:
        # if game_detail["playtime_forever"] > 0:
        app_ids[game_detail["appid"]] = True

    log.info("Fetching existing games..")

    # Retrieve all games, that are already in the graph
    games: NodeSet = Game.nodes.filter(steam_app_id__in=list(app_ids.keys()))

    # Make sure, the player exists before we continue
    player.save()

    log.info("Building relationships to existing games...")

    # Loop through existing games
    # ignore for now
    owned_games = list(
        map(lambda game: game.steam_app_id, player.games.all()))

    for game in games:
        # only add the game if its not already owned
        if game.steam_app_id not in owned_games:
            player.games.connect(game)

        # And remove it from the fetch list
        app_ids[game.steam_app_id] = False

    log.info("Fetching game info from non-existing games...")

    for app_id, need_to_fetch in app_ids.items():
        if need_to_fetch:
            log.info("Game %d not yet found in graph. Fetching from API...", app_id)

            db.begin()

            # Fetch from Steam
            game = import_game(app_id, key)

            # make sure its saved before establishing the relationship
            game.save()

            player.games.connect(game)

            db.commit()

    log.info("Saving player...")


def import_game(app_id: str, key: str) -> Game:
    store_info = fetch_store_info(app_id)

    # Create Graph object for game
    game = Game()
    game.steam_app_id = app_id

    if str(app_id) not in store_info or "data" not in store_info[str(app_id)]:
        log.info(
            "Could not retrieve store information for %d. Flagging game as incomplete.", app_id)
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

        # If the schema also does not contain any name, we can only return now
        if "gameName" not in schema["game"]:
            return game

        # If its an incomplete game, at least try to find a name from the schema (although it might be a wierd test name)
        if game.incomplete is True:
            game.name = schema["game"]["gameName"]

            # If the name is valid, i.e. not a ValveTestAppName, we can take away the incomplete flag
            if game.name != ("ValveTestApp" + str(app_id)):
                log.info(
                    "Found a valid name for %d. Recovered from incomplete state.", app_id)
                game.incomplete = False

        # Save the game so its available
        game.save()

        try:
            log.info("Need to insert %d achievements for %s", len(
                schema["game"]["availableGameStats"]["achievements"]), game.name)

            # Walk thru all achievements for game and save into game
            for a in schema["game"]["availableGameStats"]["achievements"]:
                achievement = Achievement()
                # achievement "names" are not globally unique
                # achievement.id = str(game.id) + "_" + a["name"]
                achievement.api_name = a["name"]
                achievement.name = a["displayName"]
                achievement.source = "Steam"

                # Description is optional
                if "description" in a:
                    achievement.description = a["description"]

                # save the achievement
                achievement.save()

                game.achievements.connect(achievement)
        except Exception:
            log.error("Could not parse achievement data for %s. Maybe the game does not contain any achievements.",
                      game.name, exception)

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

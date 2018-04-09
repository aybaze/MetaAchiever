# connect to service and return list of achievements
from requests import get


def get_achievements_steam_single(user_id, key, app_id):
    # request player details
    response = get("http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid=" +
                   str(app_id) + "&key=" + key + "&steamid=" + str(user_id))

    # build json object
    player_details_json = response.json()
    achievement_list = player_details_json["playerstats"]["achievements"]

    return achievement_list


def get_player_achievements_ubisoft(user_id, key, app_id):
    return 0

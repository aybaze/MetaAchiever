#connect to service and return list of achievements
from flask import Flask, jsonify
from requests import get

def get_achievements_steam_single(user_id, key, app_id):
    #request player details
    achievement_list_raw = get("http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid=" + app_id + "&key="+ key + "&steamid=" + user_id)
    #build json object
    achievement_list = achievement_list_raw.jsonify()
    return achievement_list

def get_player_achievements_ubisoft(user_id, key, app_id):
    return 0

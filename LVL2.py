from decimal import DivisionByZero
import requests
import pandas as pd
from collections import defaultdict
import tkinter as tk
from pandastable import Table
import sqlite3
import os
import csv

from shared import API_KEY, REGION, base_url
from LVL1 import ( get_puuid_by_username_tagline, get_username_tagline_by_puuid, get_match_history_by_puuid,
                    get_gameJson_by_matchID, get_match_stats_by_matchID, write_to_csv,
                    convert_team_statistics, show_dataframe, load_team_stats, load_winners )

                    

def get_match_history_by_username_tagline(username, tagline,  start=0, count=20, REGION=REGION, API_KEY=API_KEY):
    user_puuid = get_puuid_by_username_tagline(username, tagline, REGION=REGION, API_KEY=API_KEY)
    return get_match_history_by_puuid(user_puuid, start, count)

def process_match_by_ID(matchID, count=5):
    """Processes match and updates player statistics over the last 100 games."""
    match_json = get_gameJson_by_matchID(matchID)
    side_dict = {100: 'blue', 200: 'red'}

    teams = match_json['info']['teams']
    winner = 0  

    for team in teams:
        print(f"Checking team {team['teamId']} win status: {team['win']}")
        if team['win']:
            winner = team['teamId'] 
            break 
    
    print("Winner detected:", winner)  
    
    try:
        metadata = match_json['metadata']
        matchId = metadata['matchId']
        participants = metadata['participants']
        
        teams_data = {100: [], 200: []}  
        
        # print(f"1 - {type(match_json['info']['participants'])}")
        # Players
        if len(match_json['info']['participants']) != 10:
            return -120


        k = 1
        for p in match_json['info']['participants']:
            player_puuid = p['puuid']
            team_id = p['teamId']

            wins = 0
            loses = 0
            games = 0

            kills = 0
            deaths = 0
            assists = 0

            # Player Matches
            match_history = get_match_history_by_puuid(player_puuid, start=0, count=count)
            # print(f"2 - {type(match_history)}")
            for match in match_history:
                stats = get_match_stats_by_matchID(match, player_puuid)

                if stats is None:
                    continue

                games = games + 1

                kills = kills + stats['kills']
                deaths = deaths + stats['deaths']
                assists = assists + stats['assists']

                wins = wins + 1 if stats['win'] else wins
                loses = loses + 1 if not stats['win'] else loses
                
            try:
                player_kda_overall = (kills + assists) / deaths if deaths > 0 else kills + assists
                player_wr_overall = wins / games if games > 0 else 0
            except:
                print("Error While Calculating Player KDA or WR")

            print(f"({k}) Player Processed...")
            k += 1
            player_stats = {
                'player_kda_overall': player_kda_overall,
                'player_wr_overall': player_wr_overall
            }
            teams_data[team_id].append(player_stats)
        
        return teams_data[100], teams_data[200], winner 
    
    except Exception as e:
        print(f"Error processing match data: {e}")
        return [], []  

def show_team_data(team_stats):
    try:
        df = convert_team_statistics(team_stats [:-1])

        show_dataframe(df)
    except Exception as e:
        print(f"Error While Showing Team Stats: {e}")

def write_stats_to_csv(team_stats):
    try:
        write_to_csv("team1", team_stats[0])
        write_to_csv("team2", team_stats[1])
        write_to_csv("winners", team_stats[2])
    except:
        print("Error While Writing In CSV File")

def load_stats_from_csv(file_path1="team1", file_path2="team2", file_path3="winners"):
    try:
        team1 = load_team_stats(file_path1)
        team2 = load_team_stats(file_path2)
        winners = load_winners(file_path3)
    except:
        print("Error While Loading From CSV File")
    return team1, team2, winners




# ------------------ #
# NOT IN USE FOR NOW # 
# ------------------ #

def process_match_by_ID_all(matchID, count=5):
    match_json = get_gameJson_by_matchID(matchId, REGION=REGION, API_KEY=API_KEY)
    side_dict = {100: 'blue', 200: 'red'}
    """Processes match JSON and updates player statistics over the last 100 games."""
    side_dict = {100: 'blue', 200: 'red'}
    
    try:
        info = match_json['info']
        metadata = match_json['metadata']
        matchId = metadata['matchId']
        participants = metadata['participants']
        
        teams_data = {100: [], 200: []}  # Store team-wise player stats
        
        for p in info['participants']:
            player_puuid = p['puuid']
            team_id = p['teamId']
            role = p.get('teamPosition', '')
            champion = p['championName']

            wins = 0
            loses = 0
            games = 0

            wins_role = 0
            loses_role = 0
            games_role = 0

            wins_champ = 0
            loses_champ = 0
            games_champ = 0

            kills = 0
            deaths = 0
            assists = 0

            kills_role = 0
            deaths_role = 0
            assists_role = 0

            kills_champ = 0
            deaths_champ = 0
            assists_champ = 0

            cs = 0
            avg_gold_earned = 0

            cs_role = 0
            avg_gold_earned_role = 0

            cs_champ = 0
            avg_gold_earned_champ = 0

            match_history = get_match_history_by_puuid(player_puuid, start=0, count=count)
            for match in match_history:
                stats = get_match_stats_by_matchID(match, player_puuid)

                if stats is None:
                    continue

                games = games + 1

                kills = kills + stats['kills']
                deaths = deaths + stats['deaths']
                assists = assists + stats['assists']

                wins = wins + 1 if stats['win'] else wins
                loses = loses + 1 if not stats['win'] else loses

                cs = cs + stats['cs']
                avg_gold_earned = avg_gold_earned + stats['gold_earned']
                
                if stats['role'] == role:
                    games_role = games_role + 1

                    kills_role = kills_role + stats['kills']
                    deaths_role = deaths_role + stats['deaths']
                    assists_role = assists_role + stats['assists']

                    wins_role = wins_role + 1 if stats['win'] else wins_role
                    loses_role = loses_role + 1 if not stats['win'] else loses_role

                    cs_role = cs_role + stats['cs']
                    avg_gold_earned_role = avg_gold_earned_role + stats['gold_earned']

                if stats['champion'] == champion:
                    games_champ = games_champ + 1

                    kills_champ = kills_champ + stats['kills']
                    deaths_champ = deaths_champ + stats['deaths']
                    assists_champ = assists_champ + stats['assists']

                    wins_champ = wins_champ + 1 if stats['win'] else wins_champ
                    loses_champ = loses_champ + 1 if not stats['win'] else loses_champ

                    cs_champ = cs_champ + stats['cs']
                    avg_gold_earned_champ = avg_gold_earned_champ + stats['gold_earned']

                # -------------- #
                # -------------- #
                # -------------- #
                
            try:
                player_kda_overall = (kills + assists) / deaths if deaths > 0 else kills + assists
                player_wr_overall = wins / games if games > 0 else 0
                player_cs_overall = cs / games if games > 0 else 0
                player_gold_overall = avg_gold_earned / games if games > 0 else 0

                player_kda_role = (kills_role + assists_role) / deaths_role if deaths_role > 0 else kills_role + assists_role
                player_wr_role = wins_role / games_role if games_role > 0 else 0
                player_cs_role = cs_role / games_role if games_role > 0 else 0
                player_gold_role = avg_gold_earned_role / games_role if games_role > 0 else 0

                player_kda_champ = (kills_champ + assists_champ) / deaths_champ if deaths_champ > 0 else kills_champ + assists_champ
                player_wr_champ = wins_champ / games_champ if games_champ > 0 else 0
                player_cs_champ = cs_champ / games_champ if games_champ > 0 else 0
                player_gold_champ = avg_gold_earned_champ / games_champ if games_champ > 0 else 0
            except:
                print("Zero Division Error")

            print("Player Proccessed...")
            player_stats = {
                #'riot_id': p.get('summonerName', ''),
                #'match_id': matchId,
                #'puuid': player_puuid,

                'team_id': team_id,
                'role': role,
                'champion': champion,

                'player_kda_overall' : player_kda_overall,
                'player_wr_overall' : player_wr_overall,
                'player_cs_overall' : player_cs_overall,
                'player_gold_overall' : player_gold_overall,

                'player_kda_role' : player_kda_role,
                'player_wr_role' : player_wr_role,
                'player_cs_role' : player_cs_role,
                'player_gold_role' : player_gold_role,

                'player_kda_champ' : player_kda_champ,
                'player_wr_champ' : player_wr_champ,
                'player_cs_champ' : player_cs_champ,
                'player_gold_champ' : player_gold_champ,
            }
            teams_data[team_id].append(player_stats)
        
        return teams_data[100], teams_data[200]  # Return separate lists for both teams
    
    except Exception as e:
        print(f"Error processing match data: {e}")
        return [], []  # Return empty lists on error
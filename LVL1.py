from decimal import DivisionByZero
import requests
import pandas as pd
from collections import defaultdict
import tkinter as tk
from pandastable import Table
import sqlite3
import os
import csv
import time

from shared import API_KEY, REGION, base_url


#1
def get_puuid_by_username_tagline(username, tagline, REGION=REGION, API_KEY=API_KEY):
    base_url = f"https://{REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{username}/{tagline}"
    real_url = base_url + '?api_key=' + API_KEY

    while True:
        response = requests.get(real_url)
        if response.status_code == 200:
            return response.json()['puuid']
        else:
            print(f"Response Code: {response.status_code}")
            print(f"Response Reason: {response.reason}")
            print("Sleeping For 30 Sec...")
            time.sleep(30)

#2
def get_username_tagline_by_puuid(puuid, REGION=REGION, API_KEY=API_KEY):
    base_url = f"https://{REGION}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}"
    real_url = base_url + '?api_key=' + API_KEY

    while True:
        response = requests.get(real_url)
        if response.status_code == 200:
            return [response.json()['gameName'], response.json()['tagLine']]
        else:
            print(f"Response Code: {response.status_code}")
            print(f"Response Reason: {response.reason}")
            print("Sleeping For 30 Sec...")
            time.sleep(30)

#3
def get_match_history_by_puuid(puuid, start=0, count=20, REGION=REGION, API_KEY=API_KEY):
    base_url = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    mid_url = f'?start={start}&count={count}'
    real_url = base_url + mid_url + '&api_key=' + API_KEY

    while True:
        response = requests.get(real_url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Response Code: {response.status_code}")
            print(f"Response Reason: {response.reason}")
            print("Sleeping For 30 Sec...")
            time.sleep(30)

#4
def get_gameJson_by_matchID(matchId, REGION=REGION, API_KEY=API_KEY):
    base_url = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/{matchId}"
    real_url = base_url + '?api_key=' + API_KEY

    while True:
        game = requests.get(real_url)
        if game.status_code == 200:
            return game.json()
        else:
            print(f"Response Code: {game.status_code}")
            print(f"Response Reason: {game.reason}")
            print("Sleeping For 30 Sec...")
            time.sleep(30)

#5
def get_match_stats_by_matchID(matchId, puuid, REGION=REGION, API_KEY=API_KEY):
    base_url = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/{matchId}"
    real_url = base_url + '?api_key=' + API_KEY

    while True:
        response = requests.get(real_url)
        if response.status_code == 200:
            match_data = response.json()
            info = match_data.get('info', {})
        
            for p in info.get('participants', []):
                if p['puuid'] == puuid:
                    return {
                        'champion': p['championName'],
                        'role': p.get('teamPosition', ''),
                        'kills': p['kills'],
                        'deaths': p['deaths'],
                        'assists': p['assists'],
                        'gold_earned': p['goldEarned'],
                        'cs': p['totalMinionsKilled'] + p['totalEnemyJungleMinionsKilled'],
                        'win': p['win']
                    }
        else:
            print(f"Response Code: {response.status_code}")
            print(f"Response Reason: {response.reason}")
            print("Sleeping For 30 Sec...")
            time.sleep(30)
    return None  

#6
def write_to_csv(filename, data, append=True):
    mode = 'a' if append else 'w' 
    with open(filename, mode, newline='') as file:
        writer = csv.writer(file)
        if filename == "winners":
            writer.writerow([data])
            return
        for player_stats in data:
            player_kda = round(player_stats.get('player_kda_overall', 0), 2)
            player_wr = round(player_stats.get('player_wr_overall', 0), 2)
            writer.writerow([player_kda, player_wr])

#7
def convert_team_statistics(match_statistics):
    blue_team_stats, red_team_stats = match_statistics

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    df = pd.DataFrame(blue_team_stats + red_team_stats)

    df = df.apply(lambda x: x.astype(object).fillna(0) if x.isna().any() else x)

    return df

#8
def show_dataframe(df):
    df = df.apply(lambda x: x.astype(object).fillna(0) if x.isna().any() else x)

    root = tk.Tk()
    root.title("Match Statistics")

    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)

    pt = Table(frame, dataframe=df, showtoolbar=True, showstatusbar=True)
    pt.show()

    root.mainloop()

#9
def load_team_stats(file_path):
    """
    Reads a CSV file and returns data as a 2D list where each sublist contains 5 players' statistics.

    Parameters:
        file_path (str): Path to the CSV file.

    Returns:
        list: 2D list where each inner list contains 5 player statistics.
    """
    team_stats = []
    with open(file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        # next(reader)  # Skip header row if needed
        current_team = []

        for row in reader:
            current_team.append([float(stat) for stat in row])  
            if len(current_team) == 5:
                team_stats.append(current_team)
                current_team = []

    return team_stats

#10
def load_winners(file_path):
    """
    Reads CSV file and returns list of numbers
    """
    winners = []
    with open(file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        # next(reader)  # Uncomment if the first row is a header

        for row in reader:
            try:
                winners.append(int(row[0]))
            except:
                print("Error While Appending Winner To File")

    return winners
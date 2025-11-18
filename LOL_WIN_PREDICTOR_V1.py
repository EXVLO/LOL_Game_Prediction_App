from decimal import DivisionByZero
import requests
import pandas as pd
from collections import defaultdict
import tkinter as tk
from pandastable import Table
import sqlite3
import os
import csv
import warnings
import joblib

from sklearn.exceptions import InconsistentVersionWarning

from colorama import Fore, Style, init
init()

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

from shared import API_KEY, REGION, base_url
from LVL2 import get_match_history_by_username_tagline, process_match_by_ID, write_stats_to_csv, show_team_data, load_stats_from_csv
from LVL3 import process_matches, test_train_model1, test_train_model2, predict_winner, test_train_model3, predict_win_prob

# ========= #
# MAIN CODE #
# ========= #

""" Get Match History """
#match_history = get_match_history_by_username_tagline("Kszn", "EUNE", start=0, count=20)

""" Process Match By Id """
#players_data = process_match_by_ID(match_history[0])

#team1_data = players_data[0]
#team2_data = players_data[1]

#team1 = [list(player.values()) for player in team1_data]
#team2 = [list(player.values()) for player in team2_data]

""" Write Stats To CSV """
#write_stats_to_csv(players_data)

"""Show Team Data"""
#show_team_data(players_data)



# ======= #
# CODE #1 #
# ======= #


"""Process Matches And Write In CSV File"""
# process_matches("Silentworm", "EUNE", start=0, count=50) Already Done!

"""Load Stats From CSV File"""
team1, team2, winners = load_stats_from_csv("team1", "team2", "winners")

# test_train_model3(team1, team2, winners)


# ============ #
# TEST MACHINE #
# ============ #
"""Test Accuracy On All Matches"""
# correct = 0
# match_count = len(winners)
# for i in range (match_count):
#     test_match = predict_winner(team1[i], team2[i])
#     print(f"Predicted Winner: {test_match}")
#     print(f"Real Winner: {winners[i] // 200}")
#     if winners[i] // 200 == test_match:
#         print(Fore.GREEN + 'CORRECT')
#         print(Style.RESET_ALL)
#         correct += 1
#     else:
#         print(Fore.RED + 'INCORRECT')
#         print(Style.RESET_ALL)
#     print("--------------------------")
# print()
# print(f"Machine Guessed: {correct}/{match_count}")
# print(f"Accuracy: {float(correct / match_count)}")

"""Test Accuracy 2"""
correct = 0
match_count = len(winners)
for i in range (match_count):
    test_match = predict_win_prob("model.pkl", team1[i], team2[i])
    print(f"Probabilities:")
    print(f"Team1: {test_match['Team1'] * 100:.2f}%")
    print(f"Team2: {test_match['Team2'] * 100:.2f}%")
    AI_Winner = 0 if test_match['Team1'] >= test_match['Team2'] else 1
    print(f"Real Winner: Team{winners[i] // 200 + 1}")
    if winners[i] // 200 == AI_Winner:
        print(Fore.GREEN + 'CORRECT')
        print(Style.RESET_ALL)
        correct += 1
    else:
        print(Fore.RED + 'INCORRECT')
        print(Style.RESET_ALL)
    print("--------------------------")
print()
print(f"Machine Guessed: {correct}/{match_count}")
print(f"Accuracy: {float(correct / match_count)}")


"""Test Accuracy On Single Match"""
# num = 7

# print("Team1:")
# print(team1[num])
# print()
# print("Team2:")
# print(team2[num])
# print()
# test_match = predict_winner(team1[num], team2[num])
# print(f"Predicted Winner: {test_match}")
# print(f"Real Winner: {winners[num] // 200}")
# if winners[num] // 200 == test_match:
#     print(Fore.GREEN + 'CORRECT')
#     print(Style.RESET_ALL)
# else:
#     print(Fore.RED + 'INCORRECT')
#     print(Style.RESET_ALL)
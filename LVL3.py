from decimal import DivisionByZero
import requests
import pandas as pd
from collections import defaultdict
import tkinter as tk
from pandastable import Table
import sqlite3
import os
import csv
from colorama import Fore, Style, init
init()

import numpy as np
from sklearn.linear_model import SGDClassifier 
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, log_loss
import joblib
import xgboost as xgb

from shared import API_KEY, REGION, base_url
from LVL1 import ( get_puuid_by_username_tagline, get_username_tagline_by_puuid, get_match_history_by_puuid,
                    get_gameJson_by_matchID, get_match_stats_by_matchID, write_to_csv,
                    convert_team_statistics, show_dataframe, load_team_stats, load_winners )
from LVL2 import get_match_history_by_username_tagline, process_match_by_ID, write_stats_to_csv


def process_matches(username, tagline,  start=0, count=20, count_matches=10, REGION=REGION, API_KEY=API_KEY):
    """ Get Match History """
    match_history = get_match_history_by_username_tagline(username, tagline, start, count)

    i = 1
    for match in match_history:
        print(Fore.CYAN + f"Match #{i}")
        print(Style.RESET_ALL)
        i += 1

        """ Process Match By Id """
        players_data = process_match_by_ID(match)
        if players_data == -120:
            i -= 1
            print("Skipping...")
            print(Fore.RED + "-------------------------------------")
            print(Style.RESET_ALL)
            continue

        """ Write Stats To CSV """
        write_stats_to_csv(players_data)

        print("Finished")
        print(Fore.YELLOW + "-------------------------------------")
        print(Style.RESET_ALL)

    print()
    print ("Finished...")

def extract_features(team1, team2):
    """
    team1, team2: shape (n_matches, 5, 2)
    Returns: (n_matches, 8) features
    Features:
    - Team1 avg x, avg y
    - Team2 avg x, avg y
    - Team1 sum x, sum y
    - Difference of team avg x, y
    """
    team1 = np.array(team1)
    team2 = np.array(team2)

    team1_avg = np.mean(team1, axis=1)  # shape: (n_matches, 2)
    team2_avg = np.mean(team2, axis=1)

    team1_sum = np.sum(team1, axis=1)
    team2_sum = np.sum(team2, axis=1)

    avg_diff = team1_avg - team2_avg  # shape: (n_matches, 2)

    # Final feature vector: 8 features
    features = np.hstack([
        team1_avg,          # 2
        team2_avg,          # 2
        team1_sum,          # 2
        avg_diff            # 2
    ])
    return features

def predict_winner(team1_stats, team2_stats, model_file="model.pkl"):
    if os.path.exists(model_file):
        model = joblib.load(model_file)
        # print("Loaded Existing Model...")
    else:
        print("No Model Found...")
        return -1
    team1_flat = np.array(team1_stats).reshape(1, -1)  # (1,10)
    team2_flat = np.array(team2_stats).reshape(1, -1)  # (1,10)
    input_data = np.hstack((team1_flat, team2_flat))  # (1,20)
    
    prediction = model.predict(input_data)[0]
    return prediction 

def test_train_model1(team1, team2, winners, model_file="model.pkl"):
    team1 = np.array(team1)
    team2 = np.array(team2)
    winners = np.array(winners)

    team1_flat = team1.reshape(len(team1), -1)  # Shape: (n_matches, 10)
    team2_flat = team2.reshape(len(team2), -1)  # Shape: (n_matches, 10)
    X = np.hstack((team1_flat, team2_flat))  # Shape: (n_matches, 20)
    y = winners  # Labels (100 or 200)

    # Check if a trained model already exists
    if os.path.exists(model_file):
        model = joblib.load(model_file)
        print("Loaded existing model. Continuing training...")
    else:
        print("Training new model...")
        

    # Train or continue training
    model.partial_fit(X, y, classes=[100, 200]) 

    joblib.dump(model, model_file)
    print("Model updated and saved!")

    return model

def test_train_model2(team1, team2, winners, model_file="model.pkl"):
    team1 = np.array(team1)  # Shape: (n_matches, 5, 2)
    team2 = np.array(team2)  # Shape: (n_matches, 5, 2)
    winners = np.array(winners)
    
    team1_flat = team1.reshape(len(team1), -1)  # Shape: (n_matches, 10)
    team2_flat = team2.reshape(len(team2), -1)  # Shape: (n_matches, 10)
    X = np.hstack((team1_flat, team2_flat))  # Shape: (n_matches, 20)
    y = np.where(winners == 100, 0, 1)  # Convert labels: Team 100 -> 0, Team 200 -> 1
    
    # Check if a trained model already exists
    if os.path.exists(model_file):
        model = joblib.load(model_file)
        print("Loaded existing model. Continuing training...")
    else:
        print("Training new model...")
        model = xgb.XGBClassifier(
            objective='binary:logistic', 
            n_estimators=100, 
            learning_rate=0.1, 
            max_depth=5, 
            use_label_encoder=False, 
            eval_metric='logloss'
        )
    
    # Train or continue training
    model.fit(X, y, eval_set=[(X, y)], verbose=True)
    
    joblib.dump(model, model_file)
    print("Model updated and saved!")
    
    return model

def test_train_model3(team1, team2, winners, model_file="model.pkl"):
    team1 = np.array(team1)  # shape: (n_matches, 5, 2)
    team2 = np.array(team2)  # shape: (n_matches, 5, 2)
    winners = np.array(winners)

    # Extract features
    X = extract_features(team1, team2)
    y = np.where(winners == 100, 0, 1)  # 0 = Team1 win, 1 = Team2 win

    # Split for evaluation
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # Load or initialize model
    if os.path.exists(model_file):
        model = joblib.load(model_file)
        print("Loaded existing model. Continuing training...")
    else:
        print("Training new model...")
        # Initialize and calibrate model to improve probability estimation
        base_model = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42, class_weight='balanced')
        model = CalibratedClassifierCV(estimator=base_model, method='sigmoid')

    # Train model
    model.fit(X_train, y_train)

    # Save model
    joblib.dump(model, model_file)
    print("Model updated and saved.")

    # Evaluate
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)
    print("Accuracy:", accuracy_score(y_test, preds))
    print("Log Loss:", log_loss(y_test, probs))

    return model

def predict_win_prob(model_or_path, team1, team2):

    model = joblib.load(model_or_path)

    team1 = np.array(team1).reshape(1, 5, 2)
    team2 = np.array(team2).reshape(1, 5, 2)
    X = extract_features(team1, team2)
    probs = model.predict_proba(X)[0]
    return {"Team1": probs[0], "Team2": probs[1]}
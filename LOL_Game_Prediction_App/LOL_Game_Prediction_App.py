import requests

API_KEY = "My Key"
REGION = "eun1"  # Change based on the server (e.g., na1, kr, etc.)

def get_summoner_stats(username):
    base_url = f"https://{REGION}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{username}"
    headers = {"X-Riot-Token": API_KEY}

    response = requests.get(base_url, headers=headers)
    print(response.status_code, response.text)  # Debugging line

    if response.status_code == 200:
        data = response.json()
        summoner_id = data["id"]

        ranked_url = f"https://{REGION}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"
        ranked_response = requests.get(ranked_url, headers=headers)
        
        if ranked_response.status_code == 200:
            ranked_data = ranked_response.json()
            return {
                "Summoner Name": data["name"],
                "Level": data["summonerLevel"],
                "Ranked Stats": ranked_data
            }
        else:
            return {"error": "Failed to fetch ranked stats"}
    else:
        return {"error": "Summoner not found or invalid API key"}

# Example usage
username = "EXVLOO"
stats = get_summoner_stats(username)
print(stats)


import pandas as pd
from nhlpy import NHLClient
client = NHLClient()

#Get all the play by data which is a dict and we only want to focus on the key "plays"
play_by_play = client.game_center.play_by_play(game_id="2025020737")

#normalize plays column so that you only have a df of plays which was a nested dict
plays_df = pd.json_normalize(play_by_play["plays"])
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
#print(plays_df["typeDescKey"])
# cols = plays_df.columns.tolist()
# print(cols)

#get each player id for goals
goals = plays_df[plays_df["typeDescKey"] == "goal"]
goal_scorers = goals["details.scoringPlayerId"].dropna()


#get each player id for shots on goal
shots = plays_df[plays_df["typeDescKey"].isin(["shot-on-goal", "goal"])]
shooters = shots["details.shootingPlayerId"].dropna()


#get each player id for a hit
hits = plays_df[plays_df["typeDescKey"] == "hit"]
hitters = hits["details.hittingPlayerId"].dropna()


#get each player id for a blocked shot
blocks = plays_df[plays_df["typeDescKey"] == "blocked-shot"]
blockers = blocks["details.blockingPlayerId"].dropna()


#get each player id for a penalty
penalties = plays_df[plays_df["typeDescKey"] == "penalty"]
penalty_taker = penalties["details.committedByPlayerId"].dropna()
penalty_drawer = penalties["details.drawnByPlayerId"].dropna()


#get each player id for assists 
primary_assists= goals["details.assist1PlayerId"].dropna()
secondary_assists = goals["details.assist2PlayerId"].dropna()
assists = pd.concat([primary_assists, secondary_assists])

#get player id for faceoffs
faceoffs = plays_df[plays_df["typeDescKey"] == "faceoff"]
faceoff_winner = faceoffs["details.winningPlayerId"].dropna()
faceoff_loser = faceoffs["details.losingPlayerId"].dropna()

#Make dataframes for each stat 
goals_df = goal_scorers.value_counts().rename("goals").reset_index()

assists_df = assists.value_counts().rename("assists").reset_index()
assists_df.rename(columns={"index": "playerId"}, inplace=True)


shots_df = shooters.value_counts().rename("shots").reset_index()


hits_df = hitters.value_counts().rename("hits").reset_index()


blocks_df = blockers.value_counts().rename("blocks").reset_index()


penalties_taken_df = penalty_taker.value_counts().rename("Penalties Taken").reset_index()
penalties_drawn_df = penalty_drawer.value_counts().rename("Penalties Drawn").reset_index()

faceoffs_won_df = faceoff_winner.value_counts().rename("Faceoff Wins").reset_index()
faceoffs_lost_df = faceoff_loser.value_counts().rename("Faceoff Losses").reset_index()




goals_df = goals_df.rename(columns={"details.scoringPlayerId": "playerId"})
shots_df = shots_df.rename(columns={"details.shootingPlayerId": "playerId"})
hits_df = hits_df.rename(columns={"details.hittingPlayerId": "playerId"})
blocks_df = blocks_df.rename(columns={"details.blockingPlayerId": "playerId"})
faceoffs_won_df = faceoffs_won_df.rename(columns={"details.winningPlayerId": "playerId"})
faceoffs_lost_df = faceoffs_lost_df.rename(columns={"details.losingPlayerId": "playerId"})
penalties_taken_df = penalties_taken_df.rename(columns={"details.committedByPlayerId": "playerId"})
penalties_drawn_df = penalties_drawn_df.rename(columns={"details.drawnByPlayerId": "playerId"})

#Make boxscore
boxscore = goals_df

for df in [assists_df, shots_df, hits_df, blocks_df, faceoffs_won_df, faceoffs_lost_df, penalties_taken_df, penalties_drawn_df]:
    boxscore = boxscore.merge(df, on="playerId", how="outer")

boxscore = boxscore.fillna(0)
boxscore["points"] = boxscore["goals"] + boxscore["assists"]
f_taken = boxscore["Faceoff Wins"] + boxscore["Faceoff Losses"]
boxscore["Faceoffs Taken"] = f_taken
boxscore["Faceoff Percentage"] = boxscore["Faceoff Wins"] / f_taken.replace(0, pd.NA)
#print(boxscore)


pid_list = boxscore["playerId"].tolist()
player_names = {}
player_teams = {}

for pid in pid_list:
    career_stats = client.stats.player_career_stats(player_id=int(pid))
    first_name = career_stats["firstName"]["default"]
    last_name = career_stats["lastName"]["default"]
    full_name = f"{first_name} {last_name}"
    player_names[pid] = full_name
    
    # Get current team abbreviation
    team_abbrev = career_stats["currentTeamAbbrev"]
    player_teams[pid] = team_abbrev

# Add player names and teams to boxscore
boxscore['Name'] = boxscore['playerId'].map(player_names)
boxscore['Team'] = boxscore['playerId'].map(player_teams)

boxscore.insert(0, 'Name', boxscore.pop('Name'))
boxscore.insert(1, 'Team', boxscore.pop('Team'))

boxscore = boxscore.sort_values(by='Team', ascending=False).reset_index(drop=True)
boxscore.to_csv('boxscore.csv', index=False)
#Below is another way to add player names and teams but it caused me problems and alos uses the boxscore.

# box = client.game_center.boxscore(game_id="2025020737")
# away_id = box["awayTeam"]["id"]
# home_id = box["homeTeam"]["id"]



# away_abbr = box["awayTeam"]["abbrev"]
# home_abbr = box["homeTeam"]["abbrev"]
# print(away_abbr, home_abbr)

# away_roster = client.teams.team_roster(team_abbr=away_abbr, season="20252026")
# home_roster = client.teams.team_roster(team_abbr=home_abbr, season="20252026")

# # Create away players dataframe
# away_players = pd.DataFrame(away_roster['forwards'] + away_roster['defensemen'] + away_roster['goalies'])
# away_players['playerId'] = away_players['id']
# away_players['playerName'] = away_players['firstName'].apply(lambda x: x['default']) + " " + away_players['lastName'].apply(lambda x: x['default'])
# away_players['team'] = away_abbr
# away_players = away_players[['playerId', 'playerName', 'team']]

# # Create home players dataframe
# home_players = pd.DataFrame(home_roster['forwards'] + home_roster['defensemen'] + home_roster['goalies'])
# home_players['playerId'] = home_players['id']
# home_players['playerName'] = home_players['firstName'].apply(lambda x: x['default']) + " " + home_players['lastName'].apply(lambda x: x['default'])
# home_players['team'] = home_abbr
# home_players = home_players[['playerId', 'playerName', 'team']]

# # Combine both rosters
# all_players = pd.concat([away_players, home_players], ignore_index=True)

# # Merge boxscore with player info
# boxscore = all_players.merge(boxscore, on="playerId", how="left")
# boxscore = boxscore.fillna(0)

# boxscore.to_csv('boxscore.csv', index=False)
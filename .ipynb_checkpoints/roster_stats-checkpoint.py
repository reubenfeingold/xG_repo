import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from nhlpy import NHLClient


client = NHLClient()
teams = client.teams.teams()
roster = client.teams.team_roster(team_abbr="NYR", season="20242025")
forwards_df = pd.DataFrame(roster['forwards'])
defense_df = pd.DataFrame(roster['defensemen'])
goalies_df = pd.DataFrame(roster['goalies'])

forwards_df['position_group'] = 'F'
defense_df['position_group'] = 'D'
goalies_df['position_group'] = 'G'

roster_df = pd.concat(
    [forwards_df, defense_df, goalies_df],
    ignore_index=True
)
pd.set_option('display.max_columns', None)

ids = roster_df["id"].tolist()
career_stats = []
for pid in ids:
    career_stats.append(client.stats.player_career_stats(pid))

stats_df = pd.DataFrame(career_stats)
print(stats_df)


print("All good!")
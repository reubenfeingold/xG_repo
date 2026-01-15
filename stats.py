import pandas as pd
from nhlpy import NHLClient

client = NHLClient()

all_rows = []

for franchise_id in range(1, 33):
    skater_stats = client.stats.skater_stats_summary(
        start_season="20232024",
        end_season="20232024",
        franchise_id=str(franchise_id)
    )

    # skater_stats might be:
    # - a dict with a list inside, or
    # - already a list of dicts
    # So we normalize robustly:
    if isinstance(skater_stats, dict):
        # try common keys that hold the "rows"
        for key in ["data", "items", "results", "skaters", "skaterStats"]:
            if key in skater_stats and isinstance(skater_stats[key], list):
                rows = skater_stats[key]
                break
        else:
            # if it’s a dict but not a "dict with a list", treat it as one row
            rows = [skater_stats]
    else:
        rows = skater_stats  # assume list of dicts

    # add franchise_id so you don’t lose where it came from
    for r in rows:
        r["franchise_id"] = franchise_id

    all_rows.extend(rows)

all_skaters = pd.json_normalize(all_rows)

# show everything (optional)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)

#print(all_skaters.head())
#print("Rows:", len(all_skaters), "Cols:", all_skaters.shape[1])
print(type(all_skaters))
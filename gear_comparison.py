"""
Most common gear on the pole lap, for every 2025 race and every 2026 race so far.
"""

import os
import fastf1
import pandas as pd

YEARS = [2025, 2026]
OUTPUT_FILE = "datasets/pole_gear_by_track.csv"

cache_dir = "fastf1_cache"
os.makedirs(cache_dir, exist_ok=True)
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
fastf1.Cache.enable_cache(cache_dir)

now = pd.Timestamp.now(tz="UTC").tz_localize(None)
rows = []

for year in YEARS:

    print(f"\n========== {year} ==========")

    schedule = fastf1.get_event_schedule(year, include_testing=False)

    # Only events whose qualifying has already happened (all of 2025, part of 2026)
    schedule = schedule[schedule["Session4DateUtc"] < now]

    for _, event in schedule.iterrows():

        race = event["EventName"]
        print(f"Loading {year} {race} Qualifying...")

        try:
            session = fastf1.get_session(year, race, "Q")
            session.load(telemetry=True, weather=False, messages=False)

            pole_driver = session.results.iloc[0]["Abbreviation"]
            pole_lap = session.laps.pick_drivers(pole_driver).pick_fastest()

            gears = pole_lap.get_car_data()["nGear"]
            top_gear = int(gears.mode().iloc[0])
            pct = round((gears == top_gear).mean() * 100, 1)

        except fastf1.exceptions.RateLimitExceededError:
            print("Rate limit hit. Stopping.")
            break

        except Exception as e:
            print(f"Skipped: {e}")
            continue

        rows.append({
            "Year": year,
            "Round": event["RoundNumber"],
            "Race": race,
            "PoleDriver": pole_driver,
            "MostCommonGear": top_gear,
            "PctInGear": pct,
        })

result = pd.DataFrame(rows)
result.to_csv(OUTPUT_FILE, index=False)

print()
print(result.to_string(index=False))
print(f"\nSaved to {OUTPUT_FILE}")
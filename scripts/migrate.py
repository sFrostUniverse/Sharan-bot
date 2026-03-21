import json
from data.twitch_db import TwitchDatabase

db = TwitchDatabase()

with open("data/points.json", "r") as f:
    data = json.load(f)

points = data.get("points", {})

for user, pts in points.items():
    db.add_points(user, pts)

print("✅ Migration complete")
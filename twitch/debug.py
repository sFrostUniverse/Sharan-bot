import requests

TOKEN = "4xrz2ues3runzdzihih7menzsvpumn"

r = requests.get(
    "https://id.twitch.tv/oauth2/validate",
    headers={"Authorization": f"OAuth {TOKEN}"}
)

print(r.json())
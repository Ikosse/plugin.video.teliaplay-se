import json
import requests


#hash_url = "https://github.com/Ikosse/plugin.video.teliaplay-se/blob/master/resources/lib/hashes.json"
#
#
#graphql_hashes = requests.get(hash_url)

with open("graphql_hashes.json") as file:
    graphql_hashes = json.load(file)

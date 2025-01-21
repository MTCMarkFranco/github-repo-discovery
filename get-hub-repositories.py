import os
import json
import requests
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime

class RepoInfo:
    def __init__(self, owner, name, url, avatar_url,archived):
        self.owner = owner
        self.name = name
        self.url = url
        self.pic = avatar_url
        self.archived = archived

# Load environment variables from .env file
load_dotenv()

# Globals
repo_info_list = []
TOKEN =  os.getenv('GITHUB_TOKEN')
TEAMS_WEBHOOK =  os.getenv('TEAMS_WEBHOOK')

# Search for Hub (MTC) Microsoft repositories
SEARCH_QUERY = 'MTC_ in:name org:microsoft'
URL = f'https://api.github.com/search/repositories?q={SEARCH_QUERY}'

headers = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

# 1. Perform the search
response = requests.get(URL, headers=headers)

if response.status_code == 200:
    data = response.json()
    repositories = data.get('items', [])
    for repo in repositories:
        repo_info_list.append(
        RepoInfo(
            name=repo['name'],
            url=repo['html_url'],
            avatar_url=repo['owner']['avatar_url'],
            owner=repo['owner']['login'],
            archived=repo['archived']
        )
    )
    print("finished fetching repositories!")

else:
    print(f"Failed to fetch repositories [error]: {response.status_code}")


# 2. Send the data to Teams

# Load the adaptive card template from a file
with open('./templates/adaptive_card_template.json', 'r') as file:
    card = json.load(file)
    adaptiveCard = card

# Process search results in batches of 10 (To keep Adaptive card size below 28k)
batch_size = 10
for i in range(0, len(repo_info_list), batch_size):
    batch = repo_info_list[i:i + batch_size]
    
    # Create a new adaptive card for each batch
    adaptiveCard["body"][0]["rows"] = adaptiveCard["body"][0]["rows"][:1]
    
    # Add the data rows to the adaptive card
    for item in batch:
        adaptiveCard["body"][0]["rows"].append({
            "type": "TableRow",
            "cells": [
                {
                    "type": "TableCell",
                    "items": [
                        {
                            "type": "Image",
                            "url": f"{item.pic}",
                            "size": "Small",
                            "style": "Person"
                        },
                        {
                            "type": "TextBlock",
                            "text": f"{item.owner}",
                            "wrap": True
                        }
                    ]
                },
                {
                    "type": "TableCell",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": f"{item.name}",
                            "wrap": True,
                            "size": "small"
                        },
                        {
                            "type": "TextBlock",
                            "text": f"ARCHIVED",
                            "wrap": True,
                            "$when": f"{item.archived}",
                            "color": "Attention"
                        },
                        {
                            "type": "TextBlock",
                            "text": f"Last Checked: {datetime.now().strftime("%d/%m/%d/%y")}",
                            "wrap": True
                            
                        }
                    ]
                },
                {
                    "type": "TableCell",
                    "items": [
                        {
                            "type": "ActionSet",
                            "actions": [
                                {
                                    "type": "Action.OpenUrl",
                                    "title": "...",
                                    "url": f"{item.url}"
                                }
                            ]
                        }
                    ]
                }
            ]
        })
    
    # Send each adaptive card to Teams
    payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": adaptiveCard,
                "summary": "Outstanding Repositories"
            }
        ]
    }
    
    response = requests.post(TEAMS_WEBHOOK, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
    if response.status_code == 200:
        print(f"Finished sending message to Teams for batch starting at index {i}...")
    else:
        print(f"Failed to send message to Teams for batch starting at index {i}: {response.status_code} - {response.text}")

print("Finished sending all messages to Teams!")
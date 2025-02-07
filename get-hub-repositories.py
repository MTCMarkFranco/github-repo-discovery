import os
import json
import requests
import subprocess
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime
from colorama import Fore, Style

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
    print(Fore.BLUE + "finished fetching repositories!" + Style.RESET_ALL)

else:
    print(f"Failed to fetch repositories [error]: {response.status_code}")

# Create the directory if it doesn't exist
backup_dir = 'f:/projects/mtc_Backup_repos'
if not os.path.exists(backup_dir):
    os.makedirs(backup_dir)

# Change to the backup directory
os.chdir(backup_dir)

# Process search results in batches of 10 (To keep Adaptive card size below 28k)

for item in repo_info_list:
    
    DELETE_URL = f'https://api.github.com/repos/microsoft/{item.name}'
    
    print(f"Deleting repository: {item.url}")
    
    response_delete = requests.delete(DELETE_URL, headers=headers)

    if (response_delete.status_code == 404):
        print(Fore.WHITE + f"Repo: {item.name} Already Deleted." + Style.RESET_ALL)
    
    if (response_delete.status_code == 403):
        print(Fore.CYAN + f"Repo: {item.name} MUST HAVE ADMIN RIGHTS" + Style.RESET_ALL)
        
    if response_delete.status_code == 204:
        
        if (response_delete.reason == 'No Content'):
            print(Fore.WHITE + f"Repo: {item.name} Already Deleted." + Style.RESET_ALL)
        else:
            print(Fore.GREEN + f"Repo: {item.name} deleted successfully" + Style.RESET_ALL)

        print(Fore.GREEN + "finished deleting repository!" + Style.RESET_ALL)

    else:
        print(Fore.RED + f"Repo: {item.name} not deleted" + Style.RESET_ALL)
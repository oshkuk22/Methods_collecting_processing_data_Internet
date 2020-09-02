import requests
import json


link_api = 'https://api.github.com'
user = 'oshkuk22'


get_ = requests.get(f'{link_api}/users/{user}/repos')
info_about_repos = get_.json()

for i in info_about_repos:
    print(i['name'])

with open('repos.json', 'w') as file_repo:
    json.dump(info_about_repos, file_repo)

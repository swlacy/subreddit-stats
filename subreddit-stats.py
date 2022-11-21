#!/usr/bin/env python3

from requests import get
from json import loads
from datetime import datetime

BASE_URL = 'https://reddit.com/subreddits/new.json?limit=100'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
}
TIMEOUT = 10
MAX_DESC_LEN = 120
OUT_FILE = f'./{datetime.today().strftime("%Y-%m-%d.%H:%M:%S")}.out.csv'

def main():
    # Open the output file (OUT_FILE); write CSV headers
    with open(OUT_FILE, 'w', encoding = 'utf-8') as file:
        file.write('Updated,Subreddit,Created,Subscribers,NSFW,Quarantined,Description\n')
    # Set the url to request, sans next ID on first run
    url = f'{BASE_URL}'
    # Record count tracker
    count = 0
    # This process takes a long time
    while True:
        #Fetch data for the first page of results
        response = loads(get(url, headers=HEADERS, timeout=TIMEOUT).text)
        for row in response['data']['children']:
            # Record update time
            updated = datetime.today().isoformat()
            # Fetch each element
            subreddit = row['data']['display_name']
            created = row['data']['created']
            subscribers = row['data']['subscribers']
            nsfw = row['data']['over18']
            quarantined = row['data']['quarantine']
            description = row['data']['public_description']
            # Format each element as needed
            created = datetime.fromtimestamp(created).isoformat()
            description = description.replace(",", "").replace("\n", "")
            # Truncate description lenth
            if len(description) > MAX_DESC_LEN:
                description = description[0:MAX_DESC_LEN - 1]
            if not description:
                description = '!NO_DESCRIPTION'
            # Form final record
            record = f'{updated},{subreddit},{created},{subscribers},{nsfw},{quarantined},{description}\n'
            # Skip record if it already exists
            with open(OUT_FILE, 'r', encoding = 'utf-8') as file:
                if f'{subreddit},{created}' in file.read():
                    # STDOUT log
                    print(f'[?] (#{count}@{updated}): skipping duplicate record for \'r/{subreddit}\'')
                    continue
            # Otherwise, record the result in OUT_FILE; increment counter
            with open(OUT_FILE, 'a', encoding = 'utf-8') as file:
                file.write(record)
                # STDOUT log; increment counter
                print(f'[+] (#{count}@{updated}): added record for \'r/{subreddit}\'')
                count += 1
        # Append the next page ID to the url for the next request
        url = f'{BASE_URL}&after={response["data"]["after"]}'
main()

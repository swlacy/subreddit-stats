#!/usr/bin/env python3

from requests import get
import json
from datetime import datetime

BASE_URL = 'https://reddit.com/subreddits/new.json?limit=100'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
}
TIMEOUT = 10
MAX_DESC_LEN = 120
OUT_CSV = f'./{datetime.today().strftime("%Y-%m-%d.%H:%M:%S")}.out.csv'

def main():
    # Write CSV headers
    with open(OUT_CSV, 'w', encoding = 'utf-8') as file:
        file.write('sub_name,sub_subs,sub_date,sub_type,sub_quar,sub_nsfw,sub_desc\n')
    # Set the url to request, sans next ID on first run
    url = f'{BASE_URL}'
    # Record count tracker
    count = 0
    while True:
        #Fetch the first page of results
        response = json.loads(get(url, headers=HEADERS, timeout=TIMEOUT).text)
        for sub_id in response['data']['children']:
            # Fetch each element
            sub_name = sub_id['data']['display_name']
            sub_subs = sub_id['data']['subscribers']
            sub_date = datetime.fromtimestamp(sub_id['data']['created']).date()
            sub_type = sub_id['data']['subreddit_type']
            sub_quar = sub_id['data']['quarantine']
            sub_nsfw = sub_id['data']['over18']
            sub_desc = sub_id['data']['public_description'].replace(",", "").replace("\n", "")
            # Truncate description lenth
            if len(sub_desc) > MAX_DESC_LEN - 1:
                sub_desc = sub_desc[0:MAX_DESC_LEN - 1] + '...'
            if not sub_desc:
                sub_desc = '<No description>'
            # Form final record
            record = f'{sub_name},{sub_subs},{sub_date},{sub_type},{sub_quar},{sub_nsfw},{sub_desc}\n'
            # Skip record if it already exists
            with open(OUT_CSV, 'r', encoding = 'utf-8') as file:
                if f'\n{sub_name}' in file.read():
                    # STDOUT log
                    print(f'[+{count}] ({datetime.now()}): skipping duplicate record for \'r/{sub_name}\'')
                    continue
            # Otherwise, record the result in OUT_CSV; increment counter
            with open(OUT_CSV, 'a', encoding = 'utf-8') as file:
                file.write(record)
                # STDOUT log; increment counter
                print(f'[+{count}] ({datetime.now()}): successfully recorded \'/r/{sub_name}\' (https://reddit.com/r/{sub_name})')
                count += 1
        # Append the next page ID to the url for the next request
        url = f'{BASE_URL}&after={response["data"]["after"]}'
main()

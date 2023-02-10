import json
import requests
from pymongo import MongoClient

# Connecting to MongoDB for storing the retrieved data
client = MongoClient('mongodb://localhost:27017/')
database = client.DataBase_Twitter
collection = database.Twitter

# Twitter Bearer token created using Developer Portal
bearertoken = ""

# Twitter API to collect data
url = "https://api.twitter.com/2/tweets/sample/stream"

# Twitter parameters that are used for data collection
parameters = {'tweet.fields': 'context_annotations,created_at,lang,public_metrics,entities',
              'expansions': 'author_id,attachments.media_keys', 'user.fields': 'id,name,username'}


def main():
    headers = {"Authorization": "Bearer {}".format(bearertoken)}
    resp = requests.request("GET", url, headers=headers,
                            stream=True, params=parameters)
    for respline in resp.iter_lines():
        if respline:
            jsonresp = json.loads(respline)

            # Context Annotations
            if jsonresp['data']['lang'] == 'en':
                if 'context_annotations' in jsonresp['data']:
                    for domains in jsonresp['data']['context_annotations']:
                        if domains['domain']['id'] in ['6', '11', '12', '26', '27', '28', '39', '40', '43', '44', '60', '68', '83', '92']:
                            data = {
                                'tweet_id': jsonresp['data']['id'],
                                'time_stamp': jsonresp['data']['created_at'],
                                'author_id': jsonresp['data']['author_id'],
                                'language': jsonresp['data']['lang'],
                                'text': jsonresp['data']['text'],
                                'context': domains['domain']['name']
                            }
                            # Media Data
                            if 'media' in jsonresp['includes']:
                                mediakeys = []
                                for item in jsonresp['includes']['media']:
                                    if 'media_key' in item:
                                        mediakeys.append(item['media_key'])
                                data['media_keys'] = mediakeys
                            else:
                                data['media_keys'] = None

                            database.Twitter.insert_one(data)
                            break

    if resp.status_code != 200:
        raise Exception("Error: {} {}".format(
            resp.status_code, resp.text))


if __name__ == "__main__":
    main()

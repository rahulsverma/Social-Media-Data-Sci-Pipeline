import json
import time
import pymongo
import logging
import requests
from datetime import datetime


logger = logging.getLogger(__name__)
FORMAT = "[%(lineno)s:%(funcName)s()] %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.DEBUG)

config_file_name = "config.json"

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient.DataBase_Reddit
mycol = mydb.Reddit


def initAPI(username, password, clientid, secret):
    data = {'grant_type': 'password',
            'username': username, 'password': password}
    authentication = requests.auth.HTTPBasicAuth(clientid, secret)
    res = requests.post('https://www.reddit.com/api/v1/access_token',
                        data=data, headers={'user-agent': username}, auth=authentication)
    token = 'bearer ' + res.json()['access_token']
    headers = {'Authorization': token, 'User-Agent': username}
    resp = requests.get(
        'https://oauth.reddit.com/api/v1/me', headers=headers)
    return resp, headers


def searchPosts(headers, name, after):
    resp = requests.get('https://oauth.reddit.com/r/' + str(name) +
                        '/new?limit=25&after=' + str(after), headers=headers)
    if resp.status_code == 200:
        reqs_left = int(float(resp.headers.get("x-ratelimit-remaining")))
        time_left = int(float(resp.headers.get("x-ratelimit-reset")))
        logger.debug(f"Reqs: {reqs_left} within Time: {time_left}")
        if reqs_left < 10 and time_left > reqs_left:
            logger.debug("Sleepy Time")
            time.sleep(time_left-reqs_left+10)
        return resp.json()
    else:
        return None


def processPosts(resp):
    with open(config_file_name, "r") as config_file:
        config = json.load(config_file)
    for item in resp['data']['children']:
        if not item['data']['archived']:
            if item['data']['id'] not in set(config["POST_IDS"]):
                config["POST_IDS"].append(item['data']['id'])
    with open(config_file_name, "w") as config_file:
        json.dump(config, config_file)
    return resp['data']['after']


def searchComments(headers, post):
    resp = requests.get('https://oauth.reddit.com/comments/' + str(post) +
                        '?sort=new&limit=500', headers=headers)
    if resp.status_code == 200:
        reqs_left = int(float(resp.headers.get("x-ratelimit-remaining")))
        time_left = int(float(resp.headers.get("x-ratelimit-reset")))
        logger.debug(f"Reqs: {reqs_left} within Time: {time_left}")
        if reqs_left < 10 and time_left > reqs_left:
            logger.debug("Sleepy Time")
            time.sleep(time_left-reqs_left+10)

        return resp.json()
    else:
        return None


def checkComment(item, post, more):
    if item["kind"] == "t1":
        with open(config_file_name, "r") as config_file:
            config = json.load(config_file)
        if item['data']['id'] not in set(config["CMNT_IDS"]):
            config["CMNT_IDS"].append(item['data']['id'])
            data = {'subreddit': item['data']['subreddit'],
                    'post_id': post,
                    'comment_id': item['data']['id'],
                    'text': item['data']['body'],
                    'author': item['data']['author'],
                    'score': item['data']['score'],
                    'time_stamp': datetime.utcfromtimestamp(int(item['data']['created_utc'])).isoformat() + 'Z',
                    'current_time': datetime.now().isoformat() + 'Z'
                    }
            mycol.insert_one(data)
            with open(config_file_name, "w") as config_file:
                json.dump(config, config_file)
        return 1

    elif item["kind"] == "more":
        if (item["data"]["count"] > 0):
            more.append(item["data"]["children"])
        return 0


def dfs(visited, item, post, more):
    if item['data']['id'] not in visited:
        flag = checkComment(item, post, more)
        visited.add(item['data']['id'])
        if flag:
            if item['data']['replies']:
                for nodes in item['data']['replies']['data']['children']:
                    dfs(visited, nodes, post, more)


def processComments(resp, post):
    more = []
    for item in resp['data']['children']:
        visited = set()
        dfs(visited, item, post, more)
    return more


def searchMoreChildren(headers, post, children):
    resp = requests.get('https://oauth.reddit.com/api/morechildren?link_id=t3_' + str(
        post) + '&children=' + children + '&limit_children=False&api_type=json', headers=headers)
    if resp.status_code == 200:
        reqs_left = int(float(resp.headers.get("x-ratelimit-remaining")))
        time_left = int(float(resp.headers.get("x-ratelimit-reset")))
        logger.debug(f"Reqs: {reqs_left} within Time: {time_left}")
        if reqs_left < 10 and time_left > reqs_left:
            logger.debug("Sleepy Time")
            time.sleep(time_left-reqs_left+10)

        return resp.json()
    else:
        return None


def processMoreComments(resp, post):
    more = []
    for item in resp['json']['data']['things']:
        visited = set()
        dfs(visited, item, post, more)
    return more


def main():
    with open(config_file_name, "r") as config_file:
        config = json.load(config_file)
    username = config["API_USERNAME"]
    password = config["API_PASSWORD"]
    clientid = config["API_CLIENTID"]
    secret = config["API_SECRET"]

    api_reponse, api_headers = initAPI(
        username, password, clientid, secret)

    subreddits = config["SUBREDDITS"]

    if api_reponse.status_code == 200:
        try:
            for i, name in enumerate(subreddits):
                after = None
                while True:
                    resp = searchPosts(
                        api_headers, name, after)
                    if resp:
                        after = processPosts(resp)
                        if not after:
                            with open(config_file_name, "r") as config_file:
                                config = json.load(config_file)
                            logger.debug(str(name) + ' ' +
                                         str(len(config["POST_IDS"])))
                            break
                    else:
                        break

            with open(config_file_name, "r") as config_file:
                config = json.load(config_file)
            posts = config["POST_IDS"]

            for a, post in enumerate(posts):
                resp = searchComments(api_headers, post)
                more = processComments(resp[1], post)
                while (len(more)):
                    item = more.pop(0)
                    proc = item[0:100]
                    children = ",".join(proc)
                    item = item[100:]
                    if len(item):
                        more.append(item)
                    resp = searchMoreChildren(api_headers, post, children)
                    evenmore = processMoreComments(resp, post)
                    if len(evenmore):
                        more += evenmore

        except Exception as e:
            logger.error(f"Error:\n{str(e)}")


while True:
    main()

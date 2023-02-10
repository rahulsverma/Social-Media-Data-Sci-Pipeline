import json
import time
import pymongo
import logging
import schedule
import googleapiclient.discovery
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
FORMAT = "[%(lineno)s:%(funcName)s()] %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.DEBUG)

config_file_name = "config.json"
no_new_video = 0
no_new_comment = 0
max_timestamp = "2022-01-01T00:00:00Z"

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient.DataBase_Youtube
mycol = mydb.Youtube


def initAPI(API_KEY):
    api_service_name = "youtube"
    api_version = "v3"
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=API_KEY)
    return youtube


def searchVideos(video_api, channel_id, page_token):
    request = video_api.channels().list(
        id=channel_id,
        part='contentDetails')
    response = request.execute()
    request = video_api.playlistItems().list(
        playlistId=response['items'][0]['contentDetails']['relatedPlaylists']['uploads'],
        part="snippet",
        pageToken=page_token,
        maxResults=50)
    response = request.execute()
    logger.debug("Received Video Search Request")
    return response


def searchComments(cmmnt_api, video_id, page_token):
    request = cmmnt_api.commentThreads().list(
        part="snippet, replies",
        videoId=video_id,
        pageToken=page_token,
        order="time",
        maxResults=100
    )
    logger.debug(f"Received comment Search Request for {video_id}")
    response = request.execute()
    return response


def processAllSearch(response, channel_id, date_upper_limit, ord):
    next_page_token = response.get('nextPageToken')
    for a, item in enumerate(response["items"]):
        video_id = item['snippet']['resourceId']['videoId']
        video_title = item['snippet']['title']
        video_timestamp = item['snippet']['publishedAt']
        with open(config_file_name, "r") as config_file:
            config = json.load(config_file)
        if video_timestamp <= date_upper_limit:
            if ord:
                config["VIDEO_IDS"][channel_id].append(
                    {'VIDEO_ID': video_id, 'VIDEO_TITLE': video_title, 'LATEST_TIMESTAMP': video_timestamp})
            else:
                config["VIDEO_IDS"][channel_id].insert(0,
                                                       {'VIDEO_ID': video_id, 'VIDEO_TITLE': video_title, 'LATEST_TIMESTAMP': video_timestamp})
        with open(config_file_name, "w") as config_file:
            json.dump(config, config_file)

    return next_page_token


def processLatestSearch(response, channel_id, date_upper_limit, i):
    result = []
    with open(config_file_name, "r") as config_file:
        config = json.load(config_file)
    if response["items"][-1]['snippet']['publishedAt'] > config["CHANNEL_IDS"][i]["LATEST_TIMESTAMP"]:
        response["items"] = reversed(response["items"])
        next_page_token = processAllSearch(
            response, channel_id, date_upper_limit, 0)
    else:
        if response["items"][0]['snippet']['publishedAt'] > config["CHANNEL_IDS"][i]["LATEST_TIMESTAMP"]:
            for a, item in enumerate(response["items"]):
                if item['snippet']['publishedAt'] > config["CHANNEL_IDS"][i]["LATEST_TIMESTAMP"] and item['snippet']['publishedAt'] <= date_upper_limit:
                    result.append(item)
                else:
                    continue
            if result:
                with open(config_file_name, "r") as config_file:
                    config = json.load(config_file)
                for item in reversed(result):
                    video_id = item['snippet']['resourceId']['videoId']
                    video_title = item['snippet']['title']
                    video_timestamp = item['snippet']['publishedAt']
                    config["VIDEO_IDS"][channel_id].insert(
                        0, {'VIDEO_ID': video_id, 'VIDEO_TITLE': video_title, 'LATEST_TIMESTAMP': video_timestamp})
                with open(config_file_name, "w") as config_file:
                    json.dump(config, config_file)
        else:
            global no_new_video
            no_new_video = 1
        next_page_token = None

    return next_page_token


def processLatestComments(response, video, date_lower_limit):
    result = []
    global max_timestamp
    if response["items"][-1]["snippet"]["topLevelComment"]["snippet"]["updatedAt"] > video["LATEST_TIMESTAMP"] and response["items"][-1]["snippet"]["topLevelComment"]["snippet"]["updatedAt"] >= date_lower_limit:
        next_page_token = response.get('nextPageToken')
        for a, item in enumerate(response["items"]):
            replies = []
            comment = item["snippet"]["topLevelComment"]
            author = comment["snippet"]["authorDisplayName"]
            comment_text = comment["snippet"]["textDisplay"]
            like_count = comment["snippet"]["likeCount"]
            comment_timestamp = comment["snippet"]["updatedAt"]
            if comment_timestamp > max_timestamp:
                max_timestamp = comment_timestamp
            replycount = item["snippet"]["totalReplyCount"]
            if replycount > 0:
                try:
                    for reply in item["replies"]["comments"]:
                        replies.append(reply)
                except:
                    replycount = 0
                    replies = []
            video_id = video['VIDEO_ID']
            video_title = video['VIDEO_TITLE']
            record = {
                'video_id': video_id,
                'video_title': video_title,
                'author': author,
                'comment_text': comment_text,
                'like_count': like_count,
                'reply_count': replycount,
                'comment_timestamp': comment_timestamp,
                'current_time': datetime.now().isoformat() + 'Z'
            }
            result.append(record)
            mycol.insert_one(record)
            if replycount > 0:
                for reply in replies:
                    author = reply["snippet"]["authorDisplayName"]
                    comment_text = reply["snippet"]["textDisplay"]
                    like_count = reply["snippet"]["likeCount"]
                    comment_timestamp = reply["snippet"]["updatedAt"]
                    record = {
                        'video_id': video_id,
                        'video_title': video_title,
                        'author': author,
                        'comment_text': comment_text,
                        'like_count': like_count,
                        'reply_count': 0,
                        'comment_timestamp': comment_timestamp,
                        'current_time': datetime.now().isoformat() + 'Z'
                    }
                    result.append(record)
                    mycol.insert_one(record)
    else:
        next_page_token = None
        if response["items"][0]["snippet"]["topLevelComment"]["snippet"]["updatedAt"] > video["LATEST_TIMESTAMP"]:
            for a, item in enumerate(response["items"]):
                if item["snippet"]["topLevelComment"]["snippet"]["updatedAt"] > video["LATEST_TIMESTAMP"] and item["snippet"]["topLevelComment"]["snippet"]["updatedAt"] >= date_lower_limit:
                    replies = []
                    comment = item["snippet"]["topLevelComment"]
                    author = comment["snippet"]["authorDisplayName"]
                    comment_text = comment["snippet"]["textDisplay"]
                    like_count = comment["snippet"]["likeCount"]
                    comment_timestamp = comment["snippet"]["updatedAt"]
                    if comment_timestamp > max_timestamp:
                        max_timestamp = comment_timestamp
                    replycount = item["snippet"]["totalReplyCount"]
                    if replycount > 0:
                        try:
                            for reply in item["replies"]["comments"]:
                                replies.append(reply)
                        except:
                            replycount = 0
                            replies = []
                    video_id = video['VIDEO_ID']
                    video_title = video['VIDEO_TITLE']
                    record = {
                        'video_id': video_id,
                        'video_title': video_title,
                        'author': author,
                        'comment_text': comment_text,
                        'like_count': like_count,
                        'reply_count': replycount,
                        'comment_timestamp': comment_timestamp,
                        'current_time': datetime.now().isoformat() + 'Z'
                    }
                    result.append(record)
                    mycol.insert_one(record)
                    if replycount > 0:
                        for reply in replies:
                            author = reply["snippet"]["authorDisplayName"]
                            comment_text = reply["snippet"]["textDisplay"]
                            like_count = reply["snippet"]["likeCount"]
                            comment_timestamp = reply["snippet"]["updatedAt"]
                            record = {
                                'video_id': video_id,
                                'video_title': video_title,
                                'author': author,
                                'comment_text': comment_text,
                                'like_count': like_count,
                                'reply_count': 0,
                                'comment_timestamp': comment_timestamp,
                                'current_time': datetime.now().isoformat() + 'Z'
                            }
                            result.append(record)
                            mycol.insert_one(record)
                else:
                    continue
        else:
            global no_new_comment
            no_new_comment = 1

    return next_page_token, result


def main():
    with open(config_file_name, "r") as config_file:
        config = json.load(config_file)
    video_api_key = config["VIDEO_API_KEY"]
    cmmnt_api_key = config["CMMNT_API_KEY"]
    channel_ids = config["CHANNEL_IDS"]

    video_api = initAPI(video_api_key)
    cmmnt_api = initAPI(cmmnt_api_key)

    for i, info in enumerate(channel_ids):
        videos = []
        comments = []
        channel_id = info["CHANNEL_ID"]
        try:
            date_upper_limit = (datetime(datetime.now().year, datetime.now(
            ).month, datetime.now().day, 23, 59, 59) - timedelta(days=3)).isoformat() + 'Z'
            if info["IS_NEW"]:
                next_page = None
                while True:
                    response = searchVideos(video_api, channel_id, next_page)
                    next_page = processAllSearch(
                        response, channel_id, date_upper_limit,  1)
                    if not next_page:
                        with open(config_file_name, "r") as config_file:
                            config = json.load(config_file)
                        config["CHANNEL_IDS"][i]["IS_NEW"] = 0
                        config["CHANNEL_IDS"][i]["LATEST_TIMESTAMP"] = date_upper_limit
                        with open(config_file_name, "w") as config_file:
                            json.dump(config, config_file)
                        break
            else:
                next_page = None
                global no_new_video
                while True:
                    try:
                        response = searchVideos(video_api, channel_id, next_page)
                    except:
                        logger.debug("API Issue")
                        break
                    time.sleep(0.5)
                    next_page = processLatestSearch(
                        response, channel_id, date_upper_limit, i)
                    if not next_page:
                        if not no_new_video:
                            with open(config_file_name, "r") as config_file:
                                config = json.load(config_file)
                            config["CHANNEL_IDS"][i]["LATEST_TIMESTAMP"] = date_upper_limit
                            with open(config_file_name, "w") as config_file:
                                json.dump(config, config_file)
                        else:
                            no_new_video = 0
                        break

            with open(config_file_name, "r") as config_file:
                config = json.load(config_file)
            videos = config["VIDEO_IDS"][channel_id]

            date_lower_limit = datetime(
                2022, 10, 1, 0, 0, 0).isoformat() + 'Z'

            for a, video in enumerate(videos):
                next_page = None
                global no_new_comment
                while True:
                    try:
                        response = searchComments(
                            cmmnt_api, video['VIDEO_ID'], next_page)
                    except Exception as e:
                        logger.debug("Video Comments Disabled or API Issue")
                        break
                    time.sleep(0.5)
                    next_page, result = processLatestComments(
                        response, video, date_lower_limit)
                    comments += result
                    if not next_page:
                        if not no_new_comment:
                            global max_timestamp
                            with open(config_file_name, "r") as config_file:
                                config = json.load(config_file)
                            config["VIDEO_IDS"][channel_id][a]["LATEST_TIMESTAMP"] = max_timestamp
                            with open(config_file_name, "w") as config_file:
                                json.dump(config, config_file)
                        else:
                            no_new_comment = 0
                        max_timestamp = "2022-01-01T00:00:00Z"
                        break

        except Exception as e:
            logger.error(f"Error:\n{str(e)}")
        print(f"Total comments: {len(comments)}")
        print(f"Total videos: {len(videos)}")


schedule.every().day.at("09:00:00").do(main)

while True:
    schedule.run_pending()
    time.sleep(500)

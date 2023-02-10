## Project Abstract

Social media platforms are proven to be a good source of data for scientific analysis and for training various machine learning models. We present implementation of 3 data collection systems that collects real time tweets data from Twitter, comments on the posts from the specified subreddit and comments on all the videos from the specified YouTube channel. All the systems are implemented using Python programming language and designed to continuously collect the data and store it in a database.

## Team - data-worthy

* Arjun Mahadkar, amahadk1@binghamton.edu
* Deepang Raval, draval1@binghamton.edu
* Rahul Verma, rverma4@binghamton.edu
* Sudeep Rawat, srawat1@binghamton.edu
* Yuraj Vartak, yvartak1@binghamton.edu

## Tech-stack

* `python` - The project is developed and tested using python v3.10.6. [Python Website](https://www.python.org/)
* `request` - Request is a popular HTTP networking module(aka library) for python programming language. [Request Website](https://docs.python-requests.org/en/latest/#)
* `pymongo` - PyMongo is a Python distribution containing tools for working with MongoDB, and is the recommended way to work with MongoDB from Python. [Pymongo Website](https://pymongo.readthedocs.io/en/stable/)
* `json` - JSON (JavaScript Object Notation), is a lightweight data interchange format inspired by JavaScript object literal syntax. [json Website](https://docs.python.org/3/library/json.html)
* `time` - This module provides various time-related functions. [time Website](https://docs.python.org/3/library/time.html)
* `datetime` - The datetime module supplies classes for manipulating dates and times. [datetime Website](https://docs.python.org/3/library/datetime.html)
* `schedule` - In-process scheduler for periodic jobs. No extra processes needed. [schedule Website](https://schedule.readthedocs.io/en/stable/)
* `googleapiclient` - A client library for Google's discovery based APIs. [googleapiclient Website](https://googleapis.github.io/google-api-python-client/docs/epy/googleapiclient.discovery-module.html)
* `MongoDB`- This project uses MongoDB which is a document-oriented database classified as NoSQL for storing the collected data [MongoDB Website](https://www.mongodb.com/)

## Three data-source documentation

* `Twitter` - We are using the Twitter Stream API to fetch data related to `Sports` contexts.
  * [Tweets Stream](https://api.twitter.com/2/tweets/sample/stream) - API endpoint to get tweets in real time.
  * [API Documentation](https://developer.twitter.com/en/docs/twitter-api) - Twitter API documentation.
* `Reddit` - We are using `r/politics`, `r/uspolitics`and `r/AmericanPolitics` to fetch the comments on posts related to U.S. politics.
  * [r/politics](https://reddit.com/r/politics) - Subreddit for news and discussion about U.S. politics.
  * [r/uspolitics](https://reddit.com/r/uspolitics) - A subreddit for US Politics.
  * [r/AmericanPolitics](https://reddit.com/r/AmericanPolitics) - A place to discuss the American political process, American political topics, the political parties, elected officials, candidates, and American foreign policy.
  * [GET Posts](https://oauth.reddit.com/r/subreddit/new) - API endpoint to fetch the posts of the specified subreddit sorted by newest first.
  * [GET Comments](https://oauth.reddit.com/comments/article) - Get the comment tree for a given Link article.
  * [GET MoreComments](https://oauth.reddit.com/api/morechildren) - Retrieve additional comments omitted from a base comment tree.
  * [API Documentation](https://www.reddit.com/dev/api) - Reddit API documentation.
* `YouTube` - We fetch comments on videos posted by various Youtube channels like `SSSniperWolf`, `SidemenReacts`, `MarquesBrownlee`, `ScammerPayback` etc.
  * [GET Video Ids](https://www.googleapis.com/youtube/v3/playlistItems) - Returns a collection of playlist items that match the API request parameters.
  * [GET Comments](https://www.googleapis.com/youtube/v3/commentThreads) - Returns a list of comment threads that match the API request parameters.
  * [API Documentation](https://developers.google.com/youtube/v3/docs) - YouTube Data API documentation.

## System Architecture

* `Twitter`:

![Twitter System Architecture](https://drive.google.com/uc?export=view&id=16PaTHNrp0KBlNbgA63E-RYqI-BA1W85Y)

* `Reddit`:

![Reddit System Architecture](https://drive.google.com/uc?export=view&id=1B2pl53vX0c9ptRMXJEZLqRCcvTlc7kIN)

* `YouTube`:

![YouTube System Architecture](https://drive.google.com/uc?export=view&id=1957LEBWfyk0SeYpXG8wfLkDx4v6Yn-m8)

## How to run the project?

Install `Python` and `MongoDB`

```bash
pip install pymongo, schedule, google-api-python-client
cd twitter
nohup python3 twitter.py & echo $! > save_pid.txt
cd ../reddit
nohup python3 reddit.py & echo $! > save_pid.txt
cd ../youtube
nohup python3 youtube.py & echo $! > save_pid.txt
```

## Database schema - NoSQL

```bash
Twitter:
{
  "tweet_id": ...,
  "time_stamp": ...,
  "author_id": ...,
  "language": ...,
  "text": ...,
  "context": ...,
  "media_keys": ...
}

Reddit:
{
  "subreddit": ...,
  "post_id": ...,
  "comment_id": ...,
  "text": ...,
  "author": ...,
  "score": ...,
  "time_stamp": ...,
  "current_time": ...
}

Youtube: 
{
  "video_id": ...,
  "video_title": ...,
  "author": ...,
  "comment_text": ...,
  "like_count": ...,
  "reply_count": ...,
  "comment_timestamp": ...,
  "current_time": ...
}
```

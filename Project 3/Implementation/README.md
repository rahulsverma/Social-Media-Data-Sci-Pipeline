## Project Abstract

Social media platforms are proven to be a good source of data for scientific analysis and for training various machine learning models. We present visualizations of data from data collection systems that collects real time tweets data from Twitter, comments on the posts from the specified subreddit and comments on all the videos from the specified YouTube channel.

## Team - data-worthy

* Arjun Mahadkar, amahadk1@binghamton.edu
* Deepang Raval, draval1@binghamton.edu
* Rahul Verma, rverma4@binghamton.edu
* Sudeep Rawat, srawat1@binghamton.edu
* Yuraj Vartak, yvartak1@binghamton.edu

## Tech-stack

* `python` - The project is developed and tested using python v3.10.6. [Python Website](https://www.python.org/)
* `flask` - Web development framework for python programming language. [Flask Website](https://flask.palletsprojects.com/en/2.2.x/)
* `pandas` - pandas is a fast, powerful, flexible and easy to use open source data analysis and manipulation tool,
built on top of the Python programming language. [Pandas Website](https://pandas.pydata.org/)
* `matplotlib` - Matplotlib is a comprehensive library for creating static, animated, and interactive visualizations in Python. [matplotlib Website](https://matplotlib.org/)
* `datetime` - The datetime module supplies classes for manipulating dates and times. [datetime Website](https://docs.python.org/3/library/datetime.html)
* `wordcloud` - A little word cloud generator in Python. [wordcloud Website](https://pypi.org/project/wordcloud/)
* `spaCy` - spaCy is a free open-source library for Natural Language Processing in Python. [spaCy Website](https://spacy.io/)

## Three data-source documentation

* `Twitter` - We are using the Twitter Stream API to fetch data related to `Sports` contexts.
  * [API Documentation](https://developer.twitter.com/en/docs/twitter-api) - Twitter API documentation.
* `Reddit` - We are using `r/politics`, `r/uspolitics`and `r/AmericanPolitics` to fetch the comments on posts related to U.S. politics.
  * [r/politics](https://reddit.com/r/politics) - Subreddit for news and discussion about U.S. politics.
  * [r/uspolitics](https://reddit.com/r/uspolitics) - A subreddit for US Politics.
  * [r/AmericanPolitics](https://reddit.com/r/AmericanPolitics) - A place to discuss the American political process, American political topics, the political parties, elected officials, candidates, and American foreign policy.
* `YouTube` - We fetch comments on videos posted by various Youtube channels like `SSSniperWolf`, `SidemenReacts`, `MarquesBrownlee`, `ScammerPayback` etc.

## How to run the project?

Install `Python` and get the data files in the folder.

```bash
pip install -U pip setuptools wheel
pip install -U spacy
python -m spacy download en_core_web_sm
pip install wordcloud
pip install pandas
pip install flask
export FLASK_APP = app
export FLASK_DEBUG = 1
flask run
```

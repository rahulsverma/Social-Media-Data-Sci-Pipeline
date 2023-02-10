from pandas.core.groupby.groupby import DataFrame
from wordcloud import WordCloud, STOPWORDS
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm
from flask import Flask, request, render_template
import re
import pandas as pd
from datetime import datetime
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import base64
from io import BytesIO
pd.options.mode.chained_assignment = None
nlp = en_core_web_sm.load()

twitter_data = pd.read_csv('twitter.csv')
twitter_data['time_stamp'] = pd.to_datetime(
    twitter_data['time_stamp'], format="%Y-%m-%dT%H:%M:%S")

reddit_data = pd.read_csv('reddit.csv')
reddit_data['time_stamp'] = pd.to_datetime(
    reddit_data['time_stamp'], format="%Y-%m-%dT%H:%M:%S")

youtube_data = pd.read_csv('youtube.csv')
youtube_data['comment_timestamp'] = pd.to_datetime(
    youtube_data['comment_timestamp'], format="%Y-%m-%dT%H:%M:%S")

app = Flask(__name__)


@app.route('/', methods=["GET"])
def home():
    return render_template('home.html')


@app.route('/twitter', methods=["GET"])
def twitter():
    return render_template('twitter.html')


@app.route('/reddit', methods=["GET"])
def reddit():
    return render_template('reddit.html')


@app.route('/youtube', methods=["GET"])
def youtube():
    return render_template('youtube.html')


@app.route('/twitter-1', methods=["GET", "POST"])
def twitter_1():
	if request.method == "GET":
		start = datetime(2022, 11, 1, 0, 0, 0).isoformat()
		end = datetime(2022, 11, 2, 0, 0, 0).isoformat()
		mask = (twitter_data['time_stamp'] >= start) & (
			twitter_data['time_stamp'] < end)
		t_data = twitter_data.loc[mask]
		t_data = t_data['context'].value_counts().rename_axis(
			'Context').reset_index(name='Number of Tweets')
		legend = 'Number of tweets per context'
		labels = list(t_data['Context'])
		values = list(t_data['Number of Tweets'])
		daterange = start + " to " + end + ' UTC'
		return render_template('twitter-1.html', values=values, labels=labels, legend=legend, daterange=daterange)
	if request.method == "POST":
		startdate = request.form.get("start")
		enddate = request.form.get("end")
		start = datetime.strptime(startdate, '%Y/%m/%d %H:%M:%S').isoformat()
		end = datetime.strptime(enddate, '%Y/%m/%d %H:%M:%S').isoformat()
		mask = (twitter_data['time_stamp'] >= start) & (
			twitter_data['time_stamp'] < end)
		t_data = twitter_data.loc[mask]
		t_data = t_data['context'].value_counts().rename_axis(
			'Context').reset_index(name='Number of Tweets')
		legend = 'Number of tweets per context'
		labels = list(t_data['Context'])
		values = list(t_data['Number of Tweets'])
		daterange = start + " to " + end + ' UTC'
		return render_template('twitter-1.html', values=values, labels=labels, legend=legend, daterange=daterange)


@app.route('/twitter-2', methods=["GET", "POST"])
def twitter_2():
	if request.method == "GET":
		start = datetime(2022, 11, 1, 20, 0, 0).isoformat()
		end = datetime(2022, 11, 1, 22, 0, 0).isoformat()		
		mask = (twitter_data['time_stamp'] >= start) & (
			twitter_data['time_stamp'] < end)
		t_data = twitter_data.loc[mask]
		hashtags = t_data['text'].apply(lambda x: pd.value_counts(re.findall('(#\w+)', x.lower())))\
			.sum(axis=0)\
			.to_frame()\
			.reset_index()\
			.sort_values(by=0, ascending=False)
		hashtags.columns = ['Hashtag', 'Occurences']
		hashtags = hashtags[:10]
		legend = 'Top Hashtags'
		labels = list(hashtags['Hashtag'])
		values = list(hashtags['Occurences'])
		daterange = start + " to " + end + ' UTC'
		return render_template('twitter-2.html', values=values, labels=labels, legend=legend, daterange=daterange)
	if request.method == "POST":
		startdate = request.form.get("start")
		enddate = request.form.get("end")
		start = datetime.strptime(startdate, '%Y/%m/%d %H:%M:%S').isoformat()
		end = datetime.strptime(enddate, '%Y/%m/%d %H:%M:%S').isoformat()
		mask = (twitter_data['time_stamp'] >= start) & (
			twitter_data['time_stamp'] < end)
		t_data = twitter_data.loc[mask]
		hashtags = t_data['text'].apply(lambda x: pd.value_counts(re.findall('(#\w+)', x.lower())))\
			.sum(axis=0)\
			.to_frame()\
			.reset_index()\
			.sort_values(by=0, ascending=False)
		hashtags.columns = ['Hashtag', 'Occurences']
		hashtags = hashtags[:10]
		legend = 'Top Hashtags'
		labels = list(hashtags['Hashtag'])
		values = list(hashtags['Occurences'])
		daterange = start + " to " + end + ' UTC'
		return render_template('twitter-2.html', values=values, labels=labels, legend=legend, daterange=daterange)


@app.route('/twitter-3', methods=["GET", "POST"])
def twitter_3():
	comment_words = ''
	stopwords = set(STOPWORDS)
	stopwords.add('https')
	stopwords.add('t')
	stopwords.add('co')
	stopwords.add('rt')
	if request.method == "GET":
		start = datetime(2022, 11, 1, 21, 0, 0).isoformat()
		end = datetime(2022, 11, 1, 22, 0, 0).isoformat()
		mask = (twitter_data['time_stamp'] >= start) & (
			twitter_data['time_stamp'] < end)
		t_data = twitter_data.loc[mask]
		for ind in t_data.index:
			sequence = t_data['text'][ind].lower()
			doc = nlp(sequence)
			tokens = []
			for X in doc.ents:
				if X.label_ == 'NORP' or X.label_ == 'PERSON' or X.label_ == 'ORG' or X.label_ == 'GPE':
					tokens.append(X.text)
			for i in range(len(tokens)):
				tokens[i] = tokens[i].lower()
			comment_words += " ".join(tokens)+" "

		wordcloud = WordCloud(width=800, height=800,
								background_color='white',
								stopwords=stopwords,
								min_font_size=10).generate(comment_words)
		fig = Figure()
		FigureCanvas(fig)
		ax = fig.add_subplot(111)
		ax.imshow(wordcloud)
		ax.axis('off')
		buf = BytesIO()
		fig.savefig(buf, format="png")
		data = base64.b64encode(buf.getbuffer()).decode("ascii")
		daterange = start + " to " + end + ' UTC'
		return render_template('twitter-3.html', data=data, daterange=daterange)
	if request.method == "POST":
		startdate = request.form.get("start")
		enddate = request.form.get("end")
		start = datetime.strptime(startdate, '%Y/%m/%d %H:%M:%S').isoformat()
		end = datetime.strptime(enddate, '%Y/%m/%d %H:%M:%S').isoformat()
		mask = (twitter_data['time_stamp'] >= start) & (
			twitter_data['time_stamp'] < end)
		t_data = twitter_data.loc[mask]
		for ind in t_data.index:
			sequence = t_data['text'][ind].lower()
			doc = nlp(sequence)
			tokens = []
			for X in doc.ents:
				if X.label_ == 'NORP' or X.label_ == 'PERSON' or X.label_ == 'ORG' or X.label_ == 'GPE':
					tokens.append(X.text)
			for i in range(len(tokens)):
				tokens[i] = tokens[i].lower()
			comment_words += " ".join(tokens)+" "

		wordcloud = WordCloud(width=800, height=800,
								background_color='white',
								stopwords=stopwords,
								min_font_size=10).generate(comment_words)
		fig = Figure()
		FigureCanvas(fig)
		ax = fig.add_subplot(111)
		ax.imshow(wordcloud)
		ax.axis('off')
		buf = BytesIO()
		fig.savefig(buf, format="png")
		data = base64.b64encode(buf.getbuffer()).decode("ascii")
		daterange = start + " to " + end + ' UTC'
		return render_template('twitter-3.html', data=data, daterange=daterange)


@app.route('/reddit-1', methods=["GET", "POST"])
def reddit_1():
	if request.method == "GET":
		start = datetime(2022, 11, 4, 0, 0, 0).isoformat()
		end = datetime(2022, 11, 15, 0, 0, 0).isoformat()
		mask = (reddit_data['time_stamp'] >= start) & (
			reddit_data['time_stamp'] < end)
		r_data = reddit_data.loc[mask]
		r_data = r_data['time_stamp'].value_counts().rename_axis(
			'Date').reset_index(name='Number of Submissions')
		r_data = r_data.sort_values(by='Date')
		r_data.reset_index(drop=True)
		r_data = r_data.groupby([r_data['Date'].dt.floor('H')])
		r_data = r_data["Number of Submissions"].sum()
		r_data = DataFrame(r_data).reset_index()
		legend = 'Total Number of Submissions'
		labels = list(r_data['Date'])
		values = list(r_data['Number of Submissions'])
		daterange = start + " to " + end + ' UTC'
		return render_template('reddit-1.html', values=values, labels=labels, legend=legend, daterange=daterange)
	if request.method == "POST":
		startdate = request.form.get("start")
		enddate = request.form.get("end")
		start = datetime.strptime(startdate, '%Y/%m/%d %H:%M:%S').isoformat()
		end = datetime.strptime(enddate, '%Y/%m/%d %H:%M:%S').isoformat()
		mask = (reddit_data['time_stamp'] >= start) & (
			reddit_data['time_stamp'] < end)
		r_data = reddit_data.loc[mask]
		r_data = r_data['time_stamp'].value_counts().rename_axis(
			'Date').reset_index(name='Number of Submissions')
		r_data = r_data.sort_values(by='Date')
		r_data.reset_index(drop=True)
		r_data = r_data.groupby([r_data['Date'].dt.floor('H')])
		r_data = r_data["Number of Submissions"].sum()
		r_data = DataFrame(r_data).reset_index()
		legend = 'Total Number of Submissions'
		labels = list(r_data['Date'])
		values = list(r_data['Number of Submissions'])
		daterange = start + " to " + end + ' UTC'
		return render_template('reddit-1.html', values=values, labels=labels, legend=legend, daterange=daterange)


@app.route('/reddit-2', methods=["GET", "POST"])
def reddit_2():
	comment_words = ''
	stopwords = set(STOPWORDS)
	stopwords.add('https')
	stopwords.add('t')
	stopwords.add('co')
	stopwords.add('rt')
	if request.method == "GET":
		start = datetime(2022, 11, 4, 20, 0, 0).isoformat()
		end = datetime(2022, 11, 4, 21, 0, 0).isoformat()
		mask = (reddit_data['time_stamp'] >= start) & (
			reddit_data['time_stamp'] < end)
		r_data = reddit_data.loc[mask]
		for ind in r_data.index:
			sequence = r_data['text'][ind].lower()
			doc = nlp(sequence)
			tokens = []
			for X in doc.ents:
				if X.label_ == 'NORP' or X.label_ == 'PERSON' or X.label_ == 'ORG' or X.label_ == 'GPE':
					tokens.append(X.text)
			for i in range(len(tokens)):
				tokens[i] = tokens[i].lower()
			comment_words += " ".join(tokens)+" "
		wordcloud = WordCloud(width=800, height=800,
								background_color='white',
								stopwords=stopwords,
								min_font_size=10).generate(comment_words)
		fig = Figure()
		FigureCanvas(fig)
		ax = fig.add_subplot(111)
		ax.imshow(wordcloud)
		ax.axis('off')
		buf = BytesIO()
		fig.savefig(buf, format="png")
		data = base64.b64encode(buf.getbuffer()).decode("ascii")
		daterange = start + " to " + end + ' UTC'
		return render_template('reddit-2.html', data=data, daterange=daterange)
	if request.method == "POST":
		startdate = request.form.get("start")
		enddate = request.form.get("end")
		start = datetime.strptime(startdate, '%Y/%m/%d %H:%M:%S').isoformat()
		end = datetime.strptime(enddate, '%Y/%m/%d %H:%M:%S').isoformat()
		mask = (reddit_data['time_stamp'] >= start) & (
			reddit_data['time_stamp'] < end)
		r_data = reddit_data.loc[mask]
		for ind in r_data.index:
			sequence = r_data['text'][ind].lower()
			doc = nlp(sequence)
			tokens = []
			for X in doc.ents:
				if X.label_ == 'NORP' or X.label_ == 'PERSON' or X.label_ == 'ORG' or X.label_ == 'GPE':
					tokens.append(X.text)
			for i in range(len(tokens)):
				tokens[i] = tokens[i].lower()
			comment_words += " ".join(tokens)+" "
		wordcloud = WordCloud(width=800, height=800,
								background_color='white',
								stopwords=stopwords,
								min_font_size=10).generate(comment_words)
		fig = Figure()
		FigureCanvas(fig)
		ax = fig.add_subplot(111)
		ax.imshow(wordcloud)
		ax.axis('off')
		buf = BytesIO()
		fig.savefig(buf, format="png")
		data = base64.b64encode(buf.getbuffer()).decode("ascii")
		daterange = start + " to " + end + ' UTC'
		return render_template('reddit-2.html', data=data, daterange=daterange)


@app.route('/youtube-1', methods=["GET", "POST"])
def youtube_1():
	if request.method == "GET":
		start = datetime(2022, 11, 1, 0, 0, 0).isoformat()
		end = datetime(2022, 11, 15, 0, 0, 0).isoformat()
		mask = (youtube_data['comment_timestamp'] >= start) & (
			youtube_data['comment_timestamp'] < end)
		y_data = youtube_data.loc[mask]
		y_data = y_data['video_title'].value_counts()[:10].rename_axis(
			'Video').reset_index(name='Number of Comments')
		legend = 'Videos with most comments'
		labels = list(y_data['Video'])
		values = list(y_data['Number of Comments'])
		daterange = start + " to " + end + ' UTC'
		return render_template('youtube-1.html', values=values, labels=labels, legend=legend, daterange=daterange)
	if request.method == "POST":
		startdate = request.form.get("start")
		enddate = request.form.get("end")
		start = datetime.strptime(startdate, '%Y/%m/%d %H:%M:%S').isoformat()
		end = datetime.strptime(enddate, '%Y/%m/%d %H:%M:%S').isoformat()
		mask = (youtube_data['comment_timestamp'] >= start) & (
			youtube_data['comment_timestamp'] < end)
		y_data = youtube_data.loc[mask]
		y_data = y_data['video_title'].value_counts()[:10].rename_axis(
			'Video').reset_index(name='Number of Comments')
		legend = 'Videos with most comments'
		labels = list(y_data['Video'])
		values = list(y_data['Number of Comments'])
		daterange = start + " to " + end + ' UTC'
		return render_template('youtube-1.html', values=values, labels=labels, legend=legend, daterange=daterange)


@app.route('/youtube-2', methods=["GET", "POST"])
def youtube_2():
	if request.method == "GET":
		start = datetime(2022, 11, 1, 0, 0, 0).isoformat()
		end = datetime(2022, 11, 15, 0, 0, 0).isoformat()
		mask = (youtube_data['comment_timestamp'] >= start) & (
			youtube_data['comment_timestamp'] < end)
		y_data = youtube_data.loc[mask]
		y_data = y_data['author'].value_counts()[:10].rename_axis(
			'Author').reset_index(name='Number of Comments')
		legend = 'Authors with most comments'
		labels = list(y_data['Author'])
		values = list(y_data['Number of Comments'])
		daterange = start + " to " + end + ' UTC'
		return render_template('youtube-2.html', values=values, labels=labels, legend=legend, daterange=daterange)
	if request.method == "POST":
		startdate = request.form.get("start")
		enddate = request.form.get("end")
		start = datetime.strptime(startdate, '%Y/%m/%d %H:%M:%S').isoformat()
		end = datetime.strptime(enddate, '%Y/%m/%d %H:%M:%S').isoformat()
		mask = (youtube_data['comment_timestamp'] >= start) & (
			youtube_data['comment_timestamp'] < end)
		y_data = youtube_data.loc[mask]
		y_data = y_data['author'].value_counts()[:10].rename_axis(
			'Author').reset_index(name='Number of Comments')
		legend = 'Authors with most comments'
		labels = list(y_data['Author'])
		values = list(y_data['Number of Comments'])
		daterange = start + " to " + end + ' UTC'
		return render_template('youtube-2.html', values=values, labels=labels, legend=legend, daterange=daterange)


@app.route('/youtube-3', methods=["GET", "POST"])
def youtube_3():
	comment_words = ''
	stopwords = set(STOPWORDS)
	stopwords.add('https')
	stopwords.add('b')
	stopwords.add('br')
	if request.method == "GET":
		start = datetime(2022, 11, 1, 0, 0, 0).isoformat()
		end = datetime(2022, 11, 2, 0, 0, 0).isoformat()
		mask = (youtube_data['comment_timestamp'] >= start) & (
			youtube_data['comment_timestamp'] < end)
		y_data = youtube_data.loc[mask]
		for ind in y_data.index:
			if 'telegram' in str(y_data['author'][ind]).lower() or 'whatsapp' in str(y_data['author'][ind]).lower():
				sequence = str(y_data['comment_text'][ind]).lower()

				tok = sequence.split(" ")
				tokens = [t for t in tok]

				comment_words += " ".join(tokens)+" "

		wordcloud = WordCloud(width=800, height=800,
								background_color='white',
								stopwords=stopwords,
								min_font_size=10).generate(comment_words)
		fig = Figure()
		FigureCanvas(fig)
		ax = fig.add_subplot(111)
		ax.imshow(wordcloud)
		ax.axis('off')
		buf = BytesIO()
		fig.savefig(buf, format="png")
		data = base64.b64encode(buf.getbuffer()).decode("ascii")
		daterange = start + " to " + end + ' UTC'
		return render_template('youtube-3.html', data=data, daterange=daterange)
	if request.method == "POST":
		startdate = request.form.get("start")
		enddate = request.form.get("end")
		start = datetime.strptime(startdate, '%Y/%m/%d %H:%M:%S').isoformat()
		end = datetime.strptime(enddate, '%Y/%m/%d %H:%M:%S').isoformat()
		mask = (youtube_data['comment_timestamp'] >= start) & (
			youtube_data['comment_timestamp'] < end)
		y_data = youtube_data.loc[mask]
		for ind in y_data.index:
			if 'telegram' in str(y_data['author'][ind]).lower() or 'whatsapp' in str(y_data['author'][ind]).lower():
				sequence = str(y_data['comment_text'][ind]).lower()

				tok = sequence.split(" ")
				tokens = [t for t in tok]

				comment_words += " ".join(tokens)+" "

		wordcloud = WordCloud(width=800, height=800,
								background_color='white',
								stopwords=stopwords,
								min_font_size=10).generate(comment_words)
		fig = Figure()
		FigureCanvas(fig)
		ax = fig.add_subplot(111)
		ax.imshow(wordcloud)
		ax.axis('off')
		buf = BytesIO()
		fig.savefig(buf, format="png")
		data = base64.b64encode(buf.getbuffer()).decode("ascii")
		daterange = start + " to " + end + ' UTC'
		return render_template('youtube-3.html', data=data, daterange=daterange)

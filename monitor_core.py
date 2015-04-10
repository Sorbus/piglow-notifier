import time
import praw
import pickle
import atexit
import configparser
from PyGlow import PyGlow

pyglow = PyGlow()

Config = configparser.ConfigParser()
Config.read('config.ini')

if Config.has_option('global','delay'):
	scan_delay = Config.get('global','delay')
else:
	scan_delay = 30
	
if Config.has_option('global','max_records'):
	max_records = Config.get('global','max_records')
else:
	max_records = 50

if Config.has_section('reddit'):
	reddit = true
	target_sub = Config.get('reddit','target')
	botLogin = Config.get('reddit','login')
	botPassword = Config.get('reddit','password')
	if Config.has_option('reddit','request_size'):
		request_size = Config.get('global','request_size')
	else:
		request_size = max_records
else:
	reddit = false

if reddit:
	r = praw.Reddit('Subreddit Activity Monitor/0.5 by /u/Fourdots')
	r.config._ssl_url = None
	r.login(botLogin,botPassword)

	already_done_posts = []
	already_done_posts.append(pickle.load(open('bot-db-posts', 'rb')))
	already_done_comments = []
	already_done_comments.append(pickle.load(open('bot-db-comments', 'rb')))

colors = ['red','orange','yellow','green','blue','white']
colorcodes = [[1,7,13],[2,8,14],[3,9,15],[4,10,16],[5,11,17],[6,12,18]]

def turnup(color,wait=0.05):
	for i in range (0,200,25):
		pyglow.color(color, i)
		time.sleep(wait)

def turndown(color,wait=0.05):
	if color == 'all':
		for i in range (200,-1,-25):
			pyglow.all(i)
			time.sleep(wait)
	else:
		for i in range (200,-1,-25):
			pyglow.color(color, i)
			time.sleep(wait)

def pulseIn(wait=0.02):
	state = [10,0,0,0,0,0]
	while state[5] < 400:
		for i in range(0,6):
			if state[i] <= 200 and state[i] > 0:
				pyglow.set_leds(colorcodes[i],state[i])
				state[i] = state[i] + 10
			elif state[i] <= 400 and state[i] > 0:
				pyglow.set_leds(colorcodes[i],400-state[i])
				state[i] = state[i] + 10
			else:
				pyglow.set_leds(colorcodes[i],0)
			if state[i] == 100 and i != 5:
				state[i+1] = 10
		pyglow.update_leds()
		time.sleep(wait)
	pyglow.all(0)
	
def pulseOut(wait=0.02):
	state = [0,0,0,0,0,10]
	while state[0] < 400:
		for i in range(5,-1,-1):
			if state[i] <= 200 and state[i] > 0:
				pyglow.set_leds(colorcodes[i],state[i])
				state[i] = state[i] + 10
			elif state[i] <= 400 and state[i] > 0:
				pyglow.set_leds(colorcodes[i],400-state[i])
				state[i] = state[i] + 10
			else:
				pyglow.set_leds(colorcodes[i],0)
			if state[i] == 100 and i != 0:
				state[i-1] = 10
		pyglow.update_leds()
		time.sleep(wait)
	pyglow.all(0)

def startup():
	for item in colors:
		turnup(item)
	turndown('all')

def shutdown():
	pyglow.all(0)

def clear(array):
	removed = 0
	while len(array) > 50:
		array.pop(0)
		removed = removed + 1
#	print('Removed ' + str(removed) + ' entries from array, new size ' + str(len(array)))

atexit.register(shutdown)

startup()

subreddit = r.get_subreddit(target_sub)

if reddit:
	while True:
		comments = 0;
		submissions = 0;
	#	print('-----------')
		for submission in subreddit.get_new(limit=request_size):
			if submission.id not in already_done_posts:
	#			print(str(submission.author) + ' posts:\t' + submission.title)
				submissions = submissions + 1
				already_done_posts.append(submission.id)
	#	print('-----------')
		for comment in subreddit.get_comments(limit=request_size):
			if comment.id not in already_done_comments:
	#			if comment.body.__len__() > 100:
	#				print(str(comment.author) + ' comments:\t' + comment.body[0:100] + '...')
	#			else:
	#				print(comment.body)
				comments = comments + 1
				already_done_comments.append(comment.id)
	#	print('-----------')
		clear(already_done_posts)
		clear(already_done_comments)
		print((str(comments) + ' new comments seen, ' + str(submissions) + ' new submissions seen'))
		while comments > 0:
			pulseOut()
			comments = comments - 1
		while submissions > 0:
			pulseIn()
			submissions = submissions - 1
		print('Cycle complete, waiting')
		pickle.dump(already_done_comments, open('bot-db-comments', 'wb'))
		pickle.dump(already_done_posts, open('bot-db-posts', 'wb'))
		time.sleep(scan_delay)
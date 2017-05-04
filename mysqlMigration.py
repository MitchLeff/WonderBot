import mysql.connector, pprint, tweepy, json, time
from constants import *
from mysql.connector import errorcode

# Import authentication credentials from "keys.json" file
try:
	keys = json.load(open("keys.json"))
	print("Keys located...\n")
except:
	print("Unable to locate keys")

# Authenticate 
auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
auth.set_access_token(keys['access_token'], keys['access_token_secret'])

#Create API connection
try:
	api = tweepy.API(auth)
	print("API connection secured...\n")
except:
	print("Unable to make API connection")


s = api.search(QUERY_STRING)

newTweets = []

for n in s:
	newTweets.append(str(n.id))
	
	try:
		tweet = api.get_status(n.id)
	except:
		print("No tweet found with ID: " + str(n.id))
		

	cnx = mysql.connector.connect(user=MYSQL_USER, password=MYSQL_PASSWORD,
							  host='localhost',
							  database='wonders', port=3306)
	cursor = cnx.cursor()

	dateCreated = tweet._json['created_at'][-4:]+ "-04-" + tweet._json['created_at'][8:10]
	wonderText = tweet._json['text'].replace("\"","\\\"")

	wonderer = tweet._json['user']['screen_name']
	id = tweet._json['id']
	resolved = 1
	if "!give" in wonderText and "!take" in wonderText:
		commandType = "'jerk'"
	elif "!give" in wonderText:
		commandType = "'give'"
	elif "!take" in wonderText:
		commandType = "'take'"
	else:
		commandType = "'none'"

	query = ("INSERT INTO wonders (date_created, wonder_text, wonderer, resolved, command_type, id) VALUES (\"" + dateCreated + "\", \"" + wonderText + "\", \"" + wonderer + "\", " + str(resolved) + ", " + commandType + ", " + str(id) + ")")
	print(query)
	cursor.execute(query)

	cnx.commit()

	cursor.close()
	cnx.close()
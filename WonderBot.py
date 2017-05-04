import random, sys, pprint, mysql.connector
from constants import *


def addWonder(id, api):
	try:
		tweet = api.get_status(id)
		
		dateCreated = tweet._json['created_at'][-4:] + "-" + monthsDict[tweet._json['created_at'][4:7]] + "-" + tweet._json['created_at'][8:10]
		wonderer = tweet._json['user']['screen_name']
		wonderText = tweet._json['text'].replace("\"","\\\"")
		id = tweet._json['id_str']
		resolved = "0"
		if "!give" in wonderText and "!take" in wonderText:
			commandType = "'jerk'"
		elif "!give" in wonderText:
			commandType = "'give'"
		elif "!take" in wonderText:
			commandType = "'take'"
		else:
			commandType = "'none'"

		
		cnx = mysql.connector.connect(user=MYSQL_USER, password=MYSQL_PASSWORD,
							  host='localhost',
							  database='wonders', port=3306)
		
		cursor = cnx.cursor()
		
		query = ("INSERT INTO wonders (date_created, wonder_text, resolved, command_type, id) VALUES (\"" + dateCreated + "\", \"" + wonderText + "\", " + str(resolved) + ", " + commandType + ", " + str(id) + ")")
		print("Tweet " + id + " added to database")
		results = cursor.execute(query)
		cnx.commit()

		cursor.close()
		cnx.close()
		
	except:
		print("Unable to add tweet: " + str(id))
		print(str(sys.exc_info()[0]) + str(sys.exc_info()[1]))

def popWonder():
	try:
		cnx = mysql.connector.connect(user=MYSQL_USER, password=MYSQL_PASSWORD,
							  host=MYSQL_HOST,
							  database=MYSQL_DB, port=3306)
		
		cursor = cnx.cursor()
		
		query = ("SELECT id, wonder_text FROM " + str(MYSQL_DB) + ";")
		cursor.execute(query)
		rows = cursor.fetchall()
		
		if len(rows) == 0:
		
			cursor.close()
			cnx.close()
			
			return 0

		else:
			chosenWonder = rows[random.randint(0, len(rows) - 1)]
			
			id = chosenWonder[0]
			wonderString = chosenWonder[1].split("!give", 1)[-1].strip()
			
			command = ("DELETE FROM " + str(MYSQL_DB) + " WHERE id=" + str(id) + ";")
			cursor.execute(command)
			
			cnx.commit()
			
			cursor.close()
			cnx.close()
			
			return wonderString
		
	except:
		print("Unable to pop wonder")
		print(str(sys.exc_info()[0]) + str(sys.exc_info()[1]))
		return ""
	

def addWonderToFile(wonderString):
	try:
		#This function adds a wonder to the wonderlist
		with open(WONDER_FILE, 'a') as f:
			f.write(wonderString + "\n")
	except:
		print("Unable to add a wonder to " + WONDER_FILE)
		print(sys.exc_info()[0] + sys.exc_info()[1])

def popWonderFromFile():
	#This function takes a wonder out of the wonderlist and returns it
	try:
		with open(WONDER_FILE, 'r') as f:
			flist = list(f)
			numlines = len(flist)

		if numlines <= 0:
			return 0
		else:
			lineChosen = random.randint(0, numlines - 1)
			returnString = flist.pop(lineChosen)
		
			with open(WONDER_FILE, 'w') as f:
				for line in flist:
					f.write(line)
		return returnString

	except:
		print("Unable to pop a wonder from " + WONDER_FILE)
		print(str(sys.exc_info()[0]) + str(sys.exc_info()[1]))
		return ""
		
def UpdateNew(api):
	# This function checks to see if there are new tweets that have not been processed yet and returns a list of new tweets
	try:
		s = api.search(QUERY_STRING)
		
		newTweets = []
		
		for n in s:
			id = str(n.id)
			
			if id in open("ids.txt").read():
				pass
			else:
				newTweets.append(n.id)
			
		return newTweets
	except:
		print("Failed to make query search")
		print(sys.exc_info())
		return []


def ResolveTweet(id, api):
	# This function resolves if WonderBot needs to send a wonder or is taking a wonder
	try:
		tweet = api.get_status(id)
	except:
		print("No tweet found with ID: " + str(id))
		print(str(sys.exc_info()[0]) + str(sys.exc_info()[1]))
		return
	
	
	resolved = False
	print("\nResolving " + str(tweet.id))
	
	try:
		if "!give" in tweet.text and "!take" in tweet.text:
			print(tweet._json['user']['screen_name'] + " is an asshole dumbass")
			api.update_status("@" + tweet._json['user']['screen_name'] + " Don't try to confuse me :(", in_reply_to_status_id = tweet.id_str)
			
		elif "!give" in tweet.text:
			wonder = tweet.text.split("!give", 1)[-1].strip()
			addWonder(tweet.id_str, api)
			print("Wonder added:\t" + str(wonder))
			api.update_status("@" + tweet._json['user']['screen_name'] + " Thank you! Your wonder is safe with me.", in_reply_to_status_id = tweet.id_str)
			
		elif "!take" in tweet.text:
			wonder = popWonder()
			if wonder == 0:
				print("No wonders left to give!")
				api.update_status("@" + tweet._json['user']['screen_name'] + " I'm sorry, I'm all out of wonders at the moment. :(", in_reply_to_status_id = tweet.id_str)
			elif wonder == "":
				print("Unable to pop wonder...")
			else:
				wonder = wonder.strip()
				print("Wonder taken:\t" + str(wonder))
				api.update_status("@" + tweet._json['user']['screen_name'] + " \"" + wonder + "\"", in_reply_to_status_id = tweet.id_str)
		else:
			print("No command found")
		resolved = True
	except:
		print("Unable to resolve tweet")
		print(str(sys.exc_info()[0]) + str(sys.exc_info()[1]))
	
	if resolved:
		try:
			#After resolution, add ID to list of resolved tweets
			with open("ids.txt",'a') as f:
				f.write(str(id) + "\n")
		except:
			print("Unable to write to ids.txt")
			print(str(sys.exc_info()[0]) + str(sys.exc_info()[1]))
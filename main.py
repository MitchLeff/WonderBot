import tweepy, time, json, mysql.connector
from WonderBot import *
from constants import *

print("Yawwwwwn. I'm awake...\n")

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
	
#Wondering Text Variables
wondering = "WONDERING"
wonderNum = 0


print("Beginning wondering process...")
running = True

#Initialize last update run time
last_run_time = time.time()

# ---- BEGIN MAIN LOOP ----
while running:
	# Update current time
	now = time.time()
	
	# Check to see if the update time is reached
	if now - last_run_time > SLEEP_TIME:
	
		# Reset the last update time to current time
		last_run_time = now
		
		# Run the update
		newTweets = UpdateNew(api)
		
		# Resolve new tweets if there are any found
		if newTweets:
			print("New tweets found: " + str(newTweets))
		
			for tweet in newTweets:
				ResolveTweet(tweet, api)
				
		else: 
			# If no new tweets, print still wondering statement
			print(time.ctime(now) + " - " + wondering[wonderNum % len(wondering):] + wondering[:wonderNum % len(wondering)])
			wonderNum += 1
	
	# Rest one second between update checks
	time.sleep(1)
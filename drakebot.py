#!/usr/bin/env python

import os, time, re, random, eliza
from slackclient import SlackClient

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

# instantiate eliza
eliza_mode = 0
therapist = eliza.eliza()

# drakebot's user ID in Slack: value is assigned after the bot starts up
drakebot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "give me a drake fact"
MENTION_REGEX = r"^.*<@(|[WU].+?)>\W?(.*)"
DRAKE_FACT_FILE = 'drakebot_facts.txt'
DRAKE_REGEXES = {
	"best": re.compile(".*tell (.*) they (tha|da) best")
	,"fact": re.compile("(TELL|GIVE) ME.*DRAKE FACT", re.I)
	,"hi": re.compile("HI|HELLO|WHAT'S UP|HEY|WHAT UP", re.I)
	,"yolo": re.compile(".*YOLO.*", re.I)
	,"eliza_on": re.compile(".*enter therapy mode.*", re.I)
	,"eliza_off": re.compile(".*exit therapy mode.*", re.I)
	,"love": re.compile(".*do you love me.*", re.I) 
}

def random_drake_fact():
	afile = open(DRAKE_FACT_FILE)
	line = next(afile)
	for num, aline in enumerate(afile):
		if random.randrange(num + 2): continue
		line = aline
	return line

def parse_bot_commands(slack_events):
	"""
		Parses a list of events coming from the Slack RTM API to find bot commands.
		If a bot command is found, this function returns a tuple of command and channel.
		If its not found, then this function returns None, None.
	"""
	for event in slack_events:
		if event["type"] == "message" and not "subtype" in event:
			user_id, message = parse_direct_mention(event["text"])
			if user_id == drakebot_id:
				return message, event["channel"]
	return None, None

def parse_direct_mention(message_text):
	"""
		Finds a direct mention (a mention that is at the beginning) in message text
		and returns the user ID which was mentioned. If there is no direct mention, returns None
	"""
	matches = re.search(MENTION_REGEX, message_text)
	# the first group contains the username, the second group contains the remaining message
	return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
	"""
		Executes bot command if the command is known
	"""
	#eliza mode
	global eliza_mode

	#global regexes
	global DRAKE_REGEXES

	# Default response is help text for the user
	default_response = "Not sure what you mean. Try *{}*, or *tell <name> they tha best*".format(EXAMPLE_COMMAND)
	
	# Finds and executes the given command, filling in response
	response = None

	# This is where you start to implement more commands!
	try:
		if DRAKE_REGEXES["fact"].match(command) is not None:
			response = random_drake_fact()
		elif DRAKE_REGEXES["best"].match(command):
			response = "{}, you da best, you da you da best".format((best_regex.match(command)).group(1))
		elif DRAKE_REGEXES["hi"].match(command):
			response = "What up"
		elif DRAKE_REGEXES["yolo"].match(command):
			response = "That's the motto"
		elif DRAKE_REGEXES["love"].match(command):
			response = "Only partly.  I only love my bed and momma; I'm sorry."
		elif DRAKE_REGEXES["eliza_on"].match(command):
			eliza_mode = 1
			response = therapist.respond("Hello")
		elif DRAKE_REGEXES["eliza_off"].match(command):
			eliza_mode = 0
			response = therapist.respond("quit")
		else:
			if eliza_mode is 1:
				response = therapist.respond(command)
			else:
				response = default_response
	except Exception as e:
		response = "I have crashed! Help!"
		print(str(e))

	# Sends the response back to the channel
	slack_client.api_call(
		"chat.postMessage",
		channel=channel,
		text=response or default_response
	)

if __name__ == "__main__":
	if slack_client.rtm_connect(with_team_state=False):
		print("Drake Bot connected and running!")
		# Read bot's user ID by calling Web API method `auth.test`
		drakebot_id = slack_client.api_call("auth.test")["user_id"]
		while True:
			command, channel = parse_bot_commands(slack_client.rtm_read())
			if command:
				print("DEBUG: " + command)
				handle_command(command, channel)
			time.sleep(RTM_READ_DELAY)
	else:
		print("Connection failed. Exception traceback printed above.")

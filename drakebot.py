#!python3

import os
import time
import re
import random
import slack
import eliza
import ENV


# constants
BOT_NAME = 'Drake Bot'
EXAMPLE_COMMAND = "give me a drake fact"
MENTION_REGEX = r"^.*<@(|[WU].+?)>\W?(.*)"
DRAKE_FACT_FILE = 'drakebot_facts.txt'
DRAKE_REGEXES = {
	"best": re.compile(".*tell (.*) they (tha|da) best")
	,"fact": re.compile(".*(TELL|GIVE) ME.*DRAKE FACT", re.I)
	,"hi": re.compile("HI|HELLO|WHAT'S UP|HEY|WHAT UP", re.I)
	,"yolo": re.compile(".*YOLO.*", re.I)
	,"eliza_on": re.compile(".*can we talk.*|.*I want to talk.*", re.I)
	,"eliza_off": re.compile(".*I feel much better now.*|.*I'm done talking.*", re.I)
	,"love": re.compile(".*do you love me.*", re.I)
}
DEFAULT_RESPONSE = "Not sure what you mean. Try *{}*, or *tell <name> they tha best*".format(EXAMPLE_COMMAND)


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

	def parse_direct_mention(message_text):
		"""
			Finds a direct mention (a mention that is at the beginning) in message text
			and returns the user ID which was mentioned. If there is no direct mention, returns None
		"""
		matches = re.search(MENTION_REGEX, message_text)
		# the first group contains the username, the second group contains the remaining message
		return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

	for event in slack_events:
		if event["type"] == "message" and not "subtype" in event:
			user_id, message = parse_direct_mention(event["text"])
			if user_id == drakebot_id:
				return message, event["channel"]
	return None, None


def old_handle_command(command, channel):
	"""
		Executes bot command if the command is known
	"""
	# pull in global variables
	global eliza_mode, DRAKE_REGEXES, DEFAULT_RESPONSE

	# Finds and executes the given command, filling in response
	response = None

	# This is where you start to implement more commands!
	try:
		if DRAKE_REGEXES["fact"].match(command) is not None:
			response = random_drake_fact()
		elif DRAKE_REGEXES["best"].match(command):
			response = "{}, you da best, you da you da best".format((DRAKE_REGEXES["best"].match(command)).group(1))
		elif DRAKE_REGEXES["hi"].match(command):
			response = "What up"
		elif DRAKE_REGEXES["yolo"].match(command):
			response = "That's the motto"
		elif DRAKE_REGEXES["love"].match(command):
			response = "Only paresponse = Nonertly.  I only love my bed and momma; I'm sorry."
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
				response = DEFAULT_RESPONSE
	except Exception as e:
		response = "I have crashed! Help!"
		print(str(e))

	# Sends the response back to the channel
	slack_client.api_call(
		"chat.postMessage",
		channel=channel,
		text=response or DEFAULT_RESPONSE
	)


@slack.RTMClient.run_on(event='message')
def handle_command(**payload):

	global eliza_mode
	response = None
	data = payload['data']

	# data.get('subtype') in ['message_replied', 'bot_message']

	if (data.get('subtype') not in ['message_replied', 'bot_message']):
		channel_id = data['channel']
		thread_ts = data['ts']
		user = data['user']
		webclient = payload['web_client']

		command = data['text']

		# This is where you start to implement more commands!
		try:
			if DRAKE_REGEXES["fact"].match(command) is not None:
				response = random_drake_fact()
			elif DRAKE_REGEXES["best"].match(command):
				response = "{}, you da best, you da you da best".format((DRAKE_REGEXES["best"].match(command)).group(1))
			elif DRAKE_REGEXES["hi"].match(command):
				response = "What up"
			elif DRAKE_REGEXES["yolo"].match(command):
				response = "That's the motto"
			elif DRAKE_REGEXES["love"].match(command):
				response = "Only paresponse = Nonertly.  I only love my bed and momma; I'm sorry."
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
					response = DEFAULT_RESPONSE
		except Exception as e:
			response = "I have crashed! Help!"
			print(str(e))

		webclient.chat_postMessage(
			channel=channel_id
			,text = response or DEFAULT_RESPONSE
			# ,thread_ts = thread_ts
		)
	elif (data.get('subtype') == 'message_replied'):
		print('No "text" parameter detected in payload.')
	elif (data.get('subtype') == 'bot_message'):
		print('This is a response from the bot.  Ignore this.')


if __name__ == "__main__":
	slack_token = ENV.SLACK_BOT_TOKEN

	if (slack_token is None):
		raise Exception(f'''No value found for environment variable "SLACK_BOT_TOKEN"! 
	Did you forget to activate the python environment, or create the env.bash file with necessary environment variables?
	''')

	rtmclient = slack.RTMClient(token=slack_token)

	# instantiate eliza
	eliza_mode = 0
	therapist = eliza.eliza()

	# drakebot's user ID in Slack: value is assigned after the bot starts up
	drakebot_id = None

	try:
		rtmclient.start()
	except Exception as e:
		print(f"{e.__class__.__name__}: {e}\n\nConnection failed. Exception traceback printed above.")
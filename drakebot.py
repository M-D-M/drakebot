import os
import time
import re
import logging
import slack
import drakebot_config
import ENV

# constants
LOGGING_FMT='%(levelname)s [%(asctime)s] %(name)s:%(message)s'
MENTION_REGEX = r"^.*<@(|[WU].+?)>\W?(.*)"

# global variables
Drakebot_ID = ''

def parse_direct_mention(message_text):
	"""
		Finds a direct mention (a mention that is at the beginning) in message text
		and returns the user ID which was mentioned. If there is no direct mention, returns None
	"""
	matches = re.search(MENTION_REGEX, message_text)
	# the first group contains the username, the second group contains the remaining message
	return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


@slack.RTMClient.run_on(event='message')
def handle_command(**payload):
	response = ''
	data = payload['data']

	if (not 'subtype' in data):
		user_id, message = parse_direct_mention(data['text'])
		if user_id == Drakebot_ID:
			channel_id = data['channel']
			# thread_ts = data['ts']
			# user = data['user']
			webclient = payload['web_client']

			response = drakebot_config.respond_to_message(message)

			webclient.chat_postMessage(
				channel=channel_id
				,text = response or drakebot_config.DEFAULT_RESPONSE
				# ,thread_ts = thread_ts
			)
		else:
			logging.debug('This message was not inteded for the Drake Bot.  Ignore this.')


if __name__ == "__main__":

	logging_vars = {
		'format': LOGGING_FMT
	}
	if (ENV.DEBUG):
		logging_vars.update({
			'level': logging.DEBUG
		})
	else:
		logging_vars.update({
			'level': logging.INFO
			,'filename': 'bot_output.log'
		})

	logging.basicConfig(**logging_vars)

	slack_token = ENV.SLACK_BOT_TOKEN

	if (slack_token is None):
		raise Exception(f'''No value found for environment variable "SLACK_BOT_TOKEN"! 
	Did you forget to activate the python environment, or create the ENV.py file with necessary environment variables?
	''')

	try:
		# Get just the drakebot id
		web_client = slack.WebClient(ENV.SLACK_BOT_TOKEN, timeout=30)
		Drakebot_ID = web_client.api_call("auth.test")["user_id"]
		logging.debug(f'Drake Bot ID received: {Drakebot_ID}')

		logging.debug('Starting RTM interface...')
		rtmclient = slack.RTMClient(token=slack_token)
		rtmclient.start()
	except Exception as e:
		logging.critical(f"{e.__class__.__name__}: {e}\n\nConnection failed. Exception traceback printed above.")
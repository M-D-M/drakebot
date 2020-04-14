import re
import logging
import slack
import ssl as ssl_lib
import certifi
import asyncio

# constants
MENTION_REGEX = r"^.*<@(|[WU].+?)>\W?(.*)"

# global variables
Drakebot_ID = ''
Token = ''
Message_Function = None

class drakebot:
	def __init__(self, token: str, message_function):
		if (token is None or token == ''):
			raise Exception('No value found for token!')

		if (not callable(message_function)):
			raise Exception('Function passed for "message_function" is not callable!')

		self.Token = token
		self.Message_Function = message_function

		try:
			# Get just the drakebot id
			web_client = slack.WebClient(self.Token, timeout=30)
			self.Drakebot_ID = web_client.api_call("auth.test")["user_id"]
			logging.debug(f'Drake Bot ID received: {self.Drakebot_ID}')
		except Exception as e:
			logging.critical(f"{e.__class__.__name__}: {e}\n\nConnection failed. Exception traceback printed above.")
			raise


	def start(self):
		try:
			logging.info('Starting Slack Bot RTM interface...')

			ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
			loop = asyncio.new_event_loop()
			asyncio.set_event_loop(loop)


			rtmclient = slack.RTMClient(token=self.Token, ssl=ssl_context, run_async=True, loop=loop)
			rtmclient.run_on(event='message')(self.handle_command)
			loop.run_until_complete(rtmclient.start())
		except Exception as e:
			logging.critical(f"{e.__class__.__name__}: {e}\n\nConnection failed. Exception traceback printed above.")
			raise


	def parse_direct_mention(self, message_text):
		"""
			Finds a direct mention (a mention that is at the beginning) in message text
			and returns the user ID which was mentioned. If there is no direct mention, returns None
		"""
		matches = re.search(MENTION_REGEX, message_text)
		# the first group contains the username, the second group contains the remaining message
		return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


	async def handle_command(self, **payload):
		response = ''
		data = payload['data']

		if (not 'subtype' in data):
			user_id, message = self.parse_direct_mention(data['text'])
			if user_id == self.Drakebot_ID:
				channel_id = data['channel']
				# thread_ts = data['ts']
				# user = data['user']
				webclient = payload['web_client']

				response = self.Message_Function(message, payload)

				webclient.chat_postMessage(
					channel=channel_id
					,text = response
					# ,thread_ts = thread_ts
				)
			else:
				logging.debug('This message was not inteded for the bot.  Ignore this.')


if __name__ == "__main__":
	logging.critical('Please load this script as a class.')
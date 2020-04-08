import re
import random
import logging
import drakebot
import eliza
import ENV

# Constants
LOGGING_FMT='%(levelname)s [%(asctime)s] %(name)s:%(message)s'
DEFAULT_RESPONSE = "Not sure what you mean. Try *give me a drake fact*, or *tell <name> they tha best*"

# Solution-specific constants
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

# Global variables
Eliza_Mode = 0
Therapist = None
Slack_Interface = None


def random_drake_fact():
	afile = open(DRAKE_FACT_FILE)
	line = next(afile)
	for num, aline in enumerate(afile):
		if random.randrange(num + 2): continue
		line = aline
	return line


def respond_to_message(command: str):
    global Eliza_Mode, Therapist
    response = ''

    if Therapist is None:
        # instantiate eliza
	    Therapist = eliza.eliza()

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
            response = "Only partly.  I only love my bed and momma; I'm sorry."
        elif DRAKE_REGEXES["eliza_on"].match(command):
            Eliza_Mode = 1
            response = Therapist.respond("Hello")
        elif DRAKE_REGEXES["eliza_off"].match(command):
            Eliza_Mode = 0
            response = Therapist.respond("quit")
        else:
            if Eliza_Mode is 1:
                response = Therapist.respond(command)
            else:
                response = DEFAULT_RESPONSE
    except Exception as e:
        response = "I have crashed! Help!"
        logging.error(str(e))

    return response


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

    Slack_Interface = drakebot.drakebot(ENV.SLACK_BOT_TOKEN, respond_to_message)

    Slack_Interface.start()
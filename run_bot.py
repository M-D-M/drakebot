import re
import sys
import logging
import drakebot
import CONFIG 

sys.path.append('/var/tmp/share')
import ENV

# Constants
LOGGING_FMT='%(levelname)s [%(asctime)s] %(name)s:%(message)s'
DEFAULT_RESPONSE = "Not sure what you mean. Try *help* or *update*."


# Global variables
Slack_Interface = None
Response_Regex = []


def get_help(message: str):
    response_message = "Usage:\n\n"

    for regex_cfg_item in Response_Regex:
        response_message += "{0}: {1}\n".format(
            regex_cfg_item['regex']
            ,regex_cfg_item['desc']
        )

    return response_message


def get_status(message: str):
    response_message = ENV.callShellCmd('./ark_helper_scripts/getServersOnline.bash')
    return response_message


def update_servers(message: str):
    response_message = "Under construction."
    return response_message


def restart_servers(message: str):
    response_message = "Under construction."
    return response_message


def stop_servers(message: str):
    response_message = "Under construction."
    return response_message


def respond_to_message(message: str):
    response = ''

    logging.debug(f'Passed string: {message}')

    try:
        for regex_cfg_item in Response_Regex:
            if re.search(regex_cfg_item['regex'], message):
                logging.info('Match found! Executing function for regex "{}".'.format(regex_cfg_item['regex']))

                if (not callable(regex_cfg_item['function'])):
                    raise Exception('{} is not a callable function!'.format(regex_cfg_item['function']))

                response = regex_cfg_item['function'](message)
                break
    except Exception as e:
        response = "I have crashed! Help!"
        logging.error(str(e))

    if response == '':
        response = DEFAULT_RESPONSE

    return response


if __name__ == "__main__":
    logging_vars = {
        'format': LOGGING_FMT
    }
    if (CONFIG.DEBUG):
        logging_vars.update({
            'level': logging.DEBUG
        })
    else:
        logging_vars.update({
            'level': logging.INFO
            ,'filename': 'bot_output.log'
        })
    logging.basicConfig(**logging_vars)

    # Solution-specific constants
    Response_Regex = [{
        'desc': 'Returns a status of running ARK servers.'
        ,'regex': 'status'
        ,'function': get_status
    },{
        'desc': 'Update ARK server code.'
        ,'regex': 'update'
        ,'function': update_servers
    },{
        'desc': 'Restart ARK servers, if they are running, or starts them if they are not.'
        ,'regex': 'restart'
        ,'function': restart_servers
    },{
        'desc': 'Stop ARK servers, if they are running.'
        ,'regex': 'stop'
        ,'function': stop_servers
    },{
        'desc': 'Displays this help message.'
        ,'regex': 'help'
        ,'function': get_help
    }]

    Slack_Interface = drakebot.drakebot(CONFIG.SLACK_BOT_TOKEN, respond_to_message)
    Slack_Interface.start()

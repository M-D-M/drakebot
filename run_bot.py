import re
import sys
import os
import platform
import logging
import drakebot
import CONFIG 

if (platform.system() != 'Windows'):
    sys.path.append('/var/tmp/share')
    import ENV

# Constants
LOGGING_FMT='%(levelname)s [%(asctime)s] %(name)s:%(message)s'
DEFAULT_RESPONSE = "Not sure what you mean. Try *help* or *update <password>*."
ARK_SHELL_SCRIPTS_DIR = 'ark_helper_scripts' 


# Global variables
Slack_Interface = None
Response_Regex = []
ARK_Server_Password = ''
ARK_SHELL_SCRIPTS_PATH = ''
Command_Currently_Being_Executed = None


def post_message(message: str, payload):
    payload['web_client'].chat_postMessage(
        channel=payload['data']['channel']
        ,text = message
        # ,thread_ts = thread_ts
    )


def get_help(regex_search_obj, payload):
    response_message = "*Interact with me via the below commands.* (Replace _<password>_ with the ARK server password you use to login.)\n\n"

    for regex_cfg_item in Response_Regex:
        response_message += "{0}\n".format(
            regex_cfg_item['desc']
        )

    return response_message


def get_status(regex_search_obj, payload):
    response_message = ENV.callShellCmd(os.path.join(ARK_SHELL_SCRIPTS_PATH, 'getServersOnline.bash'))
    return response_message


def update_servers(regex_search_obj, payload):
    if regex_search_obj[1] == ARK_Server_Password:
        post_message('Beginning ARK update!', payload)
        response_message = "Under construction."
    else:
        response_message = 'Password does not match! Try again.'

    return response_message


def restart_servers(regex_search_obj, payload):
    if regex_search_obj[1] == ARK_Server_Password:
        post_message('Beginning ARK update!', payload)
        response_message = "Under construction."
    else:
        response_message = 'Password does not match! Try again.'

    return response_message


def stop_servers(regex_search_obj, payload):
    if regex_search_obj[1] == ARK_Server_Password:
        post_message('Beginning ARK update!', payload)
        response_message = "Under construction."
    else:
        response_message = 'Password does not match! Try again.'

    return response_message


def respond_to_message(message: str, payload = None):
    global Command_Currently_Being_Executed
    response = ''

    logging.debug(f'Passed string: {message}')

    try:
        for regex_cfg_item in Response_Regex:
            regex_search_obj = re.search(regex_cfg_item['regex'], message)
            if (regex_search_obj is not None):
                logging.info('Match found! Executing function for regex "{}".'.format(regex_cfg_item['regex']))

                if (not callable(regex_cfg_item['function'])):
                    raise Exception('{} is not a callable function!'.format(regex_cfg_item['function']))
                if (Command_Currently_Being_Executed is None):
                    Command_Currently_Being_Executed = {
                        "command": regex_search_obj[0]
                        ,"user": payload['data']['user']
                    }
                    logging.debug(f'Storing command: {Command_Currently_Being_Executed}')

                    response = regex_cfg_item['function'](regex_search_obj, payload)

                    logging.debug('Clearing stored command...')
                    Command_Currently_Being_Executed = None
                else:
                    response = f'Sorry, the command "{Command_Currently_Being_Executed["command"]}" is currently being executed by "{Command_Currently_Being_Executed["user"]}".' 

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
        'desc': 'Returns a status of running ARK servers. Usage: "@ARK Bot status"'
        ,'regex': r'status'
        ,'function': get_status
    },{
        'desc': 'Update ARK server code. "@ARK Bot update <password>"'
        ,'regex': r"update (\w+)"
        ,'function': update_servers
    },{
        'desc': 'Restart ARK servers, if they are running, or starts them if they are not. Usage: "@ARK Bot restart <password>"'
        ,'regex': r"restart (\w+)"
        ,'function': restart_servers
    },{
        'desc': 'Stop ARK servers, if they are running. Usage "@ARK Bot stop <password>"'
        ,'regex': r"stop (\w+)"
        ,'function': stop_servers
    },{
        'desc': 'Displays this help message. Usage: "@ARK Bot help"'
        ,'regex': r'help'
        ,'function': get_help
    }]

    # Get ARK shell helper scripts dir path
    ARK_SHELL_SCRIPTS_PATH = os.path.join(os.path.dirname(__file__), ARK_SHELL_SCRIPTS_DIR)

    # Get ARK Server Password from ARK config files
    # Under construction; for now just get hardcoded password in local CONFIG.py file
    ARK_Server_Password = CONFIG.ARK_PASSWORD

    Slack_Interface = drakebot.drakebot(CONFIG.SLACK_BOT_TOKEN, respond_to_message)
    Slack_Interface.start()

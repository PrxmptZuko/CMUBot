import random

#basic response function for bot
def handle_response(message) -> str:
    p_message = message.lower()

    if p_message == 'hello':
        return 'Hey there!'
    
    if p_message == '!roll':
        return str(random.randint(1,10))
    # should build this out so when someone does !help they will be given options to contact mod or create ticket, something along those lines.
    if p_message == '!help':
        return "'This is a help message that you can modify.'"
    
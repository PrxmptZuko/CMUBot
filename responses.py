import random

def handle_response(message, AD='') -> str:
    """Basic response functionality for bot"""
    p_message = message.lower()

    if p_message == 'hello':
        return 'Hey there!'
    
    if p_message == '!roll':
        return str(random.randint(1,10))

    if '!look' in p_message:
        # Looks up a user from a provided global ID.
        
        # Strips the first part of the command
        user = p_message.replace('!look ','')

        # Error handling in case a global ID doesn't exist
        try:
            user_description = AD.look_up_user(user)
        except Exception as error:
            return f'An error has occured: {error}'
        else:
            return f"User: {user}\nDescription: {user_description}"

    if p_message == '!help':
        # TODO Add options to contact a mod or create a support ticket
        return "'This is a help message that you can modify.'"
    
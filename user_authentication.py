import re
import random

from email_validator import validate_email, EmailNotValidError

"""

Steps to use this module:
1. import the file
    from user_authentication import get_email, check_ad
2. Feed in a message to get_email
    email = get_email(message.content.lower())
        will return either the provided email or None for error handling
3. Take that email and run it through AD
    user_description = check_AD(bot.AD, email)

"""

def _test_email(email):
    """Validates the provided email is real"""

    try:
        test_email = validate_email(email=email, check_deliverability=True)
    except EmailNotValidError as e:
        print('Error in _test_email')
        return None
    else:
        return test_email.normalized

def get_email(message):
    """Uses regex to grab an email address from a message"""

    try:
        # provided_email = re.search(r"[a-z0-9._%+-]+\@[a-z0-9._%+-]+\.[a-z]{2,3}", message.content.lower()).group()
        provided_email = re.search(r"[a-z0-9._%+-]+\@[a-z0-9._%+-]+\.[a-z]{2,3}", message).group()
    except AttributeError:
        print('Error encountered in get_email')
        return None
    else:
        # email = _test_email(provided_email)
        email = provided_email
        return email
    
def check_AD(AD, email):
    """Cross checks the provided email against AD records"""
    
    email_parts = email.split('@', 1)

    if email_parts[1] != 'cmich.edu':
        user_description = 'Community'
    else:
        user_description = AD.look_up_user(email_parts[0])
    
    return user_description

def create_auth_code():
    auth_code = ''
    for _ in range(5):
        auth_code += str(random.randint(0, 9))
    return auth_code

def confirm_auth_code(message_history, user_id):
    """Goes through the last 50 messages to see if an authorization code was sent to a user"""
    
    # Important variables
    auth_message_sent = False
    auth_code = None
    target_msg = None

    for msg in message_history:
        if msg.embeds:
            embed = msg.embeds[0].to_dict()
            if str(user_id) in embed['description']:
                auth_message_sent = True
                auth_code = re.search(r"\b[0-9]{5}$", embed['description']).group()
                target_msg = msg
                break
    return auth_message_sent, auth_code, target_msg
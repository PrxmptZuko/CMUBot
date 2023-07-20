import re

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
        return None
    else:
        return test_email.normalized

def get_email(message):
    """Uses regex to grab an email address from a message"""

    try:
        # provided_email = re.search(r"[a-z0-9._%+-]+\@[a-z0-9._%+-]+\.[a-z]{2,3}", message.content.lower()).group()
        provided_email = re.search(r"[a-z0-9._%+-]+\@[a-z0-9._%+-]+\.[a-z]{2,3}", message).group()
    except AttributeError:
        return None
    else:
        email = _test_email(provided_email)
        return email
    
def check_AD(AD, email):
    """Cross checks the provided email against AD records"""
    
    email_parts = email.split('@', 1)

    if email_parts[1] != 'cmich.edu':
        user_description = 'Community'
    else:
        user_description = AD.look_up_user(email_parts[0])
    
    return user_description

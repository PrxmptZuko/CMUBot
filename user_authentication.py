import re
import random
import json
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart 


def _generate_authentication_code():
    """Creates an authentication code"""

    auth_code = random.randint(10000, 99999)
    return auth_code

def _find_authentication_code(message):
    """Looks for the 5 digit auth code within a message"""

    auth_code = re.search(r"[0-9]{5}", message.content).group()
    return auth_code

def create_user(member):
    """Creates a user record within the user.json file"""

    # Acts as a placeholder for future data provided by user
    user_id = str(member.id)
    user_record = {
        user_id: { 
        'email': '',
        'auth_code': ''
        }
    }
    
    # Opens the users.json file and appends a new user to the list
    with open('users.json', 'a') as file:
        json.dump(user_record, file)
        file.close()
    print('User record created')
    

def create_email(message):
    """Creates the email contents to be sent out"""

    # Grabs the provided email from the user's message using regex
    email_address = re.search(r"[a-z0-9._%+-]+\@[a-z0-9._%+-]+\.[a-z]{3}", message.content.lower()).group()
    auth_code = _generate_authentication_code()

    email_subject = "[Do Not Reply] - CMU eSports Authentication Code"
    email_body = f"Your authentication code is: \n{auth_code}"

    # This package is used for both the sent email and user info
    email_package = {
        'email_address': email_address,
        'email_subject': email_subject,
        'email_body': email_body,
        'auth_code': auth_code
    }

    return email_package

def send_email(email_package):
    """Placeholder for real email functionality later"""

    # TODO Add real functionality to this method

    sender = 'house3mm@cmich.edu'
    reciever = email_package['email_address']
    subject = email_package['email_subject']
    body = email_package['email_body']
    
    # Creat MIME message object





    print(f"Email sent to {email_package['email_address']}\nSubject: {email_package['email_subject']}\Body: {email_package['email_body']}")

def authenticate_user(message, AD):
    """Looks in the users.json file for an existing user and authenticates from there"""
    
    # Gets the current user from the users.json file
    with open('users.json', 'r') as file:
        user_data = file.readlines
        current_user = user_data[message.author.id]
        file.close()

    # Confirms the authentication code exists within the message
    auth_code = int(_find_authentication_code(message))
    if auth_code == None: 
        output_message = "Authentication failed. Please make sure to enter the correct code" 
        return output_message, None
    
    # Matches the provided auth_code with the user's stored auth_code
    if current_user['auth_code'] == auth_code:
        output_message = f"Authentication successful! Your account has been verified\nWelcome to CMU eSports Discord {message.user_id}"
        
        # Grabs the users email and checks if they used a cmich.edu email using regex
        user_email_segments = re.split(r'\@', current_user['email'])
        if user_email_segments[1] == 'cmich.edu':
            user_description = AD.look_up_user(user_email_segments[0])
        else:
            user_description = 'Community'
    else:
        output_message = "Authentication failed. Please make sure to enter the correct code" 
        user_description = None
    
    # The message to the user and necessary role based on user description within AD
    return output_message, user_description

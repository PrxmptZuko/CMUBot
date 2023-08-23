import json
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Gmail:

    def __init__(self) -> None:
        self.EMAIL, self.PASSWORD = self._get_secrets()
        self.email_connection = self._start()

        with open('authentication_email.html', 'r', encoding='utf-8') as html_file:
            self.email_content = html_file.read()
            html_file.close()

    def _start(self):
        """Initializes the SMTP email connection"""

        email_connection = smtplib.SMTP('smtp.gmail.com', 587)
        email_connection.starttls(context=ssl.create_default_context())
        email_connection.login(user=self.EMAIL, password=self.PASSWORD)
        return email_connection

    def _get_secrets(self):
        """Grabs the secret variables for the email_connection to use in its instance"""

        with open('config.json', encoding='utf-8') as file:
            data = json.load(file)
            EMAIL = data["GMAIL_EMAIL"]
            EMAIL_PASSWORD = data["GMAIL_PASSWORD"]
        file.close()

        return EMAIL, EMAIL_PASSWORD
    
    def send_message(self, auth_code: str, destination: str):
        # self.email_connection.sendmail(from_addr=self.EMAIL, to_addrs=destination, msg=message)
        # print(f'Email sent to {destination}')

        outbound_message = MIMEMultipart('alternative')
        outbound_message["Subject"] = "[DO NOT REPLY] - CMU eSports Discord Authentication"
        outbound_message['From'] = self.EMAIL
        outbound_message["To"] = destination

        plain_text = f"Hello!\nYour authentication code for the CMU eSports Discord Server is {auth_code}.\nPlease enter this code into the DM channel with Chip to authenticate your account."
        part1 = MIMEText(plain_text, "plain")
        part2 = MIMEText(self.email_content.format(auth_code), 'html')

        outbound_message.attach(part1)
        outbound_message.attach(part2)

        self.email_connection.sendmail(from_addr=self.EMAIL, to_addrs=destination, msg=outbound_message.as_string())
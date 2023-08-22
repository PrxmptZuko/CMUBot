import smtplib, ssl
import json

class Gmail:

    def __init__(self) -> None:
        self.EMAIL, self.PASSWORD = self._get_secrets()
        self.email_connection = self._start()

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
    
    def send_message(self, message, destination):
        self.email_connection.sendmail(from_addr=self.EMAIL, to_addrs=destination, msg=message)
        print(f'Email sent to {destination}')

    # TODO Message creator using an HMTL/CSS template

gmail = Gmail()
gmail.send_message('This is a test', 'schal2tl@cmich.edu')
import json
from ms_active_directory import ADDomain

"""

Steps to use this module:
1. import the file
    from active_directory import ActiveDirectory
2. Create an ActiveDirectory object
    AD = ActiveDirectory()
3. Call the look_up_user function to return a user's description
    user_description = AD.look_up_user(user)

"""

class ActiveDirectory:
    """Logs into and pulls data from Active Directory"""

    def __init__ (self):
        """Initializes the AD session"""

        self.session = self._login()

    def _login(self):
        """Logs into AD using the saved credentials"""

        with open('config.json', encoding="utf-8") as file:
            data = json.load(file)
            self.DOMAIN = data['DOMAIN']
            self.EMAIL = data['CMICH_EMAIL']
            self.PASSWORD = data['CMICH_PASSWORD']
        file.close()

        session = ADDomain(self.DOMAIN).create_session_as_user(self.EMAIL, self.PASSWORD)
        return session

    def look_up_user(self, gid):
        """Searches AD for a provided global ID and returns the user information"""
        try:
            user = self.session.find_user_by_sam_name(gid, ['givenName','sn', 'description'])
        except:
            print('Error with look_up_user')
            return 'Community', None, None
        else:
            user_description = user.get('description')[0]
            user_given_name = user.get('givenName')
            user_surname = user.get('sn')
            return user_description, user_given_name, user_surname

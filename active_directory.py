import json
from ms_active_directory import ADDomain

"""

Steps to use this module:
1. import the file
    from active_directory.py import ActiveDirectory
2. Create an ActiveDirectory object
    AD = ActiveDirectory()
3. Call the look_up_user function to return a user's description
    user_description = AD.look_up_user(user)

"""

class ActiveDirectory:
    """Logs into and pulls data from Active Directory"""

    def __init__ (self):
        """Initializes the AD session"""

        with open('config.json', encoding="utf-8") as file:
            data = json.load(file)
            self.DOMAIN = data['DOMAIN']
            self.EMAIL = data['EMAIL']
            self.PASSWORD = data['PASSWORD']
        file.close()

        self.session = ADDomain(self.DOMAIN).create_session_as_user(self.EMAIL, self.PASSWORD)

    def look_up_user(self, gid):
        """Searches AD for a provided global ID and returns the user description"""

        user=self.session.find_user_by_sam_name(gid, ['description'])
        user_description = user.get('description')[0]
        return user_description

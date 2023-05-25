from ms_active_directory import ADDomain
import json

class ActiveDirectory:
    """Class to log into and pull data from Active Directory"""

    def __init__ (self):
        """Initializes the AD session"""
        with open('config.json', 'r') as file:
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


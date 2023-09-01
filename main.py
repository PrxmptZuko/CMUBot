# Native modules
import time
import json

# Discord specific modules
import discord
from discord.ext import commands

# Custom modules
from active_directory import ActiveDirectory
import user_authentication as user_auth
from gmail import Gmail

class CMUBot(commands.Bot):
    """Creates the Discord bot"""

    def __init__(self):
        """Initializes the bot with intents, an AD session, and secrets"""
        super().__init__(command_prefix='!',intents=intents)
        self.AD = ActiveDirectory() # Temporarily disabled
        self.TOKEN, self.GUILD = self._get_secrets()
        self.GMAIL = Gmail()

        self.ROLES = {
            'Alumnus': 'Alumni',
            'Student': 'Student',
            'Prospect': 'Prospective Student',
            'Staff': 'Faculty/Staff',
            'Community': 'Community Members',
        }

    def _get_secrets(self):
        """Grabs the secret variables for the bot to use in its instance"""
        with open('config.json', encoding='utf-8') as file:
            data = json.load(file)
            TOKEN = data["TOKEN"]
            GUILD = data["GUILD"]
        file.close()

        return TOKEN, GUILD
    
    async def on_ready(self):
        """Flag to say the bot is ready for use"""
        print(f'{self.user} is now running!')

# Sets the bot intents (Needs to be outside the CMUBot class)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Initializes the bot
bot = CMUBot()

@bot.event
async def on_member_join(member):
    """Currently only listens for new members and sends a welcome message after a short delay"""

    if member == bot.user:
        return

    welcome_message = "Welcome to the Official Central Michigan Esports Discord! Please provide your CMU or personal email address for authentication."
    time.sleep(10) # A small delay between joining the server and bot message
    await member.send(welcome_message)
    print(f'Welcome message sent to {member.id}')

@bot.event
async def on_message(message):
    """Listens for messages from the user"""
    if message.author == bot.user:
        return

    # Only used if the message channel is a DM
    if isinstance(message.channel, discord.DMChannel):
        # Connects to the server from the DM channel and preps user for role
        server = bot.get_guild(bot.GUILD)
        member = server.get_member(message.author.id)

        # Cuts off communication between the bot and user if role is already granted
        authenticated = False
        server_roles = server.roles
        for server_role in server_roles:
            if server_role.name == 'Mod 🛠': # Exception roles for testing
                authenticated = False
                break
            if member.get_role(server_role.id):
                authenticated = True
        
        # Boolean for managing authentication section of isinstance
        if not authenticated:

            # Gets the message history from mod channel and checks for existing auth codes for user
            moderation_channel = bot.get_channel(1143918140519100507)
            message_history = [message async for message in moderation_channel.history(limit=50)]
            auth_message_sent, auth_code, target_msg = user_auth.confirm_auth_code(message_history, message.author.id)
            
            if auth_message_sent: # An authorization message was sent to the user
                if auth_code in message.content:
                    await target_msg.add_reaction('👍') # Confirmation user has been authenticated
                    
                    email = user_auth.get_email(target_msg.embeds[0].to_dict()['description'])
                    user_description = user_auth.check_AD(bot.AD, email)

                    role_name = bot.ROLES[user_description]
                    
                    # Sets the role for the user
                    role = discord.utils.get(server.roles, name=role_name)
                    await member.add_roles(role)

                    await member.send(f'Thank you! You have been granted the {role_name} role.')
                    print(f'Role of {role_name} granted to {member.id}')

            else: # An authorization message does not exist for the user
                
                # Gets the email from a message
                email = user_auth.get_email(message.content.lower())

                # Error handling if an email wasn't found or not a real email address
                if email is None:
                    error_message = "An error was detected regarding your email. Please double check your email was spelled correctly and try again."
                    await message.channel.send(error_message)
                else:
                    # Creates an auth code and sends user an email
                    auth_code = user_auth.create_auth_code()
                    bot.GMAIL.send_message(auth_code, email)

                    # Message to mod channel for logging new user
                    moderation_message = f"{message.author.name} - {message.author.id}\n{email}\n{auth_code}"
                    new_user_embed = discord.Embed(title='New User Added', description=moderation_message)
                    await moderation_channel.send(embed=new_user_embed)

                    # Message to user explaining next steps
                    message_for_user = 'Thank you!\n A message was sent to the provided email address containing your unique authorization code. The message will be coming from cmichesportsbot@gmail.com so make sure to check your inbox and spam folder. Respond to this message with your code to continue the authorization process.'
                    await member.send(message_for_user)
    
    # TODO Add in ticketing system
    # if message.content.startswith('!ticket'):
    #     ticket_channel_id = 1124065175172042853
    #     ticket_channel = bot.get_channel(ticket_channel_id)

    #     log_history = [msg async for msg in ticket_channel.history(limit=50)]



if __name__=='__main__':
    bot.run(bot.TOKEN)

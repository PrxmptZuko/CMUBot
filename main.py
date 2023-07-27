# Native modules
import time
import json

# Discord specific modules
import discord
from discord.ext import commands

# Custom modules
from active_directory import ActiveDirectory
from user_authentication import get_email, check_AD

class CMUBot(commands.Bot):
    """Creates the Discord bot"""

    def __init__(self):
        """Initializes the bot with intents, an AD session, and secrets"""
        super().__init__(command_prefix='!',intents=intents)
        self.AD = ActiveDirectory()
        self.TOKEN, self.GUILD = self._get_secrets()

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

    print(f"\n{member} has joined the server")
    time.sleep(10) # A small delay between joining the server and bot message
    print(f'DM sent to {member}')

    await member.send(welcome_message)

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
        server_roles = server.roles
        for server_role in server_roles:
            if server_role.name == 'Moderator': # Exception roles for testing
                continue
            if member.get_role(server_role.id):
                return
        
        # Gets the email from a message
        email = get_email(message.content.lower())

        # Error handling if an email wasn't found or not a real email address
        if email is None:
            error_message = "An error was detected regarding your email. Please double check your email was spelled correctly and try again."
            await message.channel.send(error_message)
        else:
            user_description = check_AD(bot.AD, email)

            # Currently only 2 roles but can be expanded later.
            if user_description == 'Community':
                role_name = 'Community'
            else:
                role_name = 'CMU'
            
            # Sets the role for the user
            role = discord.utils.get(server.roles, name=role_name)
            await member.add_roles(role)

            await member.send(f'Thank you! You have been granted the {role_name} role.')


if __name__=='__main__':
    bot.run(bot.TOKEN)

# Native modules
import time
import json

import random
# Discord specific modules
import discord
from discord.ext import commands

import asyncio, os, datetime
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

# Initializes bot and active directory sessions.
AD = ActiveDirectory()

#defining prefix ! to run bot 
intents = discord.Intents.default()
intents.message_content = True 
intents.members = True 
bot = commands.Bot(command_prefix="!", intents=intents)

# independant message sent by the bot in either a private DM or returning output to original channel
async def send_message(message, user_message, is_private):
    try:
        response = response.handle_response(user_message, AD)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as error:
        print(error)

def get_token_from_file(TOKEN):
    with open(TOKEN, "r") as file:
        data = json.load(file)
        token = data["TOKEN"]
        return token

# Activates bot
def run_discord_bot():
    TOKEN = get_token_from_file("config.json")
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    return bot, TOKEN

bot, TOKEN = run_discord_bot()

@bot.event
async def on_ready():
# Print the invite link and the integer value of the permissions
    
    print(f"Permissions Integer Value: {integer_value}")
    # print(f"Invite Link: {invite_link}")
    print(f'{bot.user} is now running!')

# Sets the bot intents (Needs to be outside the CMUBot class)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

#init permissions for bot 
permissions = discord.Permissions()
permissions.read_messages = True 
permissions.send_messages = True
#gets the integer value of the permissions and prints to terminal
integer_value = permissions.value

# store user data with user_id as the key and authentication code as the value
user_data = {}

# Dictionary to store help ticket data
help_tickets = {}

#Ticket convo init dictionary for storing !ticket convos 
ticket_conversations = {}
Now = datetime.datetime.now()

# Initializes the bot
bot = CMUBot()
@bot.event
async def on_member_join(member):
    """Currently only listens for new members and sends a welcome message after a short delay"""

    if member == bot.user:
        return

    guild = member.guild
    #The default welcome channel (usually #general)
    channel = guild.system_channel 

    if channel is not None:
        # Retrieve the last message in the channel
        async for message in channel.history(limit=1):
            last_message = message

         # Ignore the event if the last message was sent by the bot
        if last_message and last_message.author == bot.user:
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

    print('Starting ticket process')
    if message.content.startswith("!ticket"):
        # Generate a case number
        print('ticket process Started')
        case_number = len(help_tickets) + 1

        # Get the ticket channel
        print('Fetching ticket channel')
        ticket_channel = bot.get_channel(TICKET_CHANNEL_ID)
        if ticket_channel is None:
            await message.author.send("Ticket channel not found. Please contact an administrator.")
            return

        print('Storing user info for ticket')
        # Store the user ID and thread in the help_tickets dictionary
        help_tickets[case_number] = {
            "user_id": message.author.id,
            "temp_channel": None  # Initialize with None
        }

        # Send the case number to the user
        print('sent user case number')
        await message.author.send(f"Your case number is {case_number}. \nYou will receive a @ mention when a moderator accepts your case.")

        # Log the case number in the moderation and log channels
        print('sends ticket case and user id to mod and log channel')
        mod_channel = bot.get_channel(MODERATION_CHANNEL_ID)
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        await mod_channel.send(f"New ticket created. Case #{case_number}. User: {message.author}")
        await log_channel.send(f"New ticket created. Case #{case_number}. User: {message.author}")


        if isinstance(message.channel, discord.DMChannel) and message.author != bot.user:
            user_id = message.author.id

        with open('users.json', 'r') as file:
            user_data = json.load(file)

        if user_id not in user_data:
            email_package = user_auth.create_email(message)

            user_data[user_id]={
            'email':email_package['email_address'],
            'auth_code':email_package['auth_code']
        }
            file.close()

            user_auth.send_email(email_package)

            reply_message = ("Thank you for providing your email address.\n"
                            f"An email has been sent to {email_package['email_address']} with your authorization code")
            await message.channel.send(reply_message)
        else: 
            reply_message, role = user_auth.authenticate_user(message, AD)

            await message.channel.send(reply_message)

    print ('checks for new user response')
    # check if the message is from a new user in private message
    if isinstance(message.channel, discord.DMChannel) and message.author != bot.user:
        user_id = message.author.id

    # #check if the user already has auth code
    #     with open('users.json', 'r') as file:
    #         user_data = json.load(file)

    #     if user_id not in user_data:
    #         email_package = user_auth.create_email(message)

    #         user_data[user_id]={
    #         'email':email_package['email_address'],
    #         'auth_code':email_package['auth_code']
    #     }
    #         file.close()

    #         user_auth.send_email(email_package)

    #         reply_message = ("Thank you for providing your email address.\n"
    #                         f"An email has been sent to {email_package['email_address']} with your authorization code")
    #         await message.channel.send(reply_message)
    #     else: 
    #         reply_message, role = user_auth.authenticate_user(message, AD)

    #         await message.channel.send(reply_message)

        print ('looks for ! prefix')
    elif message.content.startswith("!"):
        await bot.process_commands(message)
    else: 
        return

    #process commands from message
    username = str(message.author)
    user_message = str(message.content)
    channel = str(message.channel)

    print(f'{username} said: "{user_message}" ({channel})')

    print ('checks for ? prefix incase')
    if user_message.startswith('?'):
        user_message = user_message[1:] 
        await send_message(message, user_message, is_private=True)
    else:
        await send_message(message, user_message, is_private=False)

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

                    # Help Ticket creation !ticket
@bot.command()
async def casenumber(ctx, case_number: int):
    if case_number in help_tickets:
        # Get the user ID for the case number
        print('put case # to user id')
        user_id = help_tickets[case_number]["user_id"]
        user = bot.get_user(user_id)

        # Create a temporary text channel with the user
        print('creating temp channel')
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True)
        }
        print('create temp channel')
        temp_channel = await ctx.guild.create_text_channel(f"ticket-{case_number}", overwrites=overwrites)

        print('fetching mod roles')
        # Get the moderator roles
        moderator_roles = [role for role in ctx.guild.roles if role.id in [1093914220178984960]]  # Server moderation role id

        print('@ user and mods in temp channel')
        # Mention the user and moderator roles in the temp channel
        mention_text = f"{user.mention} {' '.join(role.mention for role in moderator_roles)}"
        await temp_channel.send(mention_text)

# Store the temporary channel in the help_tickets dictionary
        print('store temp channel')
        help_tickets[case_number]["temp_channel"] = temp_channel

        # Send a message to the moderator and the log channel
        print('sent ticket info to channels')
        mod_channel = bot.get_channel(MODERATION_CHANNEL_ID)
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        await mod_channel.send(f"Opened case #{case_number}. User: {user}")
        await log_channel.send(f"Opened case #{case_number}. User: {user}")
    else:
        print('invalid case number')
        await ctx.send("Invalid case number.")

#resolving tickets !resolve [casenumber]
@bot.command()
async def resolve(ctx, case_number: int):
    if case_number in help_tickets:
        temp_channel = help_tickets[case_number]["temp_channel"]

        # Send a message to the moderator and the log channel
        print('sent resolve msg')
        mod_channel = bot.get_channel(MODERATION_CHANNEL_ID)
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        await mod_channel.send(f"Resolved case #{case_number}.")
        await log_channel.send(f"Resolved case #{case_number}.")

        # Send a message to the user in the temporary channel
        user = bot.get_user(help_tickets[case_number]["user_id"])
        await user.send(f"Your ticket (case #{case_number}) has been resolved.")

        # Close the temporary channel and remove it from the help_tickets dictionary
        print('closing temp channel')
        await temp_channel.send("Your ticket has been resolved. Closing this channel.")
        del help_tickets[case_number]
        await temp_channel.delete()
    else:
        print('invalid case number')
        await ctx.send("Invalid case number.")

#cancel ticket !cancel [casenumber]
@bot.command()
async def cancel(ctx, case_number: int):
    print('canceling ticket')
    if case_number in help_tickets:
        temp_channel = help_tickets[case_number]["temp_channel"]

        # Send a message to the moderator and the log channel
        print('sent cancel msg')
        mod_channel = bot.get_channel(MODERATION_CHANNEL_ID)
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        await mod_channel.send(f"Cancelled case #{case_number}.")
        await log_channel.send(f"Cancelled case #{case_number}.")

        # Send a message to the user in the temporary channel
        user = bot.get_user(help_tickets[case_number]["user_id"])
        await user.send(f"Your ticket (case #{case_number}) has been cancelled.")

        # Close the temporary channel and remove it from the help_tickets dictionary
        print('closing temp channel')
        await temp_channel.send("Your ticket has been cancelled. Closing this channel.")
        del help_tickets[case_number]
        await temp_channel.delete()
    else:
        print('invalid case number')
        await ctx.send("Invalid case number.")

    @bot.command(name= "namechange")
    async def namechange(ctx):
    # if message.startswith("!namechange"):
        print("Sending message to Mod channel")
        mod_channel = bot.get_channel(MODERATION_CHANNEL_ID)
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        await mod_channel.send(f"User {ctx.author} has requested a name change.")
        await log_channel.send(f"User {ctx.author} requested a name change.") 

#dont worry about it
@bot.command(name= "coolguy")
async def cool_guy(ctx):
    print("Telling everyone who a cool guy is.")
    general_channel = bot.get_channel(GENERAL_CHANNEL_ID)
    await general_channel.send(f"Hey everyone! {ctx.author} just wanted to remind yall that Matt is a cool guy. despite what the government says ;)")

#sends random meme from file
@bot.command(name= "meme")
async def random_image(ctx):
    print("Pulling a random image")
    with open('meme_images/sait.jpg', 'rb') as f:
        picture = discord.File(f)
        await ctx.send(file=picture)

#list server bot commands !commands
@bot.command(name="commands")
async def list_commands(ctx):
    commands_list = [
        "!ticket: Creates a new help ticket.",
        "!namechange: Will notify mods to your request to change sever name."
    ]

    help_message = "\n".join(commands_list)
    await ctx.send(f"Here are the available commands:\n{help_message}")

#list server bot commands !commands
@bot.command(name="mod")
async def list_commands(ctx):
    commands_list = [
        "!ticket: Creates a new help ticket.",
        "!casenumber [casenumber]: opens ticket and temp channel",
        "!resolve [case_number]: Resolves a help ticket.",
        "!cancel [case_number]: Cancels a help ticket.",
        "!namechange: Will notify mods to your request to change sever name.",
        "!coolguy: Will let you know whos the coolguy",
        "!mod: shows list of commands mods will use"
    ]

    help_message = "\n".join(commands_list)
    await ctx.send(f"Here are the available commands mods use:\n{help_message}")



#Constants
MODERATION_CHANNEL_ID = 1093257930356293773
LOG_CHANNEL_ID = 1096277903773282345
moderation_role_id = 1093914220178984960
TICKET_CHANNEL_ID = 1096277903773282345
GENERAL_CHANNEL_ID = 1096173041559539723
# bot_permissions = 534723951680


if __name__=='__main__':
    bot.run(bot.TOKEN)

# git config --global user.email "you@example.com"
#   git config --global user.name "Your Name"
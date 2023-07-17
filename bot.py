import discord, responses, json, random
from active_directory import ActiveDirectory
from discord.ext import commands
# from discord_slash import SlashCommand
from discord.ui import Button, View

import user_authentication

# Initializes bot and active directory sessions.
AD = ActiveDirectory()

#defining prefix ! to run bot 
intents = discord.Intents.default()
intents.message_content = True 
intents.members = True 
bot = commands.Bot(command_prefix="!", intents=intents)

#setting permissions for bot
permissions = discord.Permissions()
permissions.read_messages = True 
permissions.send_messages = True
#gets the integer value of the permissions and prints to terminal
integer_value = permissions.value

# invite_link = discord.utils.oauth_url(1108466431068229643, permissions=integer_value)
# slash = SlashCommand(bot, sync_commands=True)
# store user data with user_id as the key and authentication code as the value
user_data = {}


# independant message sent by the bot in either a private DM or returning output to original channel
async def send_message(message, user_message, is_private):
    try:
        response = responses.handle_response(user_message, AD)
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

# join logic - needs authentication process to prompt to user in private DM

@bot.event
async def on_member_join(member):
    if member == bot.user:
        return
    # if message.content == f"Welcome {member.name}!":
    #     return

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

    welcome_message = "Welcome to the Official Central Michigan Esports Discord! Please provide your email address for authentication:"
    try:
        if welcome_message:
            # Creates a user record within users.json
            user_authentication.create_user(member)
            await member.send(welcome_message)
    except discord.Forbidden:
        print(f"Failed to send a private message to {member}.")

@bot.event 
async def on_message(message):
    if message.author == bot.user:
        return

    # check if the message is from a new user in private message
    if isinstance(message.channel, discord.DMChannel) and message.author != bot.user:
        user_id = message.author.id

        #check if the user already has auth code
        with open('users.json', 'r') as file:
            user_data = json.load(file)

        if user_id not in user_data:
            email_package = user_authentication.create_email(message)

            user_data[user_id]={
            'email':email_package['email_address'],
            'auth_code':email_package['auth_code']
        }
            file.close()

            user_authentication.send_email(email_package)

            reply_message = ("Thank you for providing your email address.\n"
                            f"An email has been sent to {email_package['email_address']} with your authorization code")
            await message.channel.send(reply_message)
        else: 
            reply_message, role = user_authentication.authenticate_user(message, AD)

            # TODO assign a user role based on the role variable

            await message.channel.send(reply_message)
        
    elif message.content.startswith("!"):
        await bot.process_commands(message)
    else: 
        # Handle normal messages with the handle_response function
        reply = responses.handle_response(message.content, AD)
        await message.channel.send(reply)
        return
    #process commands from message
    await bot.process_commands(message)

# When message is sent into a channel that the bot has access to -
# @client.event logs user chat msg to check if its a "!command", if so, Calls the 'send_message' function to send response to user

    username = str(message.author)
    user_message = str(message.content)
    channel = str(message.channel)

    print(f'{username} said: "{user_message}" ({channel})')

    # if user_message.startswith('?'):
    #     user_message = user_message[1:] 
    #     await send_message(message, user_message, is_private=True)
    # else:
    #     await send_message(message, user_message, is_private=False)

# Help Ticket creation 

#Constants

MODERATION_CHANNEL_ID = 1126969936082894988
LOG_CHANNEL_ID = 1128764737170178073
moderation_role_id = 1126249291875369070
bot_permissions = 534723951680

#ticket data
case_number = 1
active_ticket = {}

@bot.command()
async def ticket(ctx):
    # Check if the command is run in a guild (server) text channel
    if isinstance(ctx.channel, discord.TextChannel):
        #send DM to user with ticket selection menu
        select_menu = discord.ui.Select(
            placeholder='Select a ticket type',
            options=[
                discord.SelectOption(label='Issue',value='issue'),
                discord.SelectOption(label='Question',value='question')
            ]
        )
        select_view = discord.ui.View()
        select_view.add_item(select_menu)
        try:
            dm_channel = await ctx.author.create_dm()
            await dm_channel.send('Please select a ticket type:', view=select_view)
        except Exception as e:
            print(F'Failed to send DM to {ctx.author}: {e}')

@bot.event
async def on_select_option(interaction):
    if interaction.component.custom_id == 'ticket_selection':
        selected_ticket_type = interaction.values[0]
        global case_number
        case_id = case_number
        case_number += 1
        #create ticket object
        ticket = {
            'case_id': case_id,
            'ticket_type': selected_ticket_type,
            'user_id': interaction.user_id,
            'channel_id': None,
            'moderator_id': None
        }

        active_ticket[case_id] = ticket
        
        #send ticket information to the moderation channel
        moderation_channel = bot.get_channel(MODERATION_CHANNEL_ID)
        if moderation_channel is None:
            print('Failed to find moderation channel')
            return
        ticket_info = f'Ticket {case_id} | Type: {selected_ticket_type} | User: <@{interaction.user.id}>'
        await moderation_channel.send(ticket_info)

        #Log Ticket Creation
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel is not None:
            await log_channel.send(f'Ticket {case_id} created by <@{interaction}')

        #Create Temporary text channel for the ticket
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.get_role(interaction.uswer.id): discord.PermissionOverwrite(read_messages=True),
            guild.get_role(moderation_role_id): discord.PermissionOverwrite(read_messages=True)
        }
        ticket_channel = await guild.create_text_channel(f'ticket-{case_id}', overwrites=overwrites)
        ticket['channel_id'] = ticket_channel.id
        active_ticket[case_id] = ticket

#Ticket Cancellation 
@bot.command()
async def cancel_ticket(ctx):
    if isinstance(ctx.channel, discord.TextChannel) and ctx.channel.id in [ticket['channel_id'] for ticket in active_ticket.values()]:
        ticket_channel = ctx.channel
        case_id = int(ticket_channel.name.split('-')[-1].strip())

        if case_id in active_ticket:
            ticket = active_ticket[case_id]

            #log ticket cancelation 
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            if log_channel is not None:
                await log_channel.send(f'Ticket {case_id} was canceled by <@{ctx.author.id}')

            #Delete temp channel
            await ticket_channel.delete()

            #remove the ticket from active_tickets
            active_ticket.pop(case_id, None)

            #Send cancelation message to user 
            user = await bot.fetch_user(ticket['user_id'])
            if user is not None:
                await user.send(f'Your ticket (case {case_id}) has been canceled. Thank you!')
                

if __name__ == '__main__':
    bot.run(TOKEN)

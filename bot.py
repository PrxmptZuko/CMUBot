import discord, responses, json, random
from active_directory import ActiveDirectory
from discord.ext import commands
from discord.ui import Button, View

import user_authentication


# Initializes bot and active directory sessions.

AD = ActiveDirectory()

#defining prefix ! to run bot 
intents = discord.Intents.default()
intents.message_content = True 
intents.members = True 
bot = commands.Bot(command_prefix="!", intents=intents)

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
    client = discord.Client(intents=intents)
    return client, TOKEN

client, TOKEN = run_discord_bot()

@client.event
async def on_ready():
    print(f'{client.user} is now running!')




# join logic - needs authentication process to prompt to user in private DM

@client.event
async def on_member_join(member):
    if member == client.user:
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
        if last_message and last_message.author == client.user:
            return

    welcome_message = "Welcome to the Official Central Michigan Esports Discord! Please provide your email address for authentication:"
    try:
        if welcome_message:
            # Creates a user record within users.json
            user_authentication.create_user(member)
            await member.send(welcome_message)
    except discord.Forbidden:
        print(f"Failed to send a private message to {member}.")

@client.event 
async def on_message(message):
    if message.author == client.user:
        return
    
    # check if the message is from a new user in private message
    if isinstance(message.channel, discord.DMChannel) and message.author != client.user:
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

# When message is sent into a channel that the bot has access to -
# @client.event logs user chat msg to check if its a "!command", if so, Calls the 'send_message' function to send response to user

    username = str(message.author)
    user_message = str(message.content)
    channel = str(message.channel)

    print(f'{username} said: "{user_message}" ({channel})')

    if user_message.startswith('?'):
        user_message = user_message[1:] 
        await send_message(message, user_message, is_private=True)
    else:
        await send_message(message, user_message, is_private=False)

# Help Ticket creation 

# defaults users cant see channel, when interaction (user select create ticket) changes view permission to 'True'. role = True allows mods to see channel
async def ticketcallback(interaction):
    guild = interaction.guild
    role = discord.utils.get(guild.roles, name="Moderator")
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        interaction.user: discord.PermissionOverwrite(view_channel=True),
        role: discord.PermissionOverwrite(view_channel=True)
    }

    # user selects either option 1 or 2 being a help ticket or something else (test)
     #edit : changed 'Select' to discord.ui.select
    select = discord.ui.select (options = [
        discord.SelectOption(label="Help Ticket", value="01", emoji="✅", description= "This will open a help ticket"),
        discord.SelectOption(label="Other Ticket", value="02", emoji="❌", description="This will open a ticket in the other section")
    ])

    # Handles ticket channel creation and sets necessary permissions 

    if select.value[0] == "01":
        category = discord.utils.get(guild.categories, name="Tickets")
        channel = await guild.create_text_channel(f"{interaction.user.name}-ticket", category=category, overwrites=overwrites)
        await interaction.response.send_message(f"Created ticket - <#{channel.id}>", ephemeral=True)
        await channel.send("Hello, how can i help you?")
    elif select.values[0] == "02":
        category = discord.utils.get(guild.categories, name= "Other Tickets")
        channel = await guild.create_text_channel(f"{interaction.user.name}-ticket", category=category, overwrites=overwrites)
        await interaction.response.send_message(f"Created ticket - <#{channel.id}>", ephemeral=True)
        await channel.send("Hello, how can i help you?")

    view = View(timeout=None)
    view.add_item(select)
    await interaction.response.send_message("Choose an option below", view=view, ephemeral=True)

# I want to test ctx (context) instead of labeling individual values. 'ctx' can pull details within commands so i want to try 
@bot.command()
async def ticket(interaction):
    button = Button(label= "📥 Create Ticket", style=discord.ButtonStyle.green)
    button.callback = ticketcallback
    view = discord.ui.View(timeout=None)
    view.add_item(button)
    await interaction.send("Open a ticket below", view=view)




if __name__ == '__main__':
    client.run(TOKEN)

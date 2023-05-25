import discord, responses, json
from active_directory import ActiveDirectory

# Initializes bot and active directory sessions.
bot = discord.Client(intents=discord.Intents.default())
AD = ActiveDirectory()

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

#Activates bot - creates instance of the client and preps connection to Discord API with TOKEN and outlines permissions
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

# barebone user join logic - needs authentication process to prompt to user in private DM

@client.event
async def on_member_join(member):
    print(f'{member} has joined the server!')

# When message is sent into a channel that the bot has access to -
# @client.event logs user chat msg to check if its a "!command", if so, Calls the 'send_message' function to send response to user

@client.event 
async def on_message(message):
    if message.author == client.user:
        return
        
    username = str(message.author)
    user_message = str(message.content)
    channel = str(message.channel)

    print(f'{username} said: "{user_message}" ({channel})')

    if user_message[0] == '?':
        user_message = user_message[1:] 
        await send_message(message, user_message, is_private=True)
    else:
        await send_message(message, user_message, is_private=False)


client.run(TOKEN)

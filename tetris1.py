import discord, responses, json, random
import discord.errors
from active_directory import ActiveDirectory
from discord.ext import commands
from discord.ui import Button, View, Select 
import asyncio
import datetime
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
#gets the integer value of the permissions and prints to terminal.
integer_value = permissions.value

# store user data with user_id as the key and authentication code as the value
user_data = {}
current_case_number = None
# Dictionary to store help ticket data
help_tickets = {}

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

# join logic
@bot.event
async def on_member_join(member):
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

    welcome_message = "Welcome to the Official Central Michigan Esports Discord! Please provide your email address for authentication:"
    try:
        if welcome_message:
            # Creates a user record within users.json
            user_authentication.create_user(member)
            await member.send(welcome_message)
    except discord.Forbidden:
        print(f"Failed to send a private message to {member}.")
        
#when message is sent to channel bot has access to
@bot.event
async def on_message(message):
    global current_case_number  # Declare the global variable
    if message.author == bot.user:
        return

    user_id = message.author.id

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

            # Log user messages
    if not message.author.bot:  # Exclude messages from bots
        if isinstance(message.channel, discord.DMChannel):
            log_conversation("tempchannel_dm",case_number, message.author.id, message.content)

        # Check if the users.json file is empty or contains valid JSON
        with open('users.json', 'r') as file:
            content = file.read()
            if content:
                user_data = json.loads(content)
            else:
                user_data = {}

        if user_id not in user_data:
            email_package = user_authentication.create_email(message)

            user_data[user_id]={
            'email':email_package['email_address'],
            'auth_code':email_package['auth_code']
        }
            file.close()

        # Log user messages including the current case number
            if current_case_number:
                log_conversation(current_case_number, message.author.id, message.content)
            user_authentication.send_email(email_package)

            reply_message = ("Thank you for providing your email address.\n"
                            f"An email has been sent to {email_package['email_address']} with your authorization code")
            await message.channel.send(reply_message)
        else: 
            reply_message, role = user_authentication.authenticate_user(message, AD)

            await message.channel.send(reply_message)
    
    print ('checks for new user response')
    # check if the message is from a new user in private message
    if isinstance(message.channel, discord.DMChannel) and message.author != bot.user:


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

            await message.channel.send(reply_message)
            
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

        # Store the temporary channel in the help_tickets dictionary
        help_tickets[case_number]["temp_channel"] = temp_channel
        
        # Log conversation in the temporary channel
        log_conversation(case_number, ctx.author.id, f"Case #{case_number} started by {ctx.author.display_name} (moderator)")

        print('fetching mod roles')
        # Get the moderator roles
        moderator_roles = [role for role in ctx.guild.roles if role.id in [1126249291875369070]]  # Server moderation role id

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

def log_conversation(case_number, user_id, message_content, is_mod=False):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {"timestamp": timestamp, "user_id": user_id, "message": message_content, "is_mod": is_mod}
    
    log_filename = f"helpticketlog_{case_number}.json" 
    with open(log_filename, "a") as log_file:
        json.dump(log_entry, log_file)
        log_file.write("\n")



#list server bot commands !commands
@bot.command(name="commands")
async def list_commands(ctx):
    commands_list = [
        "!ticket: Creates a new help ticket.",
        "!casenumber [casenumber]: opens ticket and temp channel",
        "!resolve [case_number]: Resolves a help ticket.",
        "!cancel [case_number]: Cancels a help ticket.",
        "!look [global_id]: Look up a user from their global ID.",
        "!hello: Get a friendly greeting.",
        "!roll: Roll a random number between 1 and 10."
    ]
    
    help_message = "\n".join(commands_list)
    await ctx.send(f"Here are the available commands:\n{help_message}")


#Constants
MODERATION_CHANNEL_ID = 1126969936082894988
LOG_CHANNEL_ID = 1128764737170178073
moderation_role_id = 1126249291875369070
TICKET_CHANNEL_ID = 1124065175172042853
# bot_permissions = 534723951680


##########################################################################################

# Tetris game constants and logic
GRID_WIDTH = 10
GRID_HEIGHT = 20
SHAPES = [
    [(1, 1, 1, 1)],
    # ... Define other tetromino shapes
]

# Initialize the grid and other game-related variables
grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
current_tetromino = None
current_position = (0, 0)

# Function to create a new random tetromino
def create_tetromino():
    shape = random.choice(SHAPES)
    return shape

# Function to place the current tetromino onto the grid
def place_tetromino():
    global grid, current_tetromino, current_position
    for y, row in enumerate(current_tetromino):
        for x, cell in enumerate(row):
            if cell:
                grid[current_position[0] + y][current_position[1] + x] = 1

# Function to check for collision with grid boundaries and existing blocks
def check_collision(tetromino, position):
    for y, row in enumerate(tetromino):
        for x, cell in enumerate(row):
            if cell:
                if (
                    position[0] + y >= GRID_HEIGHT or
                    position[1] + x < 0 or position[1] + x >= GRID_WIDTH or
                    grid[position[0] + y][position[1] + x]
                ):
                    return True
    return False

# Display the game grid in a text channel
async def display_grid(channel):
    game_message = ""
    for row in grid:
        game_message += "".join([":red_square:" if cell else ":white_large_square:" for cell in row]) + "\n"
    
    # Split the message into smaller chunks
    chunk_size = 10
    chunked_messages = [game_message[i:i + chunk_size] for i in range(0, len(game_message), chunk_size)]

    for chunk in chunked_messages:
        await channel.send(chunk)
        await asyncio.sleep(1)  # Delay between sending chunks

# Function to place the current tetromino onto the grid
def place_tetromino():
    global grid, current_tetromino, current_position
    for y, row in enumerate(current_tetromino):
        for x, cell in enumerate(row):
            if cell:
                grid[current_position[0] + y][current_position[1] + x] = 1

# Start the Tetris game loop
async def start_game_loop(channel):
    global current_tetromino, current_position
    while True:
        if current_tetromino is None:
            current_tetromino = create_tetromino()
            current_position = (0, GRID_WIDTH // 2 - len(current_tetromino[0]) // 2)

        new_position = (current_position[0] + 1, current_position[1])
        if not check_collision(current_tetromino, new_position):
            current_position = new_position
        else:
            place_tetromino()
            current_tetromino = None

        await display_grid(channel)
        await asyncio.sleep(1)

@bot.command()
async def starttetris(ctx):
    asyncio.create_task(start_game_loop(ctx.channel))
    await ctx.send("Tetris game started!")

                

if __name__ == '__main__':
    bot.run(TOKEN)

import random

MOD_CHANNEL_ID = 123

def handle_response(message, AD='') -> str:
    """Basic response functionality for bot"""
    p_message = message.lower()

    if p_message == 'hello':
        return 'Hey there!'
    
    if p_message == '!roll':
        return str(random.randint(1,10))

    if '!look' in p_message:
        # Looks up a user from a provided global ID.
        
        # Strips the first part of the command
        user = p_message.replace('!look ','')

        # Error handling in case a global ID doesn't exist
        try:
            user_description = AD.look_up_user(user)
        except Exception as error:
            return f'An error has occured: {error}'
        else:
            return f"User: {user}\nDescription: {user_description}"
        

async def on_message(message):
    if message.author == Client.user:
        return
    
        # ticketing to send msg to mod channel 
    if message == '!help':
        if any(role.name == 'Moderator' for role in message.author.roles):
            mod_channel = Client.get_channel(MOD_CHANNEL_ID)
            await mod_channel.send(f' Ticket request from {message.author.mention}')
            await message.author.send('Your ticket request has been submitted. A moderator will assist you shortly.')
        else:
            await message.channel.send('This command is only available to moderators.')
        return "'This is a help message that you can modify.'"
    


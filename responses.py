import random
import discord


def handle_response(message, AD='') -> str:
    """Basic response functionality for bot"""
    p_message = message.lower()

    print ('!hello command run')
    if p_message.startswith('!hello'):
        return 'Hey there!'
    
    print ('!roll command run')
    if p_message.startswith('!roll'):
        return str(random.randint(1,10))
    
    print ('!look command run')
    if '!look' in p_message:
        # Looks up a user from a provided global ID.
        
        # Strips the first part of the command
        user = p_message.replace('!look ','')
        print ('error handling')
        # Error handling in case a global ID doesn't exist
        try:
            user_description = AD.look_up_user(user)
        except Exception as error:
            return f'An error has occured: {error}'
        else:
            return f"User: {user}\nDescription: {user_description}"
        # return doesnt understand command 
    print ('doesnt see command')
    return 
    # "Sorry, I didnt understand that command."



# async def send_meme():
#     if ctx.startswith('meme'):
#         with open('meme_images/sait.jpg', 'rb') as f:
#             picture = discord.File(f)
#             await ctx.send(file=picture)
#             return ctx.send(file=picture)   
if message.content.startswith("!ticket"):
        # Generate a case number
        print('Starts ticket process')
        case_number = len(help_tickets) + 1
        # Store the user ID for the case number in the help_tickets dictionary
        print('stored user id for case')
        help_tickets[case_number] = {
            "user_id": message.author.id,
            "temp_channel": None
        }

# Send the case number to the user
        print('sent user case number')
        await message.author.send(f"Your case number is {case_number}")

        # Log the case number in the moderation and log channels
        print('sends ticket case and user id to mod and log channel')
        mod_channel = bot.get_channel(MODERATION_CHANNEL_ID)
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        await mod_channel.send(f"New ticket created. Case #{case_number}. User: {message.author}")
        await log_channel.send(f"New ticket created. Case #{case_number}. User: {message.author}")

# Help Ticket creation 

@bot.command()
async def casenumber(ctx, case_number: int):
    if case_number in help_tickets:
        # Get the user ID for the case number
        print('put case # to user id')
        user_id = help_tickets[case_number]["user_id"]
        user = bot.get_user(user_id)

        # Create a temporary text channel with the user
        print('creatin temp channel')
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True)
        }
        print('create temp channel')
        temp_channel = await ctx.guild.create_text_channel(f"ticket-{case_number}", overwrites=overwrites)

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
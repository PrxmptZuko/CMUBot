# Help Ticket creation 

#Constants
MODERATION_CHANNEL_ID = 1126969936082894988
LOG_CHANNEL_ID = 1128764737170178073
moderation_role_id = 1126249291875369070
# bot_permissions = 534723951680

#ticket data
case_number = 1
active_ticket = {}

@bot.event

async def on_button_clicked(interaction):
    print("button clicked")

@bot.command()
async def ticket(ctx):
    # Check if the command is run in a guild (server) text channel
    print ('Ticket 1')
    if isinstance(ctx.channel, discord.TextChannel):
        #send DM to user with ticket selection menu
        print ('selection menu')
        select_menu = discord.ui.Select(
            custom_id='ticket_selection',
            placeholder='Select a ticket type',
            options=[
                discord.SelectOption(label='Issue',value='1', emoji="⛔"),
                discord.SelectOption(label='Question',value='2',emoji="❓")
            ]
        )
        select_view = discord.ui.View()
        select_view.add_item(select_menu)
        print ('DMing user ')
        try:
            dm_channel = await ctx.author.create_dm()
            await dm_channel.send('Please select a ticket type:', view=select_view)
        except Exception as e:
            print(F'Failed to send DM to {ctx.author}: {e}')

@bot.event
async def on_dropdown_menu(interaction):
    print('dropdown menu selected')
    print('Custom ID:', interaction.component.custom_id)
    print('Selected values:', interaction.values)
    if interaction.component.custom_id == 'ticket_selection':
        selected_ticket_type = interaction.values[0]
        global case_number
        case_id = case_number
        case_number += 1
        print('creating ticket')
        #create ticket object
        ticket = {
            'case_id': case_id,
            'ticket_type': selected_ticket_type,
            'user_id': interaction.user.id,
            'channel_id': None,
            'moderator_id': None
        }

        active_ticket[case_id] = ticket
        print ('sending ticket to channels')
        #send ticket information to the moderation channel
        moderation_channel = bot.get_channel(MODERATION_CHANNEL_ID)
        if moderation_channel is None:
            print('Failed to find moderation channel')
            return
        ticket_info = f'Ticket {case_id} | Type: {selected_ticket_type} | User: <@{interaction.user.id}>'
        await moderation_channel.send(ticket_info)

        #Log Ticket Creation
        print ('getting log channel id')
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel is not None:
            print ('sending case log to log channel')
            await log_channel.send(f'Ticket {case_id} created by <@{interaction}')

        #Create Temporary text channel for the ticket
        guild = interaction.guild
        print ('creating temp channel')
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.get_role(interaction.user.id): discord.PermissionOverwrite(read_messages=True),
            guild.get_role(moderation_role_id): discord.PermissionOverwrite(read_messages=True)
        }
        ticket_channel = await guild.create_text_channel(f'ticket-{case_id}', overwrites=overwrites)
        ticket['channel_id'] = ticket_channel.id
        active_ticket[case_id] = ticket
        

#Ticket Cancellation 
@bot.command()
async def cancel_ticket(ctx):
    print ('ticket cancel process started')
    if isinstance(ctx.channel, discord.TextChannel) and ctx.channel.id in [ticket['channel_id'] for ticket in active_ticket.values()]:
        ticket_channel = ctx.channel
        case_id = int(ticket_channel.name.split('-')[-1].strip())

        if case_id in active_ticket:
            ticket = active_ticket[case_id]
            print ('logging canceled ticket')
            #log ticket cancelation 
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            if log_channel is not None:
                await log_channel.send(f'Ticket {case_id} was canceled by <@{ctx.author.id}')
            print ('deleting temp channel')
            #Delete temp channel
            await ticket_channel.delete()
            print ('removing from active tickets')
            #remove the ticket from active_tickets
            active_ticket.pop(case_id, None)
            print ('sent cancelation dm')
            #Send cancelation message to user 
            user = await bot.fetch_user(ticket['user_id'])
            if user is not None:
                await user.send(f'Your ticket (case {case_id}) has been canceled. Thank you!')


if message.content.startswith("!ticket"):
        await ticketcallback(message)

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
    select = discord.ui.Select (options = [
        discord.SelectOption(label="Help Ticket", value="01", emoji="✅", description= "This will open a help ticket"),
        discord.SelectOption(label="Other Ticket", value="02", emoji="❌", description="This will open a ticket in the other section")
    ])

    # select = interaction.component
    # interaction = await bot.wait_for("select_option", check=lambda i: i.component[0].custom_id == "create_ticket")
    value = interaction.data["values"][0]
    # Handles ticket channel creation and sets necessary permissions 

    if value == "01":
        category = discord.utils.get(guild.categories, name="Tickets")
        channel = await guild.create_text_channel(f"{interaction.user.name}-ticket", category=category, overwrites=overwrites)
        await interaction.channel.send(f"Created ticket - <#{channel.id}>")
        await channel.send("Hello, how can I help you?")
    elif value == "02":
        category = discord.utils.get(guild.categories, name="Other Tickets")
        channel = await guild.create_text_channel(f"{interaction.user.name}-ticket", category=category, overwrites=overwrites)
        await interaction.response.send_message(f"Created ticket - <#{channel.id}>")
        await channel.send("Hello, how can I help you?")

    # if value == "01":
    #     category = discord.utils.get(guild.categories, name="Tickets")
    #     channel = await guild.create_text_channel(f"{interaction.user.name}-ticket", category=category, overwrites=overwrites)
    #     await interaction.response.send_message(f"Created ticket - <#{channel.id}>", ephemeral=True)
    #     await channel.send("Hello, how can i help you?")
    # elif value == "02":
    #     category = discord.utils.get(guild.categories, name= "Other Tickets")
    #     channel = await guild.create_text_channel(f"{interaction.user.name}-ticket", category=category, overwrites=overwrites)
    #     await interaction.response.send_message(f"Created ticket - <#{channel.id}>", ephemeral=True)
    #     await channel.send("Hello, how can i help you?")

    view = discord.ui.View(timeout=None)
    select = discord.ui.Select(
        options=[
            discord.SelectOption(
                label="Help Ticket",
                value="01",
                emoji="✅",
                description="This will open a help ticket"
            ),
            discord.SelectOption(
                label="Other Ticket",
                value="02",
                emoji="❌",
                description="This will open a ticket in the other section"
            )
        ]
    )
    select.callback = ticketcallback
    view.add_item(select)
    await interaction.message.edit(view=view)
    # await interaction.message.send("Choose an option below", view=view, ephemeral=True)

# I want to test ctx (context) instead of labeling individual values. 'ctx' can pull details within commands so i want to try 
@bot.command()
async def create_ticket(ctx):
    button = discord.ui.Button(label= "📥 Create Ticket", style=discord.ButtonStyle.green, custom_id="create_ticket")
    button.callback = ticketcallback
    view = discord.ui.View(timeout=None)
    view.add_item(button)
    await ctx.send("Open a ticket below", view=view)

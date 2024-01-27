import discord
import tbapy
from keys import *
from pprint import pprint
from discord.ext import commands

tba = tbapy.TBA(tbaKey)

global event
event = None

class EventSel(discord.ui.View):
    def __init__(self, team='frc5413'):
        super().__init__()
        self.timeout = None
        events = [discord.SelectOption(label=f"{event['year']} {event['short_name']}", value=event['key']) for event in tba.team_events(team)]
        self.children[0].options = events[-25:len(events)-1]
    @discord.ui.select(options=[])
    async def sel(self, interaction: discord.Interaction, select: discord.ui.Select):
        global event 
        event = select.values[0]
        await interaction.response.send_message(content='Pick your scout position below', view=ScoutPoss(), silent=True)
        await interaction.message.delete()


class ScoutPoss(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.timeout = None
        self.add_item(ScoutButton(label='1', style=discord.ButtonStyle.green, row=0))
        self.add_item(ScoutButton(label='2', style=discord.ButtonStyle.green, row=0))
        self.add_item(ScoutButton(label='3', style=discord.ButtonStyle.green, row=0))
        self.add_item(ScoutButton(label='4', style=discord.ButtonStyle.green, row=0))
        self.add_item(ScoutButton(label='5', style=discord.ButtonStyle.green, row=1))
        self.add_item(ScoutButton(label='6', style=discord.ButtonStyle.green, row=1))

class ScoutButton(discord.ui.Button):
    def __init__(self, style=discord.ButtonStyle.green, label='1', row=1):
        super().__init__(style=style, label=label, row=row)

    # This function is called whenever this particular button is pressed
    # This is part of the "meat" of the game logic
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        global event
        pprint(tba.event_matches(event))
        thread = await interaction.channel.create_thread(name=f'Scout {self.label}', type=discord.ChannelType.private_thread)
        user = interaction.user
        
        Matches = []
        await thread.send(f'Hi {user.nick}!\nyou are scouting team 5413 Stellar Robotics in', view=Dropdown())
        await thread.send(f'Hi {user.nick}! you are scouting team 5413')
        await thread.add_user(user)
        await interaction.followup.send(content=f"Here's your scouting form\n{thread.jump_url}")

class Dropdown(discord.ui.View):
    def __init__(self, options=[discord.SelectOption(label='Qual 1', default=True)]):
        super().__init__()
        self.timeout = None
        self.children[0].options = options
    @discord.ui.select(options=[])
    async def sel(self, interaction: discord.Interaction, select: discord.ui.Select):
        print(select.values)
        await interaction.response.edit_message(view=self)

class Spinner(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.timeout = None
    #Incriment button
    @discord.ui.button(label='<', style=discord.ButtonStyle.red)
    async def dec(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.timeout = None
        number = int(self.children[1].label) if self.children[1].label else 0
        if number > 0:
            self.children[1].label = str(number - 1)
        # Make sure to update the message with our updated selves
        await interaction.response.edit_message(view=self)
    #value display
    @discord.ui.button(label='0', style=discord.ButtonStyle.gray)
    async def count(self, interaction: discord.Interaction, button: discord.ui.Button):
        number = int(button.label) if button.label else 0
        message = interaction.message.content
        await interaction.response.send_modal(SpinnerOverwrite(title=f'edit {message}',spinner=self))
    #decriment button
    @discord.ui.button(label='>', style=discord.ButtonStyle.green)
    async def inc(self, interaction: discord.Interaction, button: discord.ui.Button):
        number = int(self.children[1].label) if self.children[1].label else 0
        self.children[1].label = str(number + 1)

        # Make sure to update the message with our updated selves
        await interaction.response.edit_message(view=self)
class SpinnerOverwrite(discord.ui.Modal):
    def __init__(self, spinner='', title='', timeout=None):
        super().__init__(title=title, timeout=timeout)
        self.spinner = spinner
    value = discord.ui.TextInput(label='Enter whole number grater than 0')
    #answer = discord.ui.TextInput(label='Answer', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        view = self.spinner
        view.children[1].label = self.value
        await interaction.response.edit_message(view=view)
import discord
import tbapy
from keys import *
from pprint import pprint
from discord.ext import commands

import backend

from enum import Enum

# class syntax
class TIType(Enum):
    Comment = 1
    Defense = 2


tba = tbapy.TBA(tbaKey)

global event
event = None

scoutData = {}
blankData = {'AutoSpeakerNotes':0, 'AutoAmpNotes':0, 'AutoTrapNotes':0, 'CrossedLine':False, 'TeleopSpeakerNotes':0, 'TeleopAmpNotes':0, 'ClimbedWith':0, 'TeleopTrapNotes':0, 'DidDefend':False, 'WasDisabled':False, 'Comments':'', 'ScoutName':'','MatchKey':'', 'ScoutNumber':0}



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
        self.add_item(ScoutButton(label='5', style=discord.ButtonStyle.green, row=1, disabled=True))
        self.add_item(ScoutButton(label='6', style=discord.ButtonStyle.green, row=1, disabled=True))

class ScoutButton(discord.ui.Button):
    def __init__(self, style=discord.ButtonStyle.green, label='1', row=1, disabled=False):
        super().__init__(style=style, label=label, row=row, disabled=disabled)

    # This function is called whenever this particular button is pressed
    # This is part of the "meat" of the game logic
    async def callback(self, interaction: discord.Interaction):
        global scoutData
        await interaction.response.defer(ephemeral=True, thinking=True)
        global event
        match_list = sorted([(match['match_number'], match['key']) for match in tba.event_matches(event) if match['comp_level'] == 'qm'])
        pprint(match_list)
        lastScouted = backend.getMostRecentMatchNumber()
        options = [discord.SelectOption(label=f'Qual {match[0]}', value=match[1], default=(match[0] == lastScouted)) for match in match_list[max(0, lastScouted-5):min(len(match_list),lastScouted+20)]]
        
        target = backend.getBotToScout(match_list[lastScouted][1], self.label)
        thread = await interaction.channel.create_thread(name=f'Scout {self.label}', type=discord.ChannelType.private_thread)
        user = interaction.user
        
        Matches = []
        await thread.send(f'Hi {user.nick}!\nyou are scouting {target} in', view=Dropdown(options=options))
        await thread.send(f'# __Auto__')
        await thread.send(f'SpeakerNotes', view=Spinner())
        await thread.send(f'AmpNotes', view=Spinner())
        await thread.send(f'TrapNotes', view=Spinner())
        await thread.send(f'CrossedLine', view=BoolButton())
        await thread.send(f'# __Teleop__')
        await thread.send(f'SpeakerNotes', view=Spinner())
        await thread.send(f'AmpNotes', view=Spinner())
        await thread.send(f'TrapNotes', view=Spinner())
        await thread.send(f'# __EndGame__')
        await thread.send(f'Climbs on same chain', view=Spinner())
        await thread.send(f'TrapNotes', view=Spinner())
        await thread.send(f'Additional Comments', view=Comments())
        await thread.send(f'', view=Submit())
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
    value = discord.ui.TextInput(label='Enter whole number grater than 0')
    def __init__(self, spinner='', title='', timeout=None):
        super().__init__(title=title, timeout=timeout)
        self.spinner = spinner
        self.value.default=spinner.children[1].label
    #answer = discord.ui.TextInput(label='Answer', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        view = self.spinner
        view.children[1].label = self.value
        await interaction.response.edit_message(view=view)

class BoolButton(discord.ui.View):
    @discord.ui.button(label='False', style=discord.ButtonStyle.red)
    async def BB(self, interaction: discord.Interaction, button: discord.ui.Button):
        if button.style == discord.ButtonStyle.red:
            button.label = 'True'
            button.style = discord.ButtonStyle.green
        else:
            button.label = 'False'
            button.style = discord.ButtonStyle.red
        # Make sure to update the message with our updated selves
        await interaction.response.edit_message(view=self)

class Comments(discord.ui.View):
    def __init__(self, commentType=TIType.Comment):
        super().__init__()
        self.timeout = None
        self.commentType = commentType
    @discord.ui.button(label='Edit', style=discord.ButtonStyle.blurple)
    async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TextInput(message=interaction.message.content))
class TextInput(discord.ui.Modal):
    comment = discord.ui.TextInput(label='', style=discord.TextStyle.paragraph)
    def __init__(self, label='', title='', message='', timeout=None):
        super().__init__(title=title, timeout=timeout)
        self.comment.label = label
        self.comment.default = message
    #value = discord.ui.TextInput(label='Enter whole number grater than 0')
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content=self.children[0].value)

class Submit(discord.ui.View):
    @discord.ui.button(label='False', style=discord.ButtonStyle.green)
    async def BB(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Make sure to update the message with our updated selves
        await interaction.response.send_modal(ConfirmSubmit())
class ConfirmSubmit(discord.ui.Modal):
    def __init__(self, label='', title='', message='', timeout=None):
        super().__init__(title=title, timeout=timeout)
    #value = discord.ui.TextInput(label='Enter whole number grater than 0')
    test = f'''
    Auto
    test
    test
    test
    test
    test
    test
    test
    test
    test
    test
    test
    test
    test
    test
    test
    test
    test
    '''
    answer = discord.ui.TextInput(label='Confirm Input', default=test, style=discord.TextStyle.paragraph)
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content=self.value)
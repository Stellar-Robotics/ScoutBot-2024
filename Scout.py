import discord
import tbapy
from keys import *
from pprint import pprint
from discord.ext import commands
from pprint import pprint

import backend

from enum import Enum

# class syntax
class InType(Enum):
    AutoSpeakerNotes = 1
    AutoAmpNotes = 2
    AutoTrapNotes = 3
    CrossedLine = 4
    TeleopSpeakerNotes = 5
    TeleopAmpNotes = 6
    ClimbedWith = 7
    TeleopTrapNotes = 8
    DidDefend = 9
    WasDisabled = 10
    Comments = 11
    ScoutName = 12
    MatchKey = 13
    ScoutNumber = 14


tba = tbapy.TBA(tbaKey)

global event
event = None

scoutData = {}
blankData = {'AutoSpeakerNotes':0, 'AutoAmpNotes':0, 'AutoTrapNotes':0, 'CrossedLine':False, 'TeleopSpeakerNotes':0, 'TeleopAmpNotes':0, 'ClimbedWith':0, 'TeleopTrapNotes':0, 'DidDefend':False, 'WasDisabled':False, 'Comments':'', 'ScoutName':'','MatchKey':'', 'ScoutNumber':0}



class EventSel(discord.ui.View):
    def __init__(self, team='frc5413'):
        super().__init__()
        self.timeout = None
        eventOptions = [discord.SelectOption(label=f"{event['year']} {event['short_name']}", value=event['key']) for event in tba.team_events(team)[:-25:-1]]
        self.children[0].options = eventOptions
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
        #pprint(match_list)
        pprint(self.label)
        lastScouted = backend.getMostRecentMatchNumber()
        
        message = interaction.message

        #message.edit(view=)
        
        targets = backend.getBotToScout(match_list[lastScouted-1][1], int(self.label))
        pprint(targets[match_list[lastScouted-1][1]])
        options = [discord.SelectOption(label=f'Qual {match[0]}', value=f'{match[1]} {targets[match[1]]}', default=(match[0] == lastScouted)) for match in match_list[max(0, lastScouted-5):min(len(match_list),lastScouted+20)]]

        thread = await interaction.channel.create_thread(name=f'Scout {self.label}', type=discord.ChannelType.private_thread)
        user = interaction.user
        
        team = targets[match_list[lastScouted-1][1]]
        team_name = tba.team(team)['nickname']

        Matches = []
        await thread.send(f'Hi {user.nick}!\nyou are scouting {team}, {team_name}, in', view=MatchSel(options=options))
        await thread.send(f'# __Auto__')
        await thread.send(f'**SpeakerNotes**', view=Spinner(InType.AutoSpeakerNotes))
        await thread.send(f'**AmpNotes**', view=Spinner(InType.AutoAmpNotes))
        await thread.send(f'**TrapNotes**', view=Spinner(InType.AutoTrapNotes))
        await thread.send(f'**CrossedLine**', view=BoolButton())
        await thread.send(f'# __Teleop__')
        await thread.send(f'**SpeakerNotes**', view=Spinner(InType.TeleopSpeakerNotes))
        await thread.send(f'**AmpNotes**', view=Spinner(InType.TeleopAmpNotes))
        await thread.send(f'**Prioritized Amplified Speaker**', view=BoolButton())
        await thread.send(f'# __EndGame__')
        #await thread.send(f'**Climbs on same chain**', view=Spinner(InType.ClimbedWith))
        climbOptions = [discord.SelectOption(label='No Climb',value=f'ClimbedWith 0',default=True), discord.SelectOption(label='Parked',value=f'ClimbedWith -1'), discord.SelectOption(label='Solo Climb',value=f'ClimbedWith 1'), discord.SelectOption(label='Pair Climbed 1 Chain',value=f'ClimbedWith 2'), discord.SelectOption(label='All Climed 1 Chain',value=f'ClimbedWith 3')]
        await thread.send(f'**Climb**', view=Dropdown(options=climbOptions))
        await thread.send(f'**Spotlit Climb**', view=BoolButton())
        await thread.send(f'**TrapNotes**', view=Spinner(InType.AutoSpeakerNotes))
        await thread.send(f'**Additional Comments**')
        await thread.send(f'', view=Comments())
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
        options = [discord.SelectOption(label=option.label, value=option.value, description=option.description, emoji=option.emoji, default=(str(option.value) == select.values[0])) for option in select.options]
        pprint(options)
        select.options = options
        await interaction.response.edit_message(view=self)

class MatchSel(discord.ui.View):
    def __init__(self, options=[discord.SelectOption(label='Qual 1', default=True)]):
        super().__init__()
        self.timeout = None
        self.children[0].options = options
    @discord.ui.select(options=[])
    async def sel(self, interaction: discord.Interaction, select: discord.ui.Select):
        #print(select.values)
        select.options = [discord.SelectOption(label=option.label, value=option.value, description=option.description, emoji=option.emoji, default=(option.value == select.values[0])) for option in select.options]
        team = select.values[0].split()[1]
        team_name = tba.team(team)['nickname']
        await interaction.response.edit_message(content=f'Hi {interaction.user.nick}!\nyou are scouting {team}, {team_name}, in', view=self)

class Spinner(discord.ui.View):
    def __init__(self, tartgetVar):
        super().__init__()
        self.timeout = None
        self.tartgetVar = tartgetVar
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
        button.tartgetVar = self.tartgetVar
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
        print('test')
        if button.style == discord.ButtonStyle.red:
            button.label = 'True'
            button.style = discord.ButtonStyle.green
        else:
            button.label = 'False'
            button.style = discord.ButtonStyle.red
        # Make sure to update the message with our updated selves
        await interaction.response.edit_message(view=self)

class Comments(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.timeout = None
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
    def dataType(self, components):
        components = components[0].children
        if len(components) == 3:
            return components[1].label
        elif components[0].type == discord.ComponentType.select:
            return [option for option in components[0].options if option.default][0].value
        else:
            return components[0].label
    @discord.ui.button(label='Submit Form', style=discord.ButtonStyle.green)
    async def BB(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Make sure to update the message with our updated selves
        scoutData = blankData
        messages = [(message.content, message.components) async for message in interaction.message.channel.history(limit=None)][::-1]
        rawData = {'Scout':[], 'Auto':[], 'Teleop':[], 'EndGame':[], 'Comments':[]}
        phase = 0
        for message in messages:
            if len(message[1]) < 1:
                match message[0]:
                    case '# __Auto__':
                        phase = 1
                    case '# __Teleop__':
                        phase = 2
                    case '# __EndGame__':
                        phase = 3
                    case '**Additional Comments**':
                        phase = 4
            else:
                match phase:
                    case 0:
                        rawData['Scout'].append((message[0].split('\n')[0][2,-1], self.dataType(message[1])))
                    case 1:
                        rawData['Auto'].append((message[0], self.dataType(message[1])))
                    case 2:
                        rawData['Teleop'].append((message[0], self.dataType(message[1])))
                    case 3:
                        rawData['EndGame'].append((message[0], self.dataType(message[1])))
                    case 4:
                        rawData['Comments'].append(message[0])
        pprint(rawData)
        '''
        for row in messages[0][1]:
            value = [option for option in row.children[0].options if option.default][0].value
            option = value.split()
            print(messages[0][0].split('\n')[0][3:-1])
            print(option)
            
        for message in messages[1:-2]:
            for row in message[1]:
                if len(row.children) == 3:
                    print('spinner')
                    print(message[0])
                    print(row.children[1].label)
                elif row.children[0].type ==discord.ComponentType.button:
                    if row.children[0].label == 'Edit':
                        print('comment')
                        print(message[0])
                    else:
                        print('bool')
                        print(message[0])
                        print(row.children[0].label)
                else:
                    value = [option for option in row.children[0].options if option.default][0].value
                    print('select')
                    print(message[0])
                    option = value.split()
                    scoutData[option[0]] = option[1]
                    print(option)
        #pprint(messages)
        '''
        await interaction.response.send_modal(ConfirmSubmit())
class ConfirmSubmit(discord.ui.Modal):
    def __init__(self, label='', title='', message='', timeout=None):
        super().__init__(title=title, timeout=timeout)
        test = f'test'
        answer = discord.ui.TextInput(label='Confirm Input', default=test, style=discord.TextStyle.paragraph)
        self.add_item(answer)
    #value = discord.ui.TextInput(label='Enter whole number grater than 0')
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content=self.value)
import tbapy
from keys import *
from pprint import pprint

tba = tbapy.TBA('tbaKey')
events = tba.team_events('frc5413')
for event in events:
    pprint(event)
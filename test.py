import tbapy
from keys import *
from pprint import pprint
import backend

matchKey = "2023ohcl_qm23"
scoutNumber = 1
tba = tbapy.TBA(tbaKey)
match = tba.match(matchKey)
compKey = match["event_key"]
assignments = backend.getMatchAssignments(competitionKey=compKey)
matchAssignments : dict = assignments[matchKey]
team = iter({key for key in matchAssignments if matchAssignments[key]==scoutNumber}).__next__()
alliance = backend.getAlliance(teamKey=team, matchKey=matchKey)
teamNum = str.replace(team,"frc","")
print(f"{teamNum} ({alliance})")
import tbapy
from keys import *
from pprint import pprint

tba = tbapy.TBA(tbaKey)
events = [keys['key'] for keys in tba.team_events(5413)]
matches = tba.event_matches("2023ohcl")
qualMatches = []
eventRobots = {}
scoutedRobots = {}
totalScoutedRobots = {}
for team in tba.event_teams("2023ohcl"):
    if team["key"] == "frc5413":
        continue
    scoutedRobots[team["key"]] = 0
    totalScoutedRobots[team["key"]] = 0
for m in matches:
    lowestScoutAmnt = min(list(scoutedRobots.values()))
    
    if m["comp_level"] == "qm":
        alliances = m["alliances"]
        if not "frc5413" in alliances["red"]["team_keys"] and not "frc5413" in alliances["blue"]["team_keys"]:
            continue
        #print(m["key"])
        qualMatches.append(m)
        robots = {}
        redScouted = 0
        blueScouted = 0
        mainScoutPos = 1
        reserveScoutPos = 5
        for robot in alliances["red"]["team_keys"]:
            if robot == "frc5413":
                continue
            if (scoutedRobots[robot] != lowestScoutAmnt or redScouted >= 2) and reserveScoutPos != 7:
                robots[robot] = reserveScoutPos
                reserveScoutPos += 1
            else:
                robots[robot] = mainScoutPos
                if mainScoutPos <= 4:
                    scoutedRobots[robot] += 1
                    redScouted += 1
                mainScoutPos += 1
            #print(f"Red Scouted: {redScouted}, Team: {robot}, Scout Assigned: {robots[robot]}")
            #totalScoutedRobots[robot] += 1
        for robot in alliances["blue"]["team_keys"]:
            if robot == "frc5413":
                continue
            if (scoutedRobots[robot] != lowestScoutAmnt or blueScouted >= 2) and reserveScoutPos != 7:
                robots[robot] = reserveScoutPos
                reserveScoutPos += 1
            else:
                robots[robot] = mainScoutPos
                if mainScoutPos <= 4:
                    scoutedRobots[robot] += 1
                    blueScouted += 1
                mainScoutPos += 1
            #print(f"Blue Scouted: {blueScouted}, Team: {robot}, Scout Assigned: {robots[robot]}")
            #totalScoutedRobots[robot] += 1
        eventRobots[m["key"]] = robots

mat = tba.match('2020isde1_qm1')
pprint(eventRobots)
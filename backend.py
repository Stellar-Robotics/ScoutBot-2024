import tbapy
import sqlite3
from keys import *

def getConnection():
    return sqlite3.connect("matchData.db")

def getBotToScout(matchKey, scoutNumber):
    #with getConnection() as conn:
    #    with conn as cur:
    #        print(cur.execute(f"SELECT COUNT(MatchKey) FROM matches WHERE MatchKey = '{matchKey}'"))
    return "5413 (Red)"

def getMostRecentMatchNumber():
    return 5

def writeScoutData(matchKey, scoutNumber, data):
    return True

def getScoutedMatches(teamKey):
    pass

def getMatchAssignments(competitionKey):
    # Commented code is most likely debug code
    #events = [keys['key'] for keys in tba.team_events(5413)]
    #qualMatches = []
    #totalScoutedRobots = {}
    tba = tbapy.TBA(tbaKey)
    matches = tba.event_matches(competitionKey)
    assignments = {}
    scoutedRobots = {}
    for team in tba.event_teams("2023ohcl"):
        if team["key"] == "frc5413":
            continue
        scoutedRobots[team["key"]] = 0
        #totalScoutedRobots[team["key"]] = 0
    for m in matches:
        lowestScoutAmnt = min(list(scoutedRobots.values()))
        
        if m["comp_level"] == "qm":
            alliances = m["alliances"]
            if not "frc5413" in alliances["red"]["team_keys"] and not "frc5413" in alliances["blue"]["team_keys"]:
                continue
            #print(m["key"])
            #qualMatches.append(m)
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
            assignments[m["key"]] = robots
    return assignments

if __name__ == "__main__":
    getBotToScout("2022isde1_qm1", 1)

    exit()

    with getConnection() as conn:
        with conn as cur:
            cur.execute("""
                CREATE TABLE matches(
                    ScoutNumber INT,
                    MatchKey CHAR(15),

                    TeamKey CHAR(8),

                    AutoSpeakerNotes INT,
                    AutoAmpNotes INT,
                    AutoTrapNotes INT,
                    CrossedLine INT,

                    TeleopSpeakerNotes INT,
                    TeleopAmpNotes INT,
                    TeleopTrapNotes INT,

                    ClimbedWith INT,

                    DidDefend INT,
                    WasDisabled INT,
                    Comments TEXT,
                    ScoutName TEXT,

                    PRIMARY KEY (ScoutNumber, MatchKey)
                )
            """)

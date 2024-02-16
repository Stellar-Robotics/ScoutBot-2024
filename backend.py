import tbapy
import sqlite3

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

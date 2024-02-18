import tbapy
from keys import *
from pprint import pprint
import backend

matchKey = "2023ohcl_qm10"
scoutNumber = 1
print(backend.getBotToScout(matchKey=matchKey,scoutNumber=scoutNumber))
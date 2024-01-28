import tbapy
from keys import *
from pprint import pprint

tba = tbapy.TBA(tbaKey)
mat = tba.match('2020isde1_qm1')
pprint(mat)
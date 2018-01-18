import sys
sys.path.insert(0,"../")
from model import *
import os

os.chdir("../")
db.connect()

db.create_tables([
    User, Group, InGroup,
    Invitation, Broadcast,
    MailQueue, Schedule
])

db.close()
from playhouse.migrate import *
import sys
sys.path.insert(0, '../')
import model
import os

os.chdir("../")

migrator = SqliteMigrator(model.db)

migrate(
    migrator.drop_column('broadcast', 'isQueued')
)
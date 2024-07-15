import sys
#set system paath 
sys.path.append('../GreenGrocer')
from db import db_connector, establish_connection
db = db_connector()
cursor = establish_connection(db) 

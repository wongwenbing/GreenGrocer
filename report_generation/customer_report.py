import sys
#set system paath 
sys.path.append('../GreenGrocer')
from db import db_connector, establish_connection
db, cursor = establish_connection()


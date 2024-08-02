import sys
#set system paath 
sys.path.append('../GreenGrocer')
from db import db_connector
db, cursor = db_connector()

class PurchasingReporrt:

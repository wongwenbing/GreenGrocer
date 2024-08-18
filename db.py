import pymysql

timeout = 10

def db_connector(): 
  db = pymysql.connect(
  charset="utf8mb4",
  connect_timeout=timeout,
  cursorclass=pymysql.cursors.DictCursor,
  db="<insert db name>",
  host="<insert db host>",
  password="<insert db pw>",
  read_timeout=timeout,
  port=19222,
  user="<insert db user>",
  write_timeout=timeout,
  )
  
  cursor = db.cursor()
  return db, cursor



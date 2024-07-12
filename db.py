import pymysql

timeout = 10

def db_connector(): 
  db = pymysql.connect(
  charset="utf8mb4",
  connect_timeout=timeout,
  cursorclass=pymysql.cursors.DictCursor,
  db="greengrocerdb",
  host="mysql-1698fa8f-wongwenbing0718-aaf0.e.aivencloud.com",
  password="AVNS_iBl4eOysp6UaiypUdJd",
  read_timeout=timeout,
  port=19222,
  user="avnadmin",
  write_timeout=timeout,
  )
  return db

def establish_connection(connection): 
  connection = connection.cursor()
  return connection

db= db_connector()
cursor = establish_connection(db)

#DROP TABLE
#cursor.execute("DROP TABLE suppliers")

#CREATE NEW TABLE 
#cursor.execute("CREATE TABLE suppliers (supplier_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,supplier_name VARCHAR(255) NOT NULL,contact_name VARCHAR(255))")

#test code to insert values
sql = "INSERT INTO suppliers (supplier_name, contact_name) VALUES (%s, %s)"
val = [
  ('GrocerA', 'Iqbal'),
  ('Redmart', 'Iggy'),
  ('SAS', 'Rachel')
]
cursor.executemany(sql, val)
#NEED TO COMMIT TO ENSURE TABLE AND DATABASE CAN BE UPDATED
db.commit()

print(cursor.rowcount,"record inserted.")

#SELECT statements
cursor.execute("SElECT * FROM suppliers")
result = cursor.fetchall()
print("Results: ")
for x in result: 
  print(x)


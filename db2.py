import pymysql

timeout = 10

def establish_connection(): 
  connection = pymysql.connect(
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
  connection = connection.cursor()
  return connection

cursor = establish_connection()

cursor.execute("SElECT * FROM suppliers")
result = cursor.fetchall()
for x in result: 
  print(x)
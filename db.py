import pymysql
import uuid
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
  
  cursor = db.cursor()
  return db

#def establish_connection(connection): 
  #connection = connection.cursor()
  
 # return connection

#db= db_connector()
#cursor = establish_connection(db)

#DROP TABLE
#cursor.execute("DROP TABLE suppliers")

#CREATE NEW TABLE 
#cursor.execute("CREATE TABLE suppliers (supplier_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,supplier_name VARCHAR(255) NOT NULL,contact_name VARCHAR(255))")



#sql = """
#INSERT INTO Products (product_ID, name, uom, usual_price, discount_percentage, category_id, country_of_origin, eco_info, ingredients, tags, stock_quantity)
#VALUES ('PR1', 'Organic Apples', 'kg', '3.99', '1', 'CA101', 'USA', 'Products grown without synthetic pesticides or fertilizers prioritize natural cultivation methods.', 'Organic Apples', 'Organic, Fruits', 15);
#"""


#cursor.execute(sql)
#NEED TO COMMIT TO ENSURE TABLE AND DATABASE CAN BE UPDATED
#db.commit()

#print(cursor.rowcount,"record inserted.")

#SELECT statements
#cursor.execute("SElECT * FROM Products")
#result = cursor.fetchall()
#print("Results: ")
#for x in result: 
#  print(x)


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


cursor.execute("""
-- Create the staff table
CREATE TABLE staff (
    id INT NOT NULL AUTO_INCREMENT,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone_number VARCHAR(15),
    address VARCHAR(255),
    role VARCHAR(20),
    date_of_birth DATE,
    hire_date DATE,
    salary DECIMAL(10, 2),
    department VARCHAR(50),
    status VARCHAR(10)
);

-- Insert data into the staff table
INSERT INTO staff (first_name, last_name, email, phone_number, address, role, date_of_birth, hire_date, salary, department, status) 
VALUES
('Michael', 'Smith', 'michael.smith@gmail.com', '9001 2345', '1 Orchard Road, Singapore 238824', 'Admin', '1960-01-01', '2023-01-01', 5000.00, 'Fresh Produce', 'Active'),
('Jessica', 'Johnson', 'jessica.johnson@yahoo.com', '9123 4567', '2 Marina Bay Sands, Singapore 018956', 'Manager', '1970-02-02', '2023-02-15', 5200.00, 'Dairy Products', 'Active'),
('Christopher', 'Williams', 'christopher.williams@gmail.com', '9234 5678', '3 Sentosa Gateway, Singapore 098269', 'Employee', '1980-03-03', '2023-03-20', 5400.00, 'Canned Goods', 'Active'),
('Amanda', 'Jones', 'amanda.jones@gmail.com', '9345 6789', '4 Raffles Place, Singapore 048619', 'Manager', '1990-04-04', '2023-04-10', 5600.00, 'Frozen Foods', 'Active'),
('Joshua', 'Brown', 'joshua.brown@yahoo.com', '9456 7890', '5 Clarke Quay, Singapore 179024', 'Employee', '1961-05-05', '2023-05-05', 5800.00, 'Snacks and Sweets', 'Active');

ALTER TABLE staff
ADD COLUMN staff_id VARCHAR(55) GENERATED ALWAYS AS (CONCAT('S', id + 100)) STORED;


""")

#DROP TABLE
#cursor.execute("DROP TABLE suppliers")

#CREATE NEW TABLE 
#cursor.execute("CREATE TABLE suppliers (supplier_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,supplier_name VARCHAR(255) NOT NULL,contact_name VARCHAR(255))")

#test code to insert values
sql = "INSERT INTO staff (first_name, last_name, email, phone_number, address, role, date_of_birth, hire_date, salary, department, status) 
 VALUES (%s, %s, %s)"
val = [
('Michael', 'Smith', 'michael.smith@gmail.com', '9001 2345', '1 Orchard Road, Singapore 238824', 'Admin', '1960-01-01', '2023-01-01', 5000.00, 'Fresh Produce', 'Active'),
('Jessica', 'Johnson', 'jessica.johnson@yahoo.com', '9123 4567', '2 Marina Bay Sands, Singapore 018956', 'Manager', '1970-02-02', '2023-02-15', 5200.00, 'Dairy Products', 'Active'),
('Christopher', 'Williams', 'christopher.williams@gmail.com', '9234 5678', '3 Sentosa Gateway, Singapore 098269', 'Employee', '1980-03-03', '2023-03-20', 5400.00, 'Canned Goods', 'Active'),
('Amanda', 'Jones', 'amanda.jones@gmail.com', '9345 6789', '4 Raffles Place, Singapore 048619', 'Manager', '1990-04-04', '2023-04-10', 5600.00, 'Frozen Foods', 'Active'),
('Joshua', 'Brown', 'joshua.brown@yahoo.com', '9456 7890', '5 Clarke Quay, Singapore 179024', 'Employee', '1961-05-05', '2023-05-05', 5800.00, 'Snacks and Sweets', 'Active'),
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


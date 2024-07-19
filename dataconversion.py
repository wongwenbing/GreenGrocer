import pandas as pd 
from db import db_connector

db,cursor = db_connector()

query = "SELECT * FROM Products"

cursor.execute(query)

rows = cursor.fetchall()

def to_dataframe(cursor, rows):
    # Get column names from the cursor description
    columns = [desc[0] for desc in cursor.description]

    # Convert the fetched data into a DataFrame
    df = pd.DataFrame(rows, columns=columns)
    # Display the DataFrame
    return df 


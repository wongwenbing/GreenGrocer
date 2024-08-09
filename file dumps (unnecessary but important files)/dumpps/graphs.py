import pandas as pd
import sys
sys.path.append('../GreenGrocer')
from db import db_connector
import plotly.express as px
import json
import plotly

db, cursor = db_connector()
def generate_pie_chart(cursor):
    query = """
    SELECT Products.product_ID, Categories.category_name 
    FROM Products INNER JOIN Categories ON Products.category_id = Categories.category_id;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    print(rows)

    # Get column names from the cursor description
    columns = [desc[0] for desc in cursor.description]
    # Convert the fetched data into a DataFrame
    df = pd.DataFrame(rows, columns=columns)
    print(df)

    #Group by Category Name
    df_counts = df['category_name'].value_counts().reset_index()
    data = pd.DataFrame(df_counts)
    print(data)
    fig = px.pie(data, names='category_name', values='count', title='Proportion of UOM')
    graph_json = fig.to_json()
    return graph_json
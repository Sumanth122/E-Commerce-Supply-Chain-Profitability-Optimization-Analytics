import os
import glob
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
import kagglehub
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


DB_USER = "postgres"
DB_PASSWORD = "Sumanth@1234"  
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "superstore_db"

def main():
    print("--- STEP 1: Downloading Dataset via KaggleHub ---")
    path = kagglehub.dataset_download("vivek468/superstore-dataset-final")
    print(f"Dataset downloaded to: {path}")

    
    csv_files = glob.glob(os.path.join(path, "**/*.csv"), recursive=True)
    if not csv_files:
        raise FileNotFoundError("No CSV file found in the KaggleHub cache directory.")
    
    print(f"Loading CSV file: {csv_files[0]}")
    df = pd.read_csv(csv_files[0], encoding='latin1')

    
    df.columns = [c.lower().replace(' ', '_').replace('-', '_') for c in df.columns]

    print("\n--- STEP 2: Connecting to PostgreSQL & Loading Data ---")
    connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)

   
    df.to_sql('superstore_orders', engine, if_exists='replace', index=False)
    print("Dataset successfully pushed to PostgreSQL table 'superstore_orders'.")

    print("\n--- STEP 3: Executing SQL Business Analytics Query ---")
    with engine.connect() as connection:
        query = text("""
            SELECT sub_category, ROUND(SUM(profit)::numeric, 2) AS total_profit
            FROM superstore_orders
            GROUP BY sub_category
            ORDER BY total_profit DESC
            LIMIT 5;
        """)
        result = connection.execute(query).fetchall()
        print("Top 5 Most Profitable Sub-Categories (from SQL):")
        for row in result:
            print(f"  -> {row[0]}: ${row[1]}")

    print("\n--- STEP 4: Running Machine Learning (K-Means RFM Segmentation) ---")
  
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    
    snapshot_date = df['order_date'].max() + pd.Timedelta(days=1)
    rfm = df.groupby('customer_id').agg({
        'order_date': lambda x: (snapshot_date - x.max()).days,  
        'order_id': 'nunique',                                   
        'sales': 'sum'                                           
    }).rename(columns={
        'order_date': 'recency',
        'order_id': 'frequency',
        'sales': 'monetary'
    }).reset_index()

    
    rfm_log = np.log1p(rfm[['recency', 'frequency', 'monetary']])

   
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm_log)

    
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    rfm['cluster'] = kmeans.fit_predict(rfm_scaled)

    print("Customer Segmentation Profile (Average metrics per cluster):")
    cluster_summary = rfm.groupby('cluster')[['recency', 'frequency', 'monetary']].mean()
    print(cluster_summary.to_string())

    print("\nPipeline execution complete successfully!")

if __name__ == "__main__":
    main()

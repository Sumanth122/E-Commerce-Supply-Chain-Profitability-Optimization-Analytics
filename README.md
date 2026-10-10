
import os
import glob
import pandas as pd
from sqlalchemy import create_engine
import kagglehub

path = kagglehub.dataset_download("vivek468/superstore-dataset-final")
csv_files = glob.glob(os.path.join(path, "**/*.csv"), recursive=True)


df = pd.read_csv(csv_files[0], encoding='latin1')


df.columns = [c.lower().replace(' ', '_').replace('-', '_') for c in df.columns]


engine = create_engine('postgresql+psycopg2://postgres:your_password@localhost:5432/superstore_db')
df.to_sql('superstore_orders', engine, if_exists='replace', index=False)
print("Data pipeline executed successfully!")

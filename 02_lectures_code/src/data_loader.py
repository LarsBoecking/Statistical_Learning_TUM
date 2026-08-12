import pandas as pd
import os

def _load_disaster_data(BASE):
    directory = "data"
    file_name = "1900_2021_DISASTERS.csv"
    file_path = os.path.join(BASE,"..", directory, file_name)
    df = pd.read_csv(file_path)

    df = df.convert_dtypes()
    df['Total Damages (US$)'] = df['Total Damages (\'000 US$)'] * 1000
    df['date'] = pd.to_datetime(
        dict(
            year=df['Start Year'],
            month=df['Start Month'].fillna(1).astype(int),
            day=df['Start Day'].fillna(1).astype(int)
        ),
        errors='coerce'
    )
    df['Disaster Type'] = df['Disaster Type'].astype('category')
    
    return df
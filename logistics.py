import numpy as np
import pandas as pd

workdays = '1111110' # Workdays are from Mon-Sat
public_holidays = ['2020-03-08', '2020-03-25', '2020-03-30', '2020-03-31']
timezone = 28800 # Set GMT+8

# Create a dictionary to store the 1st delivery attempt SLA
sla = {
    'manila_manila': 3, 
    'manila_luzon': 5, 
    'manila_visayas': 7,
    'manila_mindanao': 7, 
    'luzon_luzon': 5
    }

# SLA for the 2nd delivery attempt
sla_second_attempt = 3

df = pd.read_csv('data/delivery_orders_march.csv')

# Parse origin and destination address fields to identify the delivery route
df['origin_destination'] = df['selleraddress'].map(lambda x: x.lower().split()[-1]) + '_' + df['buyeraddress'].map(lambda x: x.lower().split()[-1])

# Establish the SLA for each order, based on the origin to destination route
df['sla'] = [sla[i] for i in df['origin_destination']]

df['2nd_deliver_attempt'].fillna(0, inplace=True)

# Convert epoch time to datetime format
start_date = pd.to_datetime(df['pick'] + timezone, unit='s').dt.date
first_date =  pd.to_datetime(df['1st_deliver_attempt'] + timezone, unit='s').dt.date
second_date = pd.to_datetime(df['2nd_deliver_attempt'] + timezone, unit='s').dt.date

# Number of days from when the parcel was picked up to 1st delivery attempt
df['num_days_first'] = np.busday_count(start_date, first_date, weekmask=workdays, holidays=public_holidays)

# Number of days between the 1st and 2nd delivery attempt
df['num_days_second'] = np.busday_count(first_date, second_date, weekmask=workdays, holidays=public_holidays)

df['is_late'] = (df['num_days_first'] > df['sla']) | (df['num_days_second'] > sla_second_attempt)
df['is_late'] = df['is_late'].astype(int)

results = df[['orderid', 'is_late']]
results.to_csv('results.csv', index=False)

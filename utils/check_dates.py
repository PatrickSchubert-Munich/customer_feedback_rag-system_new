import pandas as pd

df = pd.read_csv('./data/feedback_data_enhanced.csv')
df['Date'] = pd.to_datetime(df['Date'])

print(f'Earliest date: {df["Date"].min()}')
print(f'Latest date: {df["Date"].max()}')
print(f'Total rows: {len(df)}')
print(f'\nDate range: {(df["Date"].max() - df["Date"].min()).days} days')

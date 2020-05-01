import pandas as pd
df = pd.read_csv('data2.csv', index_col=0)
print(type(df))
print(df)
print(df[0])
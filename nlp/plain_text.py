import pandas as pd
import re
import sys



df = pd.read_csv('datasets/good_dataset.csv', sep='\t')
df2 = pd.read_csv('good_dataset.csv', sep='\t')

df = pd.concat([df,df2])
print(df)

df.to_csv('datasets/good_dataset.csv',sep='\t', index=False, encoding='utf-8')
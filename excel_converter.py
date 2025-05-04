import pandas as pd

df = pd.read_excel("Files\\AnyDesks.xlsx", sheet_name='Sheet1')
df = df[['انی دسک سرور','شماره تماس','مدیر عامل','نام شرکت']]
df.to_excel("Files\\AnyDesks2.xlsx", sheet_name='Sheet1')

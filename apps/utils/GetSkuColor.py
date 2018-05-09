# -*- coding: utf-8 -*-

import pandas as pd
d1 = {'date':'2018-01-01','v':1}
d2 = {'date':'2018-01-01','v':2}
d3 = {'date':'2018-01-02','v':3}
d4 = {'date':'2018-01-03','v':13}
df1 = pd.DataFrame([d1])
df2 = pd.DataFrame([d2])
df3 = pd.DataFrame([d3])
df4 = pd.DataFrame([d4])
res = pd.concat([df1,df2,df3,df4], join='inner')

# df = df.groupby('date',as_index = False).sum()
# Df.groupby（姓名，as_index = False）[金额].unique（）
print res

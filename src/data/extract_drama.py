# -*- coding: utf-8 -*-
import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\mazal-folder\projects\data-analysis\data\515_shipinhao\4_南瓜\南瓜-视频号4月剧集数据统计_2026-05-11-5 copy.xlsx'
xl = pd.ExcelFile(path)
df = xl.parse(xl.sheet_names[0])

# 按剧目名称取第一条视频标题作为描述
drama_desc = df.groupby('剧目名称')['视频标题'].first().reset_index()
drama_desc.columns = ['剧名', '描述']

# 按广告收益排序
by_drama = df.groupby('剧目名称').agg(广告收益=('广告收益', 'sum')).reset_index()
by_drama.columns = ['剧名', '广告收益']
result = drama_desc.merge(by_drama, on='剧名')
result = result.sort_values('广告收益', ascending=False)

output = []
for _, row in result.iterrows():
    output.append({'剧名': row['剧名'], '描述': row['描述'], '广告收益': row['广告收益']})

for item in output:
    print(item['剧名'])
    print('  描述:', item['描述'])
    print('  收益:', round(item['广告收益'], 2))
    print()

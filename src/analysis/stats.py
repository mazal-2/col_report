# -*- coding: utf-8 -*-
import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\mazal-folder\projects\data-analysis\data\515_shipinhao\4_南瓜\南瓜_视频数据_4月.csv'
df = pd.read_csv(path, skiprows=2)
df['时间'] = pd.to_datetime(df['时间'])
df = df.sort_values('时间')

print('=== Key Stats ===')
play_max_date = df.loc[df['播放'].idxmax(), '时间'].strftime('%m/%d')
like_max_date = df.loc[df['喜欢'].idxmax(), '时间'].strftime('%m/%d')
share_max_date = df.loc[df['分享'].idxmax(), '时间'].strftime('%m/%d')
follow_max_date = df.loc[df['关注'].idxmax(), '时间'].strftime('%m/%d')

print('Play peak:', df['播放'].max(), 'on', play_max_date)
print('Play avg:', round(df['播放'].mean()))
print('Like peak:', df['喜欢'].max(), 'on', like_max_date)
print('Share peak:', df['分享'].max(), 'on', share_max_date)
print('Follow peak:', df['关注'].max(), 'on', follow_max_date)
print('Total play:', df['播放'].sum())
print('Total follow:', df['关注'].sum())
print()
print('Top 5 by play:')
print(df.nlargest(5, '播放')[['时间', '播放', '喜欢', '分享', '关注']].to_string())

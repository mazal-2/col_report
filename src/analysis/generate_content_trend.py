# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
import sys
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')

# ===================== FONTS =====================
plt.rcParams['font.sans-serif'] = ['KaiTi', 'SimKai', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# ===================== LOAD DATA =====================
drama_csv = r'D:\mazal-folder\projects\data-analysis\data\515_shipinhao\4_南瓜\剧目分类标签_full.csv'
april_xl = r'D:\mazal-folder\projects\data-analysis\data\515_shipinhao\4_南瓜\april_daily_data.xlsx'

# Load classification
tag_df = pd.read_csv(drama_csv)
tag_df = tag_df[['剧名', '频道', '题材']]
print('Tag df shape:', tag_df.shape)
print(tag_df.head())

# Load daily data sheets
xl = pd.ExcelFile(april_xl)
df_rev = xl.parse('广告收益(日频)')
df_read = xl.parse('阅读量(日频)')
df_like = xl.parse('点赞数(日频)')
df_sum = xl.parse('剧名汇总')

# 单位换算：收益从"分"改为"元"，万播收益 = 收益(元) / 播放量(万) = (收益_分/100) / (阅读量/10000) = 收益_分*10000/(阅读量*100)
# 先转元，再按播放量(万)计算万播收益
df_rev[df_rev.columns[1:]] = df_rev[df_rev.columns[1:]] / 100  # 分→元
df_sum['广告收益'] = df_sum['广告收益'] / 100  # 分→元

print('Rev shape:', df_rev.shape)

# ===================== RESHAPE DAILY DATA =====================
# Melt revenue daily data: 剧名, date, revenue
rev_daily = df_rev.melt(id_vars='剧名', var_name='日期', value_name='广告收益')
rev_daily['日期'] = pd.to_datetime(rev_daily['日期'])

# Melt read daily data
read_daily = df_read.melt(id_vars='剧名', var_name='日期', value_name='阅读量')
read_daily['日期'] = pd.to_datetime(read_daily['日期'])

# Merge revenue + read
daily = rev_daily.merge(read_daily, on=['剧名', '日期'])
daily['万播收益'] = daily['广告收益'] / daily['阅读量'] * 10000
daily['万播收益'] = daily['万播收益'].replace([np.inf, -np.inf], np.nan)

# Merge with tag
daily = daily.merge(tag_df, on='剧名', how='left')
print('Daily merged shape:', daily.shape)
print('Tags found:', daily['频道'].notna().sum(), '/', len(daily))
print('Unmatched:', daily[daily['频道'].isna()]['剧名'].unique())

# ===================== DAILY AGGREGATION =====================
# By channel
daily_channel = daily.groupby(['日期', '频道']).agg(
    广告收益=('广告收益', 'sum'),
    阅读量=('阅读量', 'sum')
).reset_index()
daily_channel['万播收益'] = daily_channel['广告收益'] / daily_channel['阅读量'] * 10000
daily_channel['万播收益'] = daily_channel['万播收益'].replace([np.inf, -np.inf], np.nan)

# By genre
daily_genre = daily.groupby(['日期', '题材']).agg(
    广告收益=('广告收益', 'sum'),
    阅读量=('阅读量', 'sum')
).reset_index()
daily_genre['万播收益'] = daily_genre['广告收益'] / daily_genre['阅读量'] * 10000
daily_genre['万播收益'] = daily_genre['万播收益'].replace([np.inf, -np.inf], np.nan)

# ===================== WEEKLY AGGREGATION =====================
def get_week(date):
    day = date.day
    if day <= 5: return 'W1\n4/1-4/5'
    elif day <= 12: return 'W2\n4/6-4/12'
    elif day <= 19: return 'W3\n4/13-4/19'
    elif day <= 26: return 'W4\n4/20-4/26'
    else: return 'W5\n4/27-4/30'

daily['周'] = daily['日期'].apply(get_week)

week_channel = daily.groupby(['周', '频道']).agg(
    广告收益=('广告收益', 'sum'),
    阅读量=('阅读量', 'sum')
).reset_index()
week_channel['万播收益'] = week_channel['广告收益'] / week_channel['阅读量'] * 10000
week_channel['万播收益'] = week_channel['万播收益'].replace([np.inf, -np.inf], np.nan)
week_order = ['W1\n4/1-4/5', 'W2\n4/6-4/12', 'W3\n4/13-4/19', 'W4\n4/20-4/26', 'W5\n4/27-4/30']
week_channel['周'] = pd.Categorical(week_channel['周'], categories=week_order, ordered=True)
week_channel = week_channel.sort_values(['周', '频道'])

week_genre = daily.groupby(['周', '题材']).agg(
    广告收益=('广告收益', 'sum'),
    阅读量=('阅读量', 'sum')
).reset_index()
week_genre['万播收益'] = week_genre['广告收益'] / week_genre['阅读量'] * 10000
week_genre['万播收益'] = week_genre['万播收益'].replace([np.inf, -np.inf], np.nan)
week_genre['周'] = pd.Categorical(week_genre['周'], categories=week_order, ordered=True)
week_genre = week_genre.sort_values(['周', '题材'])

# ===================== MONTHLY AGGREGATION =====================
monthly = df_sum.merge(tag_df, on='剧名', how='left')
monthly['万播收益'] = monthly['广告收益'] / monthly['阅读量'] * 10000
monthly['万播收益'] = monthly['万播收益'].replace([np.inf, -np.inf], np.nan)

monthly_channel = monthly.groupby('频道').agg(
    广告收益=('广告收益', 'sum'),
    阅读量=('阅读量', 'sum')
).reset_index()
monthly_channel['万播收益'] = monthly_channel['广告收益'] / monthly_channel['阅读量'] * 10000

monthly_genre = monthly.groupby('题材').agg(
    广告收益=('广告收益', 'sum'),
    阅读量=('阅读量', 'sum')
).reset_index()
monthly_genre['万播收益'] = monthly_genre['广告收益'] / monthly_genre['阅读量'] * 10000

print('\n=== Monthly by Channel ===')
print(monthly_channel)
print('\n=== Monthly by Genre ===')
print(monthly_genre)

# ===================== PRINT TOP DRAMA =====================
print('\n=== Top Drama by Revenue ===')
print(monthly.nlargest(5, '广告收益')[['剧名', '广告收益', '阅读量', '万播收益', '频道', '题材']])
print('\n=== Top Drama by 阅读量 ===')
print(monthly.nlargest(5, '阅读量')[['剧名', '广告收益', '阅读量', '万播收益', '频道', '题材']])
print('\n=== Top Drama by 万播收益 ===')
top_wan = monthly[monthly['阅读量'] > 0].nlargest(5, '万播收益')
print(top_wan[['剧名', '广告收益', '阅读量', '万播收益', '频道', '题材']])

# ===================== CHART COLORS =====================
channel_colors = {'女频': '#e84c5a', '男频': '#2a81d6'}
genre_colors = {'都市': '#2ecc71', '玄幻': '#9b59b6', '末世': '#e67e22'}

# ===================== DRAW CHARTS =====================
output_base = r'D:\mazal-folder\projects\data-analysis\assets\charts\4_南瓜'

# --- Chart 1: Daily Line - By Channel (Revenue + Read) ---
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

for channel in ['女频', '男频']:
    sub = daily_channel[daily_channel['频道'] == channel].sort_values('日期')
    axes[0].plot(sub['日期'], sub['广告收益'], marker='o', markersize=3,
                 linewidth=2, label=channel, color=channel_colors[channel])
    axes[1].plot(sub['日期'], sub['万播收益'], marker='s', markersize=3,
                 linewidth=2, label=channel, color=channel_colors[channel], linestyle='--')

axes[0].set_title('日频 - 男女频 广告收益趋势', fontsize=13, fontweight='bold')
axes[0].set_ylabel('广告收益（元）', fontsize=10)
axes[0].legend()
axes[0].grid(True, alpha=0.3)
axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
axes[0].xaxis.set_major_locator(mdates.DayLocator(interval=3))
axes[1].set_title('日频 - 男女频 万播收益趋势', fontsize=13, fontweight='bold')
axes[1].set_ylabel('万播收益（元/万播）', fontsize=10)
axes[1].legend()
axes[1].grid(True, alpha=0.3)
axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
axes[1].xaxis.set_major_locator(mdates.DayLocator(interval=3))
plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=45)
fig.autofmt_xdate(rotation=45)
plt.tight_layout()
plt.savefig(f'{output_base}/chart1_daily_channel.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print('Chart 1 saved')

# --- Chart 2: Daily Line - By Genre (Revenue + Wanbo) ---
fig, axes = plt.subplots(2, 1, figsize=(14, 10))
genres = ['都市', '玄幻', '末世']

for genre in genres:
    sub = daily_genre[daily_genre['题材'] == genre].sort_values('日期')
    axes[0].plot(sub['日期'], sub['广告收益'], marker='o', markersize=3,
                 linewidth=2, label=genre, color=genre_colors.get(genre, '#888'))
    axes[1].plot(sub['日期'], sub['万播收益'], marker='s', markersize=3,
                 linewidth=2, label=genre, color=genre_colors.get(genre, '#888'), linestyle='--')

axes[0].set_title('日频 - 题材（都市/玄幻/末世）广告收益趋势', fontsize=13, fontweight='bold')
axes[0].set_ylabel('广告收益（元）', fontsize=10)
axes[0].legend()
axes[0].grid(True, alpha=0.3)
axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
axes[0].xaxis.set_major_locator(mdates.DayLocator(interval=3))
axes[1].set_title('日频 - 题材（都市/玄幻/末世）万播收益趋势', fontsize=13, fontweight='bold')
axes[1].set_ylabel('万播收益（元/万播）', fontsize=10)
axes[1].legend()
axes[1].grid(True, alpha=0.3)
axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
axes[1].xaxis.set_major_locator(mdates.DayLocator(interval=3))
plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=45)
fig.autofmt_xdate(rotation=45)
plt.tight_layout()
plt.savefig(f'{output_base}/chart2_daily_genre.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print('Chart 2 saved')

# --- Chart 3: Weekly Bar - By Channel ---
fig, axes = plt.subplots(2, 1, figsize=(12, 10))
weeks = week_order

x = np.arange(len(weeks))
width = 0.35

for i, channel in enumerate(['女频', '男频']):
    sub = week_channel[week_channel['频道'] == channel].sort_values('周')
    rev_vals = [sub[sub['周'] == w]['广告收益'].values[0] if w in sub['周'].values else 0 for w in weeks]
    wan_vals = [sub[sub['周'] == w]['万播收益'].values[0] if w in sub['周'].values else 0 for w in weeks]
    axes[0].bar(x + (i-0.5)*width, rev_vals, width, label=channel, color=channel_colors[channel])
    axes[1].bar(x + (i-0.5)*width, wan_vals, width, label=channel, color=channel_colors[channel])

axes[0].set_title('周频 - 男女频 广告收益', fontsize=13, fontweight='bold')
axes[0].set_ylabel('广告收益（元）', fontsize=10)
axes[0].set_xticks(x)
axes[0].set_xticklabels(weeks)
axes[0].legend()
axes[0].grid(True, alpha=0.3, axis='y')
axes[1].set_title('周频 - 男女频 万播收益', fontsize=13, fontweight='bold')
axes[1].set_ylabel('万播收益（元/万播）', fontsize=10)
axes[1].set_xticks(x)
axes[1].set_xticklabels(weeks)
axes[1].legend()
axes[1].grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(f'{output_base}/chart3_weekly_channel.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print('Chart 3 saved')

# --- Chart 4: Weekly Bar - By Genre ---
fig, axes = plt.subplots(2, 1, figsize=(12, 10))
genres_all = ['都市', '玄幻', '末世']
x = np.arange(len(weeks))
width = 0.25

for i, genre in enumerate(genres_all):
    sub = week_genre[week_genre['题材'] == genre].sort_values('周')
    rev_vals = [sub[sub['周'] == w]['广告收益'].values[0] if w in sub['周'].values else 0 for w in weeks]
    wan_vals = [sub[sub['周'] == w]['万播收益'].values[0] if w in sub['周'].values else 0 for w in weeks]
    axes[0].bar(x + (i-1)*width, rev_vals, width, label=genre, color=genre_colors.get(genre, '#888'))
    axes[1].bar(x + (i-1)*width, wan_vals, width, label=genre, color=genre_colors.get(genre, '#888'))

axes[0].set_title('周频 - 题材 广告收益', fontsize=13, fontweight='bold')
axes[0].set_ylabel('广告收益（元）', fontsize=10)
axes[0].set_xticks(x)
axes[0].set_xticklabels(weeks)
axes[0].legend()
axes[0].grid(True, alpha=0.3, axis='y')
axes[1].set_title('周频 - 题材 万播收益', fontsize=13, fontweight='bold')
axes[1].set_ylabel('万播收益（元/万播）', fontsize=10)
axes[1].set_xticks(x)
axes[1].set_xticklabels(weeks)
axes[1].legend()
axes[1].grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(f'{output_base}/chart4_weekly_genre.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print('Chart 4 saved')

# --- Chart 5: Monthly Pie - By Channel ---
fig, axes = plt.subplots(1, 2, figsize=(14, 7))

# Revenue pie
rev_vals = monthly_channel.sort_values('广告收益', ascending=False)
axes[0].pie(rev_vals['广告收益'], labels=rev_vals['频道'],
            autopct='%1.1f%%', colors=[channel_colors[c] for c in rev_vals['频道']],
            startangle=90)
axes[0].set_title('月频 - 男女频 广告收益占比', fontsize=13, fontweight='bold')

# Read pie
read_vals = monthly_channel.sort_values('阅读量', ascending=False)
axes[1].pie(read_vals['阅读量'], labels=read_vals['频道'],
            autopct='%1.1f%%', colors=[channel_colors[c] for c in read_vals['频道']],
            startangle=90)
axes[1].set_title('月频 - 男女频 阅读量占比', fontsize=13, fontweight='bold')

plt.tight_layout()
plt.savefig(f'{output_base}/chart5_monthly_channel.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print('Chart 5 saved')

# --- Chart 6: Monthly Pie - By Genre ---
fig, axes = plt.subplots(1, 2, figsize=(14, 7))

rev_vals = monthly_genre.sort_values('广告收益', ascending=False)
axes[0].pie(rev_vals['广告收益'], labels=rev_vals['题材'],
            autopct='%1.1f%%', colors=[genre_colors[g] for g in rev_vals['题材']],
            startangle=90)
axes[0].set_title('月频 - 题材 广告收益占比', fontsize=13, fontweight='bold')

read_vals = monthly_genre.sort_values('阅读量', ascending=False)
axes[1].pie(read_vals['阅读量'], labels=read_vals['题材'],
            autopct='%1.1f%%', colors=[genre_colors[g] for g in read_vals['题材']],
            startangle=90)
axes[1].set_title('月频 - 题材 阅读量占比', fontsize=13, fontweight='bold')

plt.tight_layout()
plt.savefig(f'{output_base}/chart6_monthly_genre.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print('Chart 6 saved')

print('\nAll charts saved!')
print('\n=== Monthly Summary ===')
print('Channel:')
print(monthly_channel.to_string(index=False))
print('\nGenre:')
print(monthly_genre.to_string(index=False))

# Save summary stats
summary_data = {
    'monthly_channel': monthly_channel,
    'monthly_genre': monthly_genre,
    'monthly': monthly,
}
print('\n=== TOP DRAMA ===')
print('By Revenue:', monthly.nlargest(3, '广告收益')[['剧名','广告收益','阅读量','万播收益','频道','题材']].to_string(index=False))
print('By Read:', monthly.nlargest(3, '阅读量')[['剧名','广告收益','阅读量','万播收益','频道','题材']].to_string(index=False))
print('By Wanbo:', monthly[monthly['阅读量']>0].nlargest(3, '万播收益')[['剧名','广告收益','阅读量','万播收益','频道','题材']].to_string(index=False))

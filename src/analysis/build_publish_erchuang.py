# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import sys
sys.stdout.reconfigure(encoding='utf-8')

plt.rcParams['font.sans-serif'] = ['KaiTi', 'SimKai', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

BASE = r'D:\mazal-folder\projects\data-analysis\assets\charts\4_南瓜'

# ===================== PART 1: 上架趋势 =====================
print('=== PART 1: 上架趋势 ===')
df = pd.read_csv(r'D:\mazal-folder\projects\data-analysis\data\515_shipinhao\4_南瓜\works_list.csv')
df['publishDate'] = pd.to_datetime(df['publishDate'])
april = df[(df['publishDate'] >= '2026-04-01') & (df['publishDate'] <= '2026-04-30')].copy()

# Daily count
daily_counts = april.groupby('publishDate').size().reset_index(name='发布剧数')
daily_counts['publishDate'] = pd.to_datetime(daily_counts['publishDate'])

# Fill gaps (days with 0)
date_range = pd.date_range('2026-04-01', '2026-04-30', freq='D')
daily_counts = daily_counts.set_index('publishDate').reindex(date_range, fill_value=0).reset_index()
daily_counts.columns = ['日期', '发布剧数']

# Weekly count
def get_week(date):
    day = date.day
    if day <= 5: return 'W1\n4/1-4/5'
    elif day <= 12: return 'W2\n4/6-4/12'
    elif day <= 19: return 'W3\n4/13-4/19'
    elif day <= 26: return 'W4\n4/20-4/26'
    else: return 'W5\n4/27-4/30'

daily_counts['周'] = daily_counts['日期'].apply(get_week)
weekly_counts = daily_counts.groupby('周')['发布剧数'].sum().reset_index()
week_order = ['W1\n4/1-4/5', 'W2\n4/6-4/12', 'W3\n4/13-4/19', 'W4\n4/20-4/26', 'W5\n4/27-4/30']
weekly_counts['周'] = pd.Categorical(weekly_counts['周'], categories=week_order, ordered=True)
weekly_counts = weekly_counts.sort_values('周')

print('Daily:')
print(daily_counts.to_string(index=False))
print('\nWeekly:')
print(weekly_counts.to_string(index=False))

# Chart 1: Daily line
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(daily_counts['日期'], daily_counts['发布剧数'], marker='o', linewidth=2, markersize=5, color='#e84c5a')
ax.fill_between(daily_counts['日期'], daily_counts['发布剧数'], alpha=0.2, color='#e84c5a')
ax.set_title('4月发布剧数日频趋势（折线图）', fontsize=13, fontweight='bold')
ax.set_ylabel('发布剧数', fontsize=11)
ax.grid(True, alpha=0.3)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
fig.autofmt_xdate()
plt.tight_layout()
plt.savefig(f'{BASE}/publish_daily.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print('Chart publish_daily.png saved')

# Chart 2: Weekly bar
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(weekly_counts['周'], weekly_counts['发布剧数'], color='#2a81d6', alpha=0.85)
for bar, val in zip(bars, weekly_counts['发布剧数']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, str(val),
            ha='center', va='bottom', fontsize=11, fontweight='bold')
ax.set_title('4月发布剧数周频分布（柱状图）', fontsize=13, fontweight='bold')
ax.set_ylabel('发布剧数', fontsize=11)
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(f'{BASE}/publish_weekly.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print('Chart publish_weekly.png saved')

# ===================== PART 2: 原创 vs 二创 =====================
print('\n=== PART 2: 原创 vs 二创 ===')
xl = pd.ExcelFile(r'D:\mazal-folder\projects\data-analysis\data\515_shipinhao\4_南瓜\南瓜-视频号4月剧集数据统计_2026-05-11-5 copy.xlsx')
df_xl = xl.parse(xl.sheet_names[0])

# Convert revenue: fen -> yuan
df_xl['广告收益'] = df_xl['广告收益'] / 100

# 主账号：南瓜动漫短剧场
# 二创账号：爱动漫微剧场
# 二创剧：祭品公主的生存法则、替嫁后沉沉睡老公超会撩
original_account = '南瓜动漫短剧场'
erchuang_account = '爱动漫微剧场'
erchuang_dramas = ['祭品公主的生存法则', '替嫁后，沉睡老公超会撩']

print(f'主账号: {original_account}')
print(f'二创账号: {erchuang_account}')
print(f'二创剧: {erchuang_dramas}')

# Filter
orig_data = df_xl[df_xl['视频号昵称'] == original_account]
erc_data = df_xl[df_xl['视频号昵称'] == erchuang_account]

print('\n--- 祭品公主的生存法则 ---')
d1_orig = orig_data[orig_data['剧目名称'] == erchuang_dramas[0]]
d1_erc = erc_data[erc_data['剧目名称'] == erchuang_dramas[0]]
print(f'原创: 播放={d1_orig["视频播放量"].sum()}, 收益={d1_orig["广告收益"].sum():.2f}')
print(f'二创: 播放={d1_erc["视频播放量"].sum()}, 收益={d1_erc["广告收益"].sum():.2f}')

print('\n--- 替嫁后，沉睡老公超会撩 ---')
d2_orig = orig_data[orig_data['剧目名称'] == erchuang_dramas[1]]
d2_erc = erc_data[erc_data['剧目名称'] == erchuang_dramas[1]]
print(f'原创: 播放={d2_orig["视频播放量"].sum()}, 收益={d2_orig["广告收益"].sum():.2f}')
print(f'二创: 播放={d2_erc["视频播放量"].sum()}, 收益={d2_erc["广告收益"].sum():.2f}')

# Compute per-drama wanbo
def wanbo(rev, read):
    if read == 0:
        return 0
    return rev / read * 10000

d1o_rev, d1o_read = d1_orig['广告收益'].sum(), d1_orig['视频播放量'].sum()
d1e_rev, d1e_read = d1_erc['广告收益'].sum(), d1_erc['视频播放量'].sum()
d2o_rev, d2o_read = d2_orig['广告收益'].sum(), d2_orig['视频播放量'].sum()
d2e_rev, d2e_read = d2_erc['广告收益'].sum(), d2_erc['视频播放量'].sum()

print(f'\n祭品公主 - 原创万播: {wanbo(d1o_rev, d1o_read):.2f}, 二创万播: {wanbo(d1e_rev, d1e_read):.2f}')
print(f'替嫁后 - 原创万播: {wanbo(d2o_rev, d2o_read):.2f}, 二创万播: {wanbo(d2e_rev, d2e_read):.2f}')

# Total
total_orig_rev = d1o_rev + d2o_rev
total_orig_read = d1o_read + d2o_read
total_erc_rev = d1e_rev + d2e_rev
total_erc_read = d1e_read + d2e_read
print(f'\n总计 - 原创: 收益{total_orig_rev:.2f}元, 播放{total_orig_read}, 万播{wanbo(total_orig_rev, total_orig_read):.2f}')
print(f'总计 - 二创: 收益{total_erc_rev:.2f}元, 播放{total_erc_read}, 万播{wanbo(total_erc_rev, total_erc_read):.2f}')

# Chart 3: Original vs Erchuang comparison
drama_names = ['祭品公主的生存法则', '替嫁后，沉睡老公超会撩', '两剧合计']
orig_wanbo = [wanbo(d1o_rev, d1o_read), wanbo(d2o_rev, d2o_read), wanbo(total_orig_rev, total_orig_read)]
erc_wanbo = [wanbo(d1e_rev, d1e_read), wanbo(d2e_rev, d2e_read), wanbo(total_erc_rev, total_erc_read)]
orig_rev = [d1o_rev, d2o_rev, total_orig_rev]
erc_rev = [d1e_rev, d2e_rev, total_erc_rev]

x = np.arange(len(drama_names))
width = 0.35

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Wanbo chart
bars1 = axes[0].bar(x - width/2, orig_wanbo, width, label='原创（南瓜动漫短剧场）', color='#2a81d6')
bars2 = axes[0].bar(x + width/2, erc_wanbo, width, label='二创（爱动漫微剧场）', color='#e84c5a')
axes[0].set_title('原创 vs 二创 万播收益对比', fontsize=13, fontweight='bold')
axes[0].set_ylabel('万播收益（元/万播）', fontsize=11)
axes[0].set_xticks(x)
axes[0].set_xticklabels(drama_names)
axes[0].legend()
axes[0].grid(True, alpha=0.3, axis='y')
for bar, val in zip(bars1, orig_wanbo):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{val:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
for bar, val in zip(bars2, erc_wanbo):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{val:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Revenue chart
bars3 = axes[1].bar(x - width/2, orig_rev, width, label='原创（南瓜动漫短剧场）', color='#2a81d6')
bars4 = axes[1].bar(x + width/2, erc_rev, width, label='二创（爱动漫微剧场）', color='#e84c5a')
axes[1].set_title('原创 vs 二创 广告收益对比', fontsize=13, fontweight='bold')
axes[1].set_ylabel('广告收益（元）', fontsize=11)
axes[1].set_xticks(x)
axes[1].set_xticklabels(drama_names)
axes[1].legend()
axes[1].grid(True, alpha=0.3, axis='y')
for bar, val in zip(bars3, orig_rev):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{val:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
for bar, val in zip(bars4, erc_rev):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{val:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig(f'{BASE}/orig_vs_erc.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print('Chart orig_vs_erc.png saved')

# Summary data for docx
print('\n=== SUMMARY ===')
print(f'Data: {drama_names}')
print(f'Orig wanbo: {orig_wanbo}')
print(f'Erc wanbo: {erc_wanbo}')
print(f'Orig rev: {orig_rev}')
print(f'Erc rev: {erc_rev}')
print(f'Daily publish data: {daily_counts.to_dict()}')
print(f'Weekly publish data: {weekly_counts.to_dict()}')

# Save summary
import json
summary = {
    'daily': daily_counts.to_dict('records'),
    'weekly': weekly_counts.to_dict('records'),
    'orig_erc': {
        'drama_names': drama_names,
        'orig_wanbo': orig_wanbo,
        'erc_wanbo': erc_wanbo,
        'orig_rev': orig_rev,
        'erc_rev': erc_rev,
        'd1o': {'rev': d1o_rev, 'read': d1o_read},
        'd1e': {'rev': d1e_rev, 'read': d1e_read},
        'd2o': {'rev': d2o_rev, 'read': d2o_read},
        'd2e': {'rev': d2e_rev, 'read': d2e_read},
    }
}
with open(rf'{BASE}/summary.json', 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print('Summary saved to summary.json')
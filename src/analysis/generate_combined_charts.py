# -*- coding: utf-8 -*-
"""
生成视频号分析图表
- 合并版（南瓜+香蕉）
- 香蕉单独版
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
import numpy as np
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

# ===================== FONTS =====================
plt.rcParams['font.sans-serif'] = ['KaiTi', 'SimKai', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# ===================== PATHS =====================
DATA_DIR = r"D:\Col_tasks\report_writer\data\515_shipinhao"
MERGED_DIR = os.path.join(DATA_DIR, "merged")
CHARTS_DIR = r"D:\Col_tasks\report_writer\assets\charts"

# 输出目录
COMBINED_OUT = os.path.join(CHARTS_DIR, "合并")
BANANA_OUT = os.path.join(CHARTS_DIR, "4_香蕉")
os.makedirs(COMBINED_OUT, exist_ok=True)
os.makedirs(BANANA_OUT, exist_ok=True)

# ===================== COLORS =====================
channel_colors = {'女频': '#e84c5a', '男频': '#2a81d6'}
genre_colors = {
    '都市': '#2ecc71',
    '玄幻': '#9b59b6',
    '末世': '#e67e22',
    '悬疑': '#3498db',
    '游戏': '#f39c12'
}
account_colors = {'南瓜': '#FF8C00', '香蕉': '#FFD700'}


def load_data():
    """加载合并数据"""
    # 日频数据
    daily_excel = os.path.join(MERGED_DIR, "combined_april_data.xlsx")
    xl = pd.ExcelFile(daily_excel)

    df_sum = xl.parse('剧名汇总')
    df_daily = xl.parse('日频明细')

    # 标签数据
    complete_excel = os.path.join(MERGED_DIR, "combined_complete_data.xlsx")
    df_tags = pd.read_excel(complete_excel, sheet_name='剧目分类标签')

    return df_sum, df_daily, df_tags


def prepare_daily_data(df_daily, df_tags):
    """准备日频数据"""
    # 合并标签
    daily = df_daily.merge(df_tags, on=['剧名', '账号'], how='left')

    # 转换日期
    daily['日期'] = pd.to_datetime(daily['日期'])

    # 计算万播收益
    daily['万播收益'] = daily['广告收益'] / daily['阅读量'] * 10000
    daily['万播收益'] = daily['万播收益'].replace([np.inf, -np.inf], np.nan)

    return daily


def get_week(date):
    """获取周标签"""
    day = date.day
    if day <= 5: return 'W1\n4/1-4/5'
    elif day <= 12: return 'W2\n4/6-4/12'
    elif day <= 19: return 'W3\n4/13-4/19'
    elif day <= 26: return 'W4\n4/20-4/26'
    else: return 'W5\n4/27-4/30'


def generate_charts_for_account(daily, monthly, account_filter, output_dir, title_prefix):
    """为指定账号生成图表"""
    print(f"\n{'='*60}")
    print(f"生成图表: {title_prefix}")
    print(f"{'='*60}")

    # 筛选账号数据
    if account_filter:
        daily_acc = daily[daily['账号'] == account_filter].copy()
        monthly_acc = monthly[monthly['账号'] == account_filter].copy()
    else:
        daily_acc = daily.copy()
        monthly_acc = monthly.copy()

    # ===================== 日频聚合 =====================
    # 按频道
    daily_channel = daily_acc.groupby(['日期', '频道']).agg(
        广告收益=('广告收益', 'sum'),
        阅读量=('阅读量', 'sum')
    ).reset_index()
    daily_channel['万播收益'] = daily_channel['广告收益'] / daily_channel['阅读量'] * 10000
    daily_channel['万播收益'] = daily_channel['万播收益'].replace([np.inf, -np.inf], np.nan)

    # 按题材
    daily_genre = daily_acc.groupby(['日期', '题材']).agg(
        广告收益=('广告收益', 'sum'),
        阅读量=('阅读量', 'sum')
    ).reset_index()
    daily_genre['万播收益'] = daily_genre['广告收益'] / daily_genre['阅读量'] * 10000
    daily_genre['万播收益'] = daily_genre['万播收益'].replace([np.inf, -np.inf], np.nan)

    # ===================== 周频聚合 =====================
    daily_acc['周'] = daily_acc['日期'].apply(get_week)
    week_order = ['W1\n4/1-4/5', 'W2\n4/6-4/12', 'W3\n4/13-4/19', 'W4\n4/20-4/26', 'W5\n4/27-4/30']

    week_channel = daily_acc.groupby(['周', '频道']).agg(
        广告收益=('广告收益', 'sum'),
        阅读量=('阅读量', 'sum')
    ).reset_index()
    week_channel['万播收益'] = week_channel['广告收益'] / week_channel['阅读量'] * 10000
    week_channel['万播收益'] = week_channel['万播收益'].replace([np.inf, -np.inf], np.nan)
    week_channel['周'] = pd.Categorical(week_channel['周'], categories=week_order, ordered=True)
    week_channel = week_channel.sort_values(['周', '频道'])

    week_genre = daily_acc.groupby(['周', '题材']).agg(
        广告收益=('广告收益', 'sum'),
        阅读量=('阅读量', 'sum')
    ).reset_index()
    week_genre['万播收益'] = week_genre['广告收益'] / week_genre['阅读量'] * 10000
    week_genre['万播收益'] = week_genre['万播收益'].replace([np.inf, -np.inf], np.nan)
    week_genre['周'] = pd.Categorical(week_genre['周'], categories=week_order, ordered=True)
    week_genre = week_genre.sort_values(['周', '题材'])

    # ===================== 月频聚合 =====================
    monthly_channel = monthly_acc.groupby('频道').agg(
        广告收益=('广告收益', 'sum'),
        阅读量=('阅读量', 'sum')
    ).reset_index()
    monthly_channel['万播收益'] = monthly_channel['广告收益'] / monthly_channel['阅读量'] * 10000

    monthly_genre = monthly_acc.groupby('题材').agg(
        广告收益=('广告收益', 'sum'),
        阅读量=('阅读量', 'sum')
    ).reset_index()
    monthly_genre['万播收益'] = monthly_genre['广告收益'] / monthly_genre['阅读量'] * 10000

    # ===================== 绘图 =====================
    weeks = week_order

    # --- Chart 1: 日频 - 男女频 ---
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    for channel in ['女频', '男频']:
        sub = daily_channel[daily_channel['频道'] == channel].sort_values('日期')
        if len(sub) > 0:
            axes[0].plot(sub['日期'], sub['广告收益'], marker='o', markersize=3,
                         linewidth=2, label=channel, color=channel_colors[channel])
            axes[1].plot(sub['日期'], sub['万播收益'], marker='s', markersize=3,
                         linewidth=2, label=channel, color=channel_colors[channel], linestyle='--')

    axes[0].set_title(f'{title_prefix} - 日频 男女频 广告收益趋势', fontsize=13, fontweight='bold')
    axes[0].set_ylabel('广告收益（元）', fontsize=10)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    axes[0].xaxis.set_major_locator(mdates.DayLocator(interval=3))
    axes[1].set_title(f'{title_prefix} - 日频 男女频 万播收益趋势', fontsize=13, fontweight='bold')
    axes[1].set_ylabel('万播收益（元/万播）', fontsize=10)
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    axes[1].xaxis.set_major_locator(mdates.DayLocator(interval=3))
    plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=45)
    fig.autofmt_xdate(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/chart1_daily_channel.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print('Chart 1 saved: chart1_daily_channel.png')

    # --- Chart 2: 日频 - 题材 ---
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    genres = list(daily_genre['题材'].unique())

    for genre in genres:
        sub = daily_genre[daily_genre['题材'] == genre].sort_values('日期')
        if len(sub) > 0:
            axes[0].plot(sub['日期'], sub['广告收益'], marker='o', markersize=3,
                         linewidth=2, label=genre, color=genre_colors.get(genre, '#888'))
            axes[1].plot(sub['日期'], sub['万播收益'], marker='s', markersize=3,
                         linewidth=2, label=genre, color=genre_colors.get(genre, '#888'), linestyle='--')

    axes[0].set_title(f'{title_prefix} - 日频 题材 广告收益趋势', fontsize=13, fontweight='bold')
    axes[0].set_ylabel('广告收益（元）', fontsize=10)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    axes[0].xaxis.set_major_locator(mdates.DayLocator(interval=3))
    axes[1].set_title(f'{title_prefix} - 日频 题材 万播收益趋势', fontsize=13, fontweight='bold')
    axes[1].set_ylabel('万播收益（元/万播）', fontsize=10)
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    axes[1].xaxis.set_major_locator(mdates.DayLocator(interval=3))
    plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=45)
    fig.autofmt_xdate(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/chart2_daily_genre.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print('Chart 2 saved: chart2_daily_genre.png')

    # --- Chart 3: 周频 - 男女频 ---
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    x = np.arange(len(weeks))
    width = 0.35

    for i, channel in enumerate(['女频', '男频']):
        sub = week_channel[week_channel['频道'] == channel].sort_values('周')
        rev_vals = [sub[sub['周'] == w]['广告收益'].values[0] if w in sub['周'].values and len(sub[sub['周'] == w]) > 0 else 0 for w in weeks]
        wan_vals = [sub[sub['周'] == w]['万播收益'].values[0] if w in sub['周'].values and len(sub[sub['周'] == w]) > 0 else 0 for w in weeks]
        axes[0].bar(x + (i-0.5)*width, rev_vals, width, label=channel, color=channel_colors[channel])
        axes[1].bar(x + (i-0.5)*width, wan_vals, width, label=channel, color=channel_colors[channel])

    axes[0].set_title(f'{title_prefix} - 周频 男女频 广告收益', fontsize=13, fontweight='bold')
    axes[0].set_ylabel('广告收益（元）', fontsize=10)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(weeks)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3, axis='y')
    axes[1].set_title(f'{title_prefix} - 周频 男女频 万播收益', fontsize=13, fontweight='bold')
    axes[1].set_ylabel('万播收益（元/万播）', fontsize=10)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(weeks)
    axes[1].legend()
    axes[1].grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/chart3_weekly_channel.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print('Chart 3 saved: chart3_weekly_channel.png')

    # --- Chart 4: 周频 - 题材 ---
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    genres_all = list(week_genre['题材'].unique())
    x = np.arange(len(weeks))
    n_genres = len(genres_all)
    width = 0.8 / n_genres

    for i, genre in enumerate(genres_all):
        sub = week_genre[week_genre['题材'] == genre].sort_values('周')
        rev_vals = [sub[sub['周'] == w]['广告收益'].values[0] if w in sub['周'].values and len(sub[sub['周'] == w]) > 0 else 0 for w in weeks]
        wan_vals = [sub[sub['周'] == w]['万播收益'].values[0] if w in sub['周'].values and len(sub[sub['周'] == w]) > 0 else 0 for w in weeks]
        offset = (i - (n_genres-1)/2) * width
        axes[0].bar(x + offset, rev_vals, width, label=genre, color=genre_colors.get(genre, '#888'))
        axes[1].bar(x + offset, wan_vals, width, label=genre, color=genre_colors.get(genre, '#888'))

    axes[0].set_title(f'{title_prefix} - 周频 题材 广告收益', fontsize=13, fontweight='bold')
    axes[0].set_ylabel('广告收益（元）', fontsize=10)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(weeks)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3, axis='y')
    axes[1].set_title(f'{title_prefix} - 周频 题材 万播收益', fontsize=13, fontweight='bold')
    axes[1].set_ylabel('万播收益（元/万播）', fontsize=10)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(weeks)
    axes[1].legend()
    axes[1].grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/chart4_weekly_genre.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print('Chart 4 saved: chart4_weekly_genre.png')

    # --- Chart 5: 月频 - 男女频占比 ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))

    if len(monthly_channel) > 0:
        rev_vals = monthly_channel.sort_values('广告收益', ascending=False)
        axes[0].pie(rev_vals['广告收益'], labels=rev_vals['频道'],
                    autopct='%1.1f%%', colors=[channel_colors.get(c, '#888') for c in rev_vals['频道']],
                    startangle=90)
        axes[0].set_title(f'{title_prefix} - 月频 男女频 广告收益占比', fontsize=13, fontweight='bold')

        read_vals = monthly_channel.sort_values('阅读量', ascending=False)
        axes[1].pie(read_vals['阅读量'], labels=read_vals['频道'],
                    autopct='%1.1f%%', colors=[channel_colors.get(c, '#888') for c in read_vals['频道']],
                    startangle=90)
        axes[1].set_title(f'{title_prefix} - 月频 男女频 阅读量占比', fontsize=13, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{output_dir}/chart5_monthly_channel.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print('Chart 5 saved: chart5_monthly_channel.png')

    # --- Chart 6: 月频 - 题材占比 ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))

    if len(monthly_genre) > 0:
        rev_vals = monthly_genre.sort_values('广告收益', ascending=False)
        axes[0].pie(rev_vals['广告收益'], labels=rev_vals['题材'],
                    autopct='%1.1f%%', colors=[genre_colors.get(g, '#888') for g in rev_vals['题材']],
                    startangle=90)
        axes[0].set_title(f'{title_prefix} - 月频 题材 广告收益占比', fontsize=13, fontweight='bold')

        read_vals = monthly_genre.sort_values('阅读量', ascending=False)
        axes[1].pie(read_vals['阅读量'], labels=read_vals['题材'],
                    autopct='%1.1f%%', colors=[genre_colors.get(g, '#888') for g in read_vals['题材']],
                    startangle=90)
        axes[1].set_title(f'{title_prefix} - 月频 题材 阅读量占比', fontsize=13, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{output_dir}/chart6_monthly_genre.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print('Chart 6 saved: chart6_monthly_genre.png')

    # 返回月度汇总数据
    return {
        'monthly_channel': monthly_channel,
        'monthly_genre': monthly_genre,
        'monthly': monthly_acc
    }


def generate_publish_charts(df_sum, output_dir, title_prefix):
    """生成上架节奏图表"""
    # 加载上架时间数据
    banana_works = os.path.join(DATA_DIR, "4_香蕉", "works_list.csv")
    pumpkin_works = os.path.join(DATA_DIR, "4_南瓜", "works_list.csv")

    works_list = []

    if os.path.exists(banana_works):
        df_b = pd.read_csv(banana_works)
        df_b['账号'] = '香蕉'
        works_list.append(df_b)

    if os.path.exists(pumpkin_works):
        df_p = pd.read_csv(pumpkin_works)
        df_p['账号'] = '南瓜'
        works_list.append(df_p)

    if not works_list:
        print("无上架时间数据，跳过")
        return

    df_works = pd.concat(works_list, ignore_index=True)

    # 转换日期
    df_works['上架日期'] = pd.to_datetime(df_works['上架日期'], errors='coerce')
    df_works = df_works[df_works['上架日期'].notna()]

    # 筛选4月数据
    df_works = df_works[(df_works['上架日期'] >= '2026-04-01') &
                        (df_works['上架日期'] <= '2026-04-30')]

    if len(df_works) == 0:
        print("无4月上架数据，跳过")
        return

    # 日频发布统计
    daily_publish = df_works.groupby('上架日期').size().reset_index(name='剧数')

    # 周频发布统计
    df_works['周'] = df_works['上架日期'].apply(get_week)
    week_order = ['W1\n4/1-4/5', 'W2\n4/6-4/12', 'W3\n4/13-4/19', 'W4\n4/20-4/26', 'W5\n4/27-4/30']
    weekly_publish = df_works.groupby('周').size().reset_index(name='剧数')
    weekly_publish['周'] = pd.Categorical(weekly_publish['周'], categories=week_order, ordered=True)
    weekly_publish = weekly_publish.sort_values('周')

    # 绘制日频图
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(daily_publish['上架日期'], daily_publish['剧数'], marker='o', linewidth=2, color='#3498db')
    ax.fill_between(daily_publish['上架日期'], daily_publish['剧数'], alpha=0.3, color='#3498db')
    ax.set_title(f'{title_prefix} - 发布剧数日频趋势', fontsize=13, fontweight='bold')
    ax.set_ylabel('发布剧数', fontsize=10)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/publish_daily.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print('Chart saved: publish_daily.png')

    # 绘制周频图
    fig, ax = plt.subplots(figsize=(10, 5))
    weeks = [w for w in week_order if w in weekly_publish['周'].values]
    vals = [weekly_publish[weekly_publish['周'] == w]['剧数'].values[0] if w in weekly_publish['周'].values else 0 for w in weeks]
    ax.bar(range(len(weeks)), vals, color='#9b59b6')
    ax.set_xticks(range(len(weeks)))
    ax.set_xticklabels(weeks)
    ax.set_title(f'{title_prefix} - 发布剧数周频统计', fontsize=13, fontweight='bold')
    ax.set_ylabel('发布剧数', fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')

    # 添加数值标签
    for i, v in enumerate(vals):
        ax.text(i, v + 0.1, str(v), ha='center', fontsize=11)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/publish_weekly.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print('Chart saved: publish_weekly.png')


if __name__ == "__main__":
    print("=" * 60)
    print("视频号分析图表生成")
    print("=" * 60)

    # 加载数据
    print("\n加载数据...")
    df_sum, df_daily, df_tags = load_data()

    # 合并标签到汇总数据
    monthly = df_sum.merge(df_tags, on=['剧名', '账号'], how='left')
    monthly['万播收益'] = monthly['广告收益'] / monthly['阅读量'] * 10000
    monthly['万播收益'] = monthly['万播收益'].replace([np.inf, -np.inf], np.nan)

    # 准备日频数据
    daily = prepare_daily_data(df_daily, df_tags)

    print(f"日频数据: {len(daily)} 条")
    print(f"月度数据: {len(monthly)} 部剧目")

    # ===================== 生成合并图表 =====================
    combined_stats = generate_charts_for_account(
        daily, monthly,
        account_filter=None,  # 全部数据
        output_dir=COMBINED_OUT,
        title_prefix="南瓜+香蕉"
    )

    generate_publish_charts(df_sum, COMBINED_OUT, "南瓜+香蕉")

    # ===================== 生成香蕉图表 =====================
    banana_stats = generate_charts_for_account(
        daily, monthly,
        account_filter='香蕉',
        output_dir=BANANA_OUT,
        title_prefix="香蕉"
    )

    # 香蕉上架图表
    banana_works = os.path.join(DATA_DIR, "4_香蕉", "works_list.csv")
    if os.path.exists(banana_works):
        df_bw = pd.read_csv(banana_works)
        df_bw['账号'] = '香蕉'
        df_bw['上架日期'] = pd.to_datetime(df_bw['上架日期'], errors='coerce')
        df_bw = df_bw[df_bw['上架日期'].notna()]
        df_bw = df_bw[(df_bw['上架日期'] >= '2026-04-01') & (df_bw['上架日期'] <= '2026-04-30')]

        if len(df_bw) > 0:
            df_bw['周'] = df_bw['上架日期'].apply(get_week)
            week_order = ['W1\n4/1-4/5', 'W2\n4/6-4/12', 'W3\n4/13-4/19', 'W4\n4/20-4/26', 'W5\n4/27-4/30']

            # 日频
            daily_pub = df_bw.groupby('上架日期').size().reset_index(name='剧数')
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(daily_pub['上架日期'], daily_pub['剧数'], marker='o', linewidth=2, color='#FFD700')
            ax.fill_between(daily_pub['上架日期'], daily_pub['剧数'], alpha=0.3, color='#FFD700')
            ax.set_title('香蕉 - 发布剧数日频趋势', fontsize=13, fontweight='bold')
            ax.set_ylabel('发布剧数', fontsize=10)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(f'{BANANA_OUT}/publish_daily.png', dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            print('Chart saved: publish_daily.png (香蕉)')

            # 周频
            weekly_pub = df_bw.groupby('周').size().reset_index(name='剧数')
            weekly_pub['周'] = pd.Categorical(weekly_pub['周'], categories=week_order, ordered=True)
            weekly_pub = weekly_pub.sort_values('周')

            fig, ax = plt.subplots(figsize=(10, 5))
            weeks = [w for w in week_order if w in weekly_pub['周'].values]
            vals = [weekly_pub[weekly_pub['周'] == w]['剧数'].values[0] if w in weekly_pub['周'].values else 0 for w in weeks]
            ax.bar(range(len(weeks)), vals, color='#FFD700')
            ax.set_xticks(range(len(weeks)))
            ax.set_xticklabels(weeks)
            ax.set_title('香蕉 - 发布剧数周频统计', fontsize=13, fontweight='bold')
            ax.set_ylabel('发布剧数', fontsize=10)
            ax.grid(True, alpha=0.3, axis='y')
            for i, v in enumerate(vals):
                ax.text(i, v + 0.1, str(v), ha='center', fontsize=11)
            plt.tight_layout()
            plt.savefig(f'{BANANA_OUT}/publish_weekly.png', dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            print('Chart saved: publish_weekly.png (香蕉)')

    # ===================== 输出统计 =====================
    print("\n" + "=" * 60)
    print("统计汇总")
    print("=" * 60)

    print("\n【合并数据】")
    print("频道分布:")
    print(combined_stats['monthly_channel'].to_string(index=False))
    print("\n题材分布:")
    print(combined_stats['monthly_genre'].to_string(index=False))

    print("\n【香蕉数据】")
    print("频道分布:")
    print(banana_stats['monthly_channel'].to_string(index=False))
    print("\n题材分布:")
    print(banana_stats['monthly_genre'].to_string(index=False))

    print("\n" + "=" * 60)
    print("图表生成完成!")
    print(f"合并图表目录: {COMBINED_OUT}")
    print(f"香蕉图表目录: {BANANA_OUT}")
    print("=" * 60)

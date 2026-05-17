# -*- coding: utf-8 -*-
"""
周频与月频数据综合分析图表
- 周频：柱状图dashboard
- 月频：饼图dashboard
- 按题材（玄幻/都市/末世）和频道（男频/女频）分类
- 指标：播放量、广告收益、万播收益
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['KaiTi', 'SimKai', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 路径配置
DATA_DIR = r"D:\Col_tasks\report_writer\data\515_shipinhao\merged"
OUTPUT_DIR = r"D:\Col_tasks\report_writer\assets\charts\final\daily"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 颜色配置（与日频一致）
GENRE_COLORS = {'玄幻': '#9b59b6', '都市': '#2ecc71', '末世': '#e67e22'}
CHANNEL_COLORS = {'男频': '#3498db', '女频': '#e74c3c'}


def load_data():
    """加载数据"""
    daily_excel = os.path.join(DATA_DIR, "combined_april_data.xlsx")
    tags_excel = os.path.join(DATA_DIR, "combined_complete_data.xlsx")

    df_daily = pd.read_excel(daily_excel, sheet_name='日频明细')
    df_tags = pd.read_excel(tags_excel, sheet_name='剧目分类标签')

    df = df_daily.merge(df_tags[['剧名', '账号', '频道', '题材']], on=['剧名', '账号'], how='left')
    df['日期'] = pd.to_datetime(df['日期'])

    # 题材合并：悬疑->都市, 游戏->玄幻
    df['题材'] = df['题材'].replace({'悬疑': '都市', '游戏': '玄幻'})

    return df


def get_week(date):
    """获取周标签"""
    day = date.day
    if day <= 5: return 'W1\n4/1-5'
    elif day <= 12: return 'W2\n4/6-12'
    elif day <= 19: return 'W3\n4/13-19'
    elif day <= 26: return 'W4\n4/20-26'
    else: return 'W5\n4/27-30'


def aggregate_weekly(df):
    """周频聚合"""
    df['周'] = df['日期'].apply(get_week)
    week_order = ['W1\n4/1-5', 'W2\n4/6-12', 'W3\n4/13-19', 'W4\n4/20-26', 'W5\n4/27-30']

    # 按周和题材
    weekly_genre = df.groupby(['周', '题材']).agg({
        '阅读量': 'sum',
        '广告收益': 'sum'
    }).reset_index()
    weekly_genre['万播收益'] = weekly_genre['广告收益'] / weekly_genre['阅读量'] * 10000
    weekly_genre['周'] = pd.Categorical(weekly_genre['周'], categories=week_order, ordered=True)
    weekly_genre = weekly_genre.sort_values('周')

    # 按周和频道
    weekly_channel = df.groupby(['周', '频道']).agg({
        '阅读量': 'sum',
        '广告收益': 'sum'
    }).reset_index()
    weekly_channel['万播收益'] = weekly_channel['广告收益'] / weekly_channel['阅读量'] * 10000
    weekly_channel['周'] = pd.Categorical(weekly_channel['周'], categories=week_order, ordered=True)
    weekly_channel = weekly_channel.sort_values('周')

    return weekly_genre, weekly_channel, week_order


def aggregate_monthly(df):
    """月频聚合"""
    # 按题材
    monthly_genre = df.groupby('题材').agg({
        '阅读量': 'sum',
        '广告收益': 'sum'
    }).reset_index()
    monthly_genre['万播收益'] = monthly_genre['广告收益'] / monthly_genre['阅读量'] * 10000

    # 按频道
    monthly_channel = df.groupby('频道').agg({
        '阅读量': 'sum',
        '广告收益': 'sum'
    }).reset_index()
    monthly_channel['万播收益'] = monthly_channel['广告收益'] / monthly_channel['阅读量'] * 10000

    return monthly_genre, monthly_channel


def create_weekly_dashboard(weekly_genre, weekly_channel, week_order, output_dir):
    """创建周频dashboard"""
    fig = plt.figure(figsize=(16, 12))

    x = np.arange(len(week_order))
    width = 0.25

    # ========== 左上：题材-播放量 ==========
    ax1 = fig.add_subplot(2, 3, 1)
    for i, genre in enumerate(['玄幻', '都市', '末世']):
        data = weekly_genre[weekly_genre['题材'] == genre]
        vals = [data[data['周'] == w]['阅读量'].values[0] if len(data[data['周'] == w]) > 0 else 0 for w in week_order]
        ax1.bar(x + (i-1)*width, vals, width, label=genre, color=GENRE_COLORS[genre])
    ax1.set_xticks(x)
    ax1.set_xticklabels(['W1', 'W2', 'W3', 'W4', 'W5'])
    ax1.set_title('播放量 - 按题材', fontsize=11, fontweight='bold')
    ax1.set_ylabel('播放量')
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3, axis='y')

    # ========== 中上：题材-广告收益 ==========
    ax2 = fig.add_subplot(2, 3, 2)
    for i, genre in enumerate(['玄幻', '都市', '末世']):
        data = weekly_genre[weekly_genre['题材'] == genre]
        vals = [data[data['周'] == w]['广告收益'].values[0] if len(data[data['周'] == w]) > 0 else 0 for w in week_order]
        ax2.bar(x + (i-1)*width, vals, width, label=genre, color=GENRE_COLORS[genre])
    ax2.set_xticks(x)
    ax2.set_xticklabels(['W1', 'W2', 'W3', 'W4', 'W5'])
    ax2.set_title('广告收益 - 按题材', fontsize=11, fontweight='bold')
    ax2.set_ylabel('收益（元）')
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3, axis='y')

    # ========== 右上：题材-万播收益 ==========
    ax3 = fig.add_subplot(2, 3, 3)
    for i, genre in enumerate(['玄幻', '都市', '末世']):
        data = weekly_genre[weekly_genre['题材'] == genre]
        vals = [data[data['周'] == w]['万播收益'].values[0] if len(data[data['周'] == w]) > 0 and data[data['周'] == w]['阅读量'].values[0] > 0 else 0 for w in week_order]
        ax3.bar(x + (i-1)*width, vals, width, label=genre, color=GENRE_COLORS[genre])
    ax3.set_xticks(x)
    ax3.set_xticklabels(['W1', 'W2', 'W3', 'W4', 'W5'])
    ax3.set_title('万播收益 - 按题材', fontsize=11, fontweight='bold')
    ax3.set_ylabel('元/万播')
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3, axis='y')

    # ========== 左下：频道-播放量 ==========
    ax4 = fig.add_subplot(2, 3, 4)
    width2 = 0.35
    for i, channel in enumerate(['男频', '女频']):
        data = weekly_channel[weekly_channel['频道'] == channel]
        vals = [data[data['周'] == w]['阅读量'].values[0] if len(data[data['周'] == w]) > 0 else 0 for w in week_order]
        ax4.bar(x + (i-0.5)*width2, vals, width2, label=channel, color=CHANNEL_COLORS[channel])
    ax4.set_xticks(x)
    ax4.set_xticklabels(['W1', 'W2', 'W3', 'W4', 'W5'])
    ax4.set_title('播放量 - 按频道', fontsize=11, fontweight='bold')
    ax4.set_ylabel('播放量')
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3, axis='y')

    # ========== 中下：频道-广告收益 ==========
    ax5 = fig.add_subplot(2, 3, 5)
    for i, channel in enumerate(['男频', '女频']):
        data = weekly_channel[weekly_channel['频道'] == channel]
        vals = [data[data['周'] == w]['广告收益'].values[0] if len(data[data['周'] == w]) > 0 else 0 for w in week_order]
        ax5.bar(x + (i-0.5)*width2, vals, width2, label=channel, color=CHANNEL_COLORS[channel])
    ax5.set_xticks(x)
    ax5.set_xticklabels(['W1', 'W2', 'W3', 'W4', 'W5'])
    ax5.set_title('广告收益 - 按频道', fontsize=11, fontweight='bold')
    ax5.set_ylabel('收益（元）')
    ax5.legend(fontsize=8)
    ax5.grid(True, alpha=0.3, axis='y')

    # ========== 右下：频道-万播收益 ==========
    ax6 = fig.add_subplot(2, 3, 6)
    for i, channel in enumerate(['男频', '女频']):
        data = weekly_channel[weekly_channel['频道'] == channel]
        vals = [data[data['周'] == w]['万播收益'].values[0] if len(data[data['周'] == w]) > 0 and data[data['周'] == w]['阅读量'].values[0] > 0 else 0 for w in week_order]
        ax6.bar(x + (i-0.5)*width2, vals, width2, label=channel, color=CHANNEL_COLORS[channel])
    ax6.set_xticks(x)
    ax6.set_xticklabels(['W1', 'W2', 'W3', 'W4', 'W5'])
    ax6.set_title('万播收益 - 按频道', fontsize=11, fontweight='bold')
    ax6.set_ylabel('元/万播')
    ax6.legend(fontsize=8)
    ax6.grid(True, alpha=0.3, axis='y')

    plt.suptitle('汇总 周频数据 题材', fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()

    output_path = os.path.join(output_dir, 'weekly_dashboard.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'保存: {output_path}')


def create_monthly_dashboard(monthly_genre, monthly_channel, output_dir):
    """创建月频dashboard"""
    fig = plt.figure(figsize=(16, 10))

    # ========== 第一行：题材饼图 ==========
    # 播放量
    ax1 = fig.add_subplot(2, 3, 1)
    colors = [GENRE_COLORS[g] for g in monthly_genre['题材']]
    ax1.pie(monthly_genre['阅读量'], labels=monthly_genre['题材'], autopct='%1.1f%%',
            colors=colors, startangle=90)
    ax1.set_title('播放量占比 - 按题材', fontsize=11, fontweight='bold')

    # 广告收益
    ax2 = fig.add_subplot(2, 3, 2)
    ax2.pie(monthly_genre['广告收益'], labels=monthly_genre['题材'], autopct='%1.1f%%',
            colors=colors, startangle=90)
    ax2.set_title('广告收益占比 - 按题材', fontsize=11, fontweight='bold')

    # 万播收益（用柱状图更直观）
    ax3 = fig.add_subplot(2, 3, 3)
    bars = ax3.bar(monthly_genre['题材'], monthly_genre['万播收益'], color=colors)
    ax3.set_title('万播收益 - 按题材', fontsize=11, fontweight='bold')
    ax3.set_ylabel('元/万播')
    ax3.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars, monthly_genre['万播收益']):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, f'{val:.1f}',
                ha='center', va='bottom', fontsize=9)

    # ========== 第二行：频道饼图 ==========
    # 播放量
    ax4 = fig.add_subplot(2, 3, 4)
    colors_ch = [CHANNEL_COLORS[c] for c in monthly_channel['频道']]
    ax4.pie(monthly_channel['阅读量'], labels=monthly_channel['频道'], autopct='%1.1f%%',
            colors=colors_ch, startangle=90)
    ax4.set_title('播放量占比 - 按频道', fontsize=11, fontweight='bold')

    # 广告收益
    ax5 = fig.add_subplot(2, 3, 5)
    ax5.pie(monthly_channel['广告收益'], labels=monthly_channel['频道'], autopct='%1.1f%%',
            colors=colors_ch, startangle=90)
    ax5.set_title('广告收益占比 - 按频道', fontsize=11, fontweight='bold')

    # 万播收益
    ax6 = fig.add_subplot(2, 3, 6)
    bars = ax6.bar(monthly_channel['频道'], monthly_channel['万播收益'], color=colors_ch)
    ax6.set_title('万播收益 - 按频道', fontsize=11, fontweight='bold')
    ax6.set_ylabel('元/万播')
    ax6.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars, monthly_channel['万播收益']):
        ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, f'{val:.1f}',
                ha='center', va='bottom', fontsize=9)

    plt.suptitle('汇总 月频数据 题材', fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()

    output_path = os.path.join(output_dir, 'monthly_dashboard.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'保存: {output_path}')


def print_summary(weekly_genre, weekly_channel, monthly_genre, monthly_channel):
    """打印汇总数据"""
    print("\n" + "=" * 60)
    print("周频数据汇总")
    print("=" * 60)

    print("\n【按题材汇总】")
    genre_sum = weekly_genre.groupby('题材').agg({'阅读量': 'sum', '广告收益': 'sum'}).reset_index()
    genre_sum['万播收益'] = genre_sum['广告收益'] / genre_sum['阅读量'] * 10000
    print(genre_sum.to_string(index=False))

    print("\n【按频道汇总】")
    channel_sum = weekly_channel.groupby('频道').agg({'阅读量': 'sum', '广告收益': 'sum'}).reset_index()
    channel_sum['万播收益'] = channel_sum['广告收益'] / channel_sum['阅读量'] * 10000
    print(channel_sum.to_string(index=False))

    print("\n" + "=" * 60)
    print("月频数据汇总")
    print("=" * 60)

    print("\n【按题材汇总】")
    print(monthly_genre.to_string(index=False))

    print("\n【按频道汇总】")
    print(monthly_channel.to_string(index=False))


if __name__ == "__main__":
    print("=" * 60)
    print("周频与月频数据综合分析")
    print("=" * 60)

    # 加载数据
    df = load_data()
    print(f"数据条数: {len(df)}")

    # 周频聚合
    weekly_genre, weekly_channel, week_order = aggregate_weekly(df)

    # 月频聚合
    monthly_genre, monthly_channel = aggregate_monthly(df)

    # 生成图表
    print("\n生成图表...")
    create_weekly_dashboard(weekly_genre, weekly_channel, week_order, OUTPUT_DIR)
    create_monthly_dashboard(monthly_genre, monthly_channel, OUTPUT_DIR)

    # 打印汇总
    print_summary(weekly_genre, weekly_channel, monthly_genre, monthly_channel)

    print("\n" + "=" * 60)
    print("完成!")
    print(f"输出目录: {OUTPUT_DIR}")
    print("=" * 60)

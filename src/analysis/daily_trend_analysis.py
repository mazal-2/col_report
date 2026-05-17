# -*- coding: utf-8 -*-
"""
日频数据综合分析图表
- 按题材（玄幻/末世/都市）统计日频广告收益和播放量
- 按频道（男频/女频）统计日频广告收益和播放量
- 标注峰值高亮区域
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import numpy as np
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['KaiTi', 'SimKai', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 路径配置
DATA_DIR = r"D:\Col_tasks\report_writer\data\515_shipinhao\merged"
OUTPUT_DIR = r"D:\Col_tasks\report_writer\assets\charts\final"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_data():
    """加载数据"""
    # 日频数据
    daily_excel = os.path.join(DATA_DIR, "combined_april_data.xlsx")
    df_daily = pd.read_excel(daily_excel, sheet_name='日频明细')

    # 标签数据
    tags_excel = os.path.join(DATA_DIR, "combined_complete_data.xlsx")
    df_tags = pd.read_excel(tags_excel, sheet_name='剧目分类标签')

    # 合并标签
    df = df_daily.merge(df_tags[['剧名', '账号', '频道', '题材']], on=['剧名', '账号'], how='left')

    # 转换日期
    df['日期'] = pd.to_datetime(df['日期'])

    # 将悬疑和游戏合并到相近类别
    # 悬疑->都市, 游戏->玄幻
    df['题材'] = df['题材'].replace({'悬疑': '都市', '游戏': '玄幻'})

    return df


def find_peak_periods(daily_sum, value_col, min_days=3, threshold_pct=0.7):
    """找出连续表现较好的时间段"""
    daily_sum = daily_sum.sort_values('日期').reset_index(drop=True)

    # 计算阈值
    threshold = daily_sum[value_col].quantile(threshold_pct)

    # 找出超过阈值的日期
    daily_sum['is_peak'] = daily_sum[value_col] >= threshold

    # 找连续区间
    peak_periods = []
    start_idx = None

    for i, row in daily_sum.iterrows():
        if row['is_peak']:
            if start_idx is None:
                start_idx = i
        else:
            if start_idx is not None:
                end_idx = i - 1
                if end_idx - start_idx + 1 >= min_days:
                    peak_periods.append((daily_sum.loc[start_idx, '日期'],
                                        daily_sum.loc[end_idx, '日期']))
                start_idx = None

    # 检查最后一个区间
    if start_idx is not None:
        end_idx = len(daily_sum) - 1
        if end_idx - start_idx + 1 >= min_days:
            peak_periods.append((daily_sum.loc[start_idx, '日期'],
                                daily_sum.loc[end_idx, '日期']))

    return peak_periods


def create_genre_daily_chart(df, output_dir):
    """按题材生成日频图表"""
    # 按日期和题材汇总
    daily_genre = df.groupby(['日期', '题材']).agg({
        '阅读量': 'sum',
        '广告收益': 'sum'
    }).reset_index()

    # 题材颜色
    genre_colors = {'玄幻': '#9b59b6', '都市': '#2ecc71', '末世': '#e67e22'}

    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    # ========== 播放量趋势 ==========
    ax1 = axes[0]
    for genre in ['玄幻', '都市', '末世']:
        data = daily_genre[daily_genre['题材'] == genre].sort_values('日期')
        if len(data) > 0:
            ax1.plot(data['日期'], data['阅读量'], marker='o', markersize=3,
                    linewidth=2, label=genre, color=genre_colors.get(genre, '#888'))

    ax1.set_title('日频播放量趋势 - 按题材分类', fontsize=14, fontweight='bold')
    ax1.set_ylabel('播放量', fontsize=11)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=2))

    # ========== 广告收益趋势 ==========
    ax2 = axes[1]
    for genre in ['玄幻', '都市', '末世']:
        data = daily_genre[daily_genre['题材'] == genre].sort_values('日期')
        if len(data) > 0:
            ax2.plot(data['日期'], data['广告收益'], marker='o', markersize=3,
                    linewidth=2, label=genre, color=genre_colors.get(genre, '#888'))

    ax2.set_title('日频广告收益趋势 - 按题材分类', fontsize=14, fontweight='bold')
    ax2.set_ylabel('广告收益（元）', fontsize=11)
    ax2.set_xlabel('日期', fontsize=11)
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax2.xaxis.set_major_locator(mdates.DayLocator(interval=2))

    plt.tight_layout()

    output_path = os.path.join(output_dir, 'daily_genre_trend.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'保存: {output_path}')
    return output_path


def create_channel_daily_chart(df, output_dir):
    """按频道生成日频图表（含峰值高亮）"""
    # 按日期和频道汇总
    daily_channel = df.groupby(['日期', '频道']).agg({
        '阅读量': 'sum',
        '广告收益': 'sum'
    }).reset_index()

    # 频道颜色
    channel_colors = {'男频': '#3498db', '女频': '#e74c3c'}

    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    # ========== 播放量趋势 ==========
    ax1 = axes[0]

    # 先绘制总面积作为背景
    daily_total = df.groupby('日期')['阅读量'].sum().reset_index()
    ax1.fill_between(daily_total['日期'], daily_total['阅读量'], alpha=0.1, color='gray')

    # 找峰值区间
    peak_periods = find_peak_periods(daily_total, '阅读量', min_days=3, threshold_pct=0.75)

    # 高亮峰值区间
    for start, end in peak_periods:
        ax1.axvspan(start, end, alpha=0.2, color='#f39c12', label='峰值区间' if start == peak_periods[0][0] else '')

    for channel in ['男频', '女频']:
        data = daily_channel[daily_channel['频道'] == channel].sort_values('日期')
        if len(data) > 0:
            ax1.plot(data['日期'], data['阅读量'], marker='o', markersize=3,
                    linewidth=2.5, label=channel, color=channel_colors[channel])

    ax1.set_title('日频播放量趋势 - 按频道分类（峰值高亮）', fontsize=14, fontweight='bold')
    ax1.set_ylabel('播放量', fontsize=11)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=2))

    # ========== 广告收益趋势 ==========
    ax2 = axes[1]

    # 先绘制总面积作为背景
    daily_total_rev = df.groupby('日期')['广告收益'].sum().reset_index()
    ax2.fill_between(daily_total_rev['日期'], daily_total_rev['广告收益'], alpha=0.1, color='gray')

    # 找峰值区间
    peak_periods_rev = find_peak_periods(daily_total_rev, '广告收益', min_days=3, threshold_pct=0.75)

    # 高亮峰值区间
    for start, end in peak_periods_rev:
        ax2.axvspan(start, end, alpha=0.2, color='#f39c12', label='峰值区间' if start == peak_periods_rev[0][0] else '')

    for channel in ['男频', '女频']:
        data = daily_channel[daily_channel['频道'] == channel].sort_values('日期')
        if len(data) > 0:
            ax2.plot(data['日期'], data['广告收益'], marker='o', markersize=3,
                    linewidth=2.5, label=channel, color=channel_colors[channel])

    ax2.set_title('日频广告收益趋势 - 按频道分类（峰值高亮）', fontsize=14, fontweight='bold')
    ax2.set_ylabel('广告收益（元）', fontsize=11)
    ax2.set_xlabel('日期', fontsize=11)
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax2.xaxis.set_major_locator(mdates.DayLocator(interval=2))

    plt.tight_layout()

    output_path = os.path.join(output_dir, 'daily_channel_trend.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'保存: {output_path}')
    return output_path


def create_combined_dashboard(df, output_dir):
    """创建综合日频仪表板"""
    # 按日期汇总
    daily_total = df.groupby('日期').agg({
        '阅读量': 'sum',
        '广告收益': 'sum'
    }).reset_index()
    daily_total = daily_total.sort_values('日期')

    # 按题材汇总
    daily_genre = df.groupby(['日期', '题材']).agg({
        '阅读量': 'sum',
        '广告收益': 'sum'
    }).reset_index()

    # 按频道汇总
    daily_channel = df.groupby(['日期', '频道']).agg({
        '阅读量': 'sum',
        '广告收益': 'sum'
    }).reset_index()

    # 颜色配置
    genre_colors = {'玄幻': '#9b59b6', '都市': '#2ecc71', '末世': '#e67e22'}
    channel_colors = {'男频': '#3498db', '女频': '#e74c3c'}

    # 创建图表
    fig = plt.figure(figsize=(16, 12))

    # ========== 左上：总播放量和收益 ==========
    ax1 = fig.add_subplot(2, 2, 1)

    # 找峰值区间
    peak_periods = find_peak_periods(daily_total, '阅读量', min_days=3, threshold_pct=0.75)
    for start, end in peak_periods:
        ax1.axvspan(start, end, alpha=0.15, color='#f39c12')

    ax1.fill_between(daily_total['日期'], daily_total['阅读量'], alpha=0.3, color='#3498db')
    ax1.plot(daily_total['日期'], daily_total['阅读量'], linewidth=2, color='#3498db')
    ax1.set_title('总播放量趋势（峰值高亮）', fontsize=12, fontweight='bold')
    ax1.set_ylabel('播放量')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax1.grid(True, alpha=0.3)

    # ========== 右上：总收益趋势 ==========
    ax2 = fig.add_subplot(2, 2, 2)

    peak_periods_rev = find_peak_periods(daily_total, '广告收益', min_days=3, threshold_pct=0.75)
    for start, end in peak_periods_rev:
        ax2.axvspan(start, end, alpha=0.15, color='#f39c12')

    ax2.fill_between(daily_total['日期'], daily_total['广告收益'], alpha=0.3, color='#e74c3c')
    ax2.plot(daily_total['日期'], daily_total['广告收益'], linewidth=2, color='#e74c3c')
    ax2.set_title('总广告收益趋势（峰值高亮）', fontsize=12, fontweight='bold')
    ax2.set_ylabel('广告收益（元）')
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax2.grid(True, alpha=0.3)

    # ========== 左下：按题材播放量 ==========
    ax3 = fig.add_subplot(2, 2, 3)
    for genre in ['玄幻', '都市', '末世']:
        data = daily_genre[daily_genre['题材'] == genre].sort_values('日期')
        if len(data) > 0:
            ax3.plot(data['日期'], data['阅读量'], marker='o', markersize=2,
                    linewidth=2, label=genre, color=genre_colors.get(genre, '#888'))
    ax3.set_title('播放量 - 按题材', fontsize=12, fontweight='bold')
    ax3.set_ylabel('播放量')
    ax3.set_xlabel('日期')
    ax3.legend()
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax3.grid(True, alpha=0.3)

    # ========== 右下：按频道收益 ==========
    ax4 = fig.add_subplot(2, 2, 4)
    for channel in ['男频', '女频']:
        data = daily_channel[daily_channel['频道'] == channel].sort_values('日期')
        if len(data) > 0:
            ax4.plot(data['日期'], data['广告收益'], marker='o', markersize=2,
                    linewidth=2, label=channel, color=channel_colors[channel])
    ax4.set_title('广告收益 - 按频道', fontsize=12, fontweight='bold')
    ax4.set_ylabel('广告收益（元）')
    ax4.set_xlabel('日期')
    ax4.legend()
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax4.grid(True, alpha=0.3)

    plt.suptitle('日频数据综合分析 Dashboard', fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()

    output_path = os.path.join(output_dir, 'daily_combined_dashboard.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'保存: {output_path}')
    return output_path, peak_periods, peak_periods_rev


if __name__ == "__main__":
    print("=" * 60)
    print("日频数据综合分析图表生成")
    print("=" * 60)

    # 加载数据
    df = load_data()
    print(f"数据条数: {len(df)}")
    print(f"日期范围: {df['日期'].min().date()} ~ {df['日期'].max().date()}")

    print("\n题材分布:")
    print(df.groupby('题材')['剧名'].nunique())

    print("\n频道分布:")
    print(df.groupby('频道')['剧名'].nunique())

    # 生成图表
    print("\n生成图表...")
    create_genre_daily_chart(df, OUTPUT_DIR)
    create_channel_daily_chart(df, OUTPUT_DIR)
    output_path, peak_views, peak_rev = create_combined_dashboard(df, OUTPUT_DIR)

    # 输出峰值区间
    print("\n【播放量峰值区间】")
    for start, end in peak_views:
        print(f"  {start.strftime('%m/%d')} - {end.strftime('%m/%d')}")

    print("\n【广告收益峰值区间】")
    for start, end in peak_rev:
        print(f"  {start.strftime('%m/%d')} - {end.strftime('%m/%d')}")

    print("\n" + "=" * 60)
    print("完成!")
    print(f"输出目录: {OUTPUT_DIR}")
    print("=" * 60)

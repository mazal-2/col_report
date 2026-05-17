# -*- coding: utf-8 -*-
"""
合并上架节奏统计
整合香蕉和南瓜两个账号的剧目上架时间数据
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['KaiTi', 'SimKai', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 路径配置
DATA_DIR = r"D:\Col_tasks\report_writer\data\515_shipinhao"
OUTPUT_DIR = r"D:\Col_tasks\report_writer\assets\charts\合并"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_banana_data():
    """加载香蕉上架数据"""
    path = os.path.join(DATA_DIR, "4_香蕉", "works_list.csv")
    if not os.path.exists(path):
        print("香蕉上架数据不存在")
        return pd.DataFrame()

    df = pd.read_csv(path)
    df = df[['剧名', '上架日期']].copy()
    df.columns = ['剧名', '日期']
    df['账号'] = '香蕉'
    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
    return df


def load_pumpkin_data():
    """加载南瓜上架数据"""
    path = os.path.join(DATA_DIR, "4_南瓜", "works_list.csv")
    if not os.path.exists(path):
        print("南瓜上架数据不存在")
        return pd.DataFrame()

    df = pd.read_csv(path)
    df = df[['dramaName', 'publishDate']].copy()
    df.columns = ['剧名', '日期']
    df['账号'] = '南瓜'
    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
    return df


def get_week(date):
    """获取周标签"""
    if pd.isna(date):
        return '未知'
    day = date.day
    if day <= 5: return 'W1\n4/1-4/5'
    elif day <= 12: return 'W2\n4/6-4/12'
    elif day <= 19: return 'W3\n4/13-4/19'
    elif day <= 26: return 'W4\n4/20-4/26'
    else: return 'W5\n4/27-4/30'


def analyze_publish_rhythm(df):
    """分析上架节奏"""
    # 筛选4月数据
    df_april = df[(df['日期'] >= '2026-04-01') & (df['日期'] <= '2026-04-30')].copy()

    print(f"4月上架剧目数: {len(df_april)}")
    print(f"  - 香蕉: {len(df_april[df_april['账号']=='香蕉'])} 部")
    print(f"  - 南瓜: {len(df_april[df_april['账号']=='南瓜'])} 部")

    # 日频统计
    daily = df_april.groupby(['日期', '账号']).size().unstack(fill_value=0).reset_index()
    daily['合计'] = daily.get('香蕉', 0) + daily.get('南瓜', 0)

    # 周频统计
    df_april['周'] = df_april['日期'].apply(get_week)
    week_order = ['W1\n4/1-4/5', 'W2\n4/6-4/12', 'W3\n4/13-4/19', 'W4\n4/20-4/26', 'W5\n4/27-4/30']
    weekly = df_april.groupby(['周', '账号']).size().unstack(fill_value=0).reset_index()
    weekly['合计'] = weekly.get('香蕉', 0) + weekly.get('南瓜', 0)
    weekly['周'] = pd.Categorical(weekly['周'], categories=week_order, ordered=True)
    weekly = weekly.sort_values('周')

    return df_april, daily, weekly


def create_daily_chart(df_april, output_dir):
    """生成日频上架图"""
    # 按日期汇总
    daily_all = df_april.groupby('日期').size().reset_index(name='剧数')

    fig, ax = plt.subplots(figsize=(14, 5))

    ax.bar(daily_all['日期'], daily_all['剧数'], color='#9b59b6', width=0.8)

    ax.set_title('合并 - 发布剧数日频统计', fontsize=14, fontweight='bold')
    ax.set_xlabel('日期')
    ax.set_ylabel('发布剧数')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax.grid(True, alpha=0.3, axis='y')

    # 添加数值标签
    for idx, row in daily_all.iterrows():
        ax.text(row['日期'], row['剧数'] + 0.1, str(row['剧数']),
               ha='center', va='bottom', fontsize=9)

    plt.xticks(rotation=45)
    plt.tight_layout()

    output_path = os.path.join(output_dir, 'publish_daily_combined.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'保存: {output_path}')
    return output_path


def create_weekly_chart(weekly, output_dir):
    """生成周频上架图"""
    fig, ax = plt.subplots(figsize=(10, 5))

    x = np.arange(len(weekly))
    width = 0.35

    # 分别绘制香蕉和南瓜
    banana_vals = weekly.get('香蕉', pd.Series([0]*len(weekly))).values if '香蕉' in weekly.columns else [0]*len(weekly)
    pumpkin_vals = weekly.get('南瓜', pd.Series([0]*len(weekly))).values if '南瓜' in weekly.columns else [0]*len(weekly)

    bars1 = ax.bar(x - width/2, banana_vals, width, label='香蕉', color='#FFD700')
    bars2 = ax.bar(x + width/2, pumpkin_vals, width, label='南瓜', color='#FF8C00')

    ax.set_xticks(x)
    ax.set_xticklabels(weekly['周'])
    ax.set_title('合并 - 发布剧数周频统计', fontsize=14, fontweight='bold')
    ax.set_ylabel('发布剧数')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    # 添加数值标签
    for bar, val in zip(bars1, banana_vals):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), str(val),
                   ha='center', va='bottom', fontsize=10)
    for bar, val in zip(bars2, pumpkin_vals):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), str(val),
                   ha='center', va='bottom', fontsize=10)

    plt.tight_layout()

    output_path = os.path.join(output_dir, 'publish_weekly_combined.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'保存: {output_path}')
    return output_path


def create_comparison_chart(df_april, output_dir):
    """生成账号对比图"""
    # 按账号和日期统计
    daily_by_acc = df_april.groupby(['日期', '账号']).size().unstack(fill_value=0).reset_index()

    fig, axes = plt.subplots(2, 1, figsize=(14, 8))

    colors = {'香蕉': '#FFD700', '南瓜': '#FF8C00'}

    # 日频趋势
    ax1 = axes[0]
    for acc in ['香蕉', '南瓜']:
        if acc in daily_by_acc.columns:
            ax1.plot(daily_by_acc['日期'], daily_by_acc[acc], marker='o',
                    label=acc, color=colors[acc], linewidth=2)

    ax1.set_title('日发布剧数趋势', fontsize=13, fontweight='bold')
    ax1.set_ylabel('发布剧数')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 累计趋势
    ax2 = axes[1]
    for acc in ['香蕉', '南瓜']:
        if acc in daily_by_acc.columns:
            daily_by_acc[f'{acc}_累计'] = daily_by_acc[acc].cumsum()
            ax2.plot(daily_by_acc['日期'], daily_by_acc[f'{acc}_累计'], marker='o',
                    label=acc, color=colors[acc], linewidth=2)

    ax2.set_title('累计发布剧数趋势', fontsize=13, fontweight='bold')
    ax2.set_ylabel('累计剧数')
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    output_path = os.path.join(output_dir, 'publish_comparison.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'保存: {output_path}')
    return output_path


if __name__ == "__main__":
    print("=" * 60)
    print("合并上架节奏统计")
    print("=" * 60)

    # 加载数据
    print("\n加载数据...")
    df_banana = load_banana_data()
    df_pumpkin = load_pumpkin_data()

    print(f"香蕉剧目数: {len(df_banana)}")
    print(f"南瓜剧目数: {len(df_pumpkin)}")

    # 合并数据
    df = pd.concat([df_banana, df_pumpkin], ignore_index=True)
    df = df.dropna(subset=['日期'])

    print(f"\n合并后剧目数: {len(df)}")
    print(f"日期范围: {df['日期'].min()} ~ {df['日期'].max()}")

    # 分析上架节奏
    print("\n" + "=" * 60)
    print("4月上架节奏分析")
    print("=" * 60)
    df_april, daily, weekly = analyze_publish_rhythm(df)

    print("\n【周频统计】")
    print(weekly.to_string(index=False))

    # 生成图表
    print("\n" + "=" * 60)
    print("生成图表")
    print("=" * 60)

    create_daily_chart(df_april, OUTPUT_DIR)
    create_weekly_chart(weekly, OUTPUT_DIR)
    create_comparison_chart(df_april, OUTPUT_DIR)

    # 保存汇总数据
    output_csv = os.path.join(OUTPUT_DIR, 'publish_summary.csv')
    weekly.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f'\n汇总数据保存: {output_csv}')

    print("\n" + "=" * 60)
    print("完成!")
    print("=" * 60)

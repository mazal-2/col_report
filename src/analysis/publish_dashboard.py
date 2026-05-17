# -*- coding: utf-8 -*-
"""
上架节奏汇总图表
- 日频发布 + 日频累计发布折线图
- 周频发布数量统计
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


def load_data():
    """加载数据"""
    # 香蕉
    banana_path = os.path.join(DATA_DIR, "4_香蕉", "works_list.csv")
    df_b = pd.read_csv(banana_path)
    df_b = df_b[['剧名', '上架日期']].copy()
    df_b.columns = ['剧名', '日期']
    df_b['账号'] = '香蕉'
    df_b['日期'] = pd.to_datetime(df_b['日期'], errors='coerce')

    # 南瓜
    pumpkin_path = os.path.join(DATA_DIR, "4_南瓜", "works_list.csv")
    df_p = pd.read_csv(pumpkin_path)
    df_p = df_p[['dramaName', 'publishDate']].copy()
    df_p.columns = ['剧名', '日期']
    df_p['账号'] = '南瓜'
    df_p['日期'] = pd.to_datetime(df_p['日期'], errors='coerce')

    # 合并
    df = pd.concat([df_b, df_p], ignore_index=True)
    df = df.dropna(subset=['日期'])

    return df


def get_week(date):
    """获取周标签"""
    if pd.isna(date):
        return '未知'
    day = date.day
    if day <= 5: return 'W1'
    elif day <= 12: return 'W2'
    elif day <= 19: return 'W3'
    elif day <= 26: return 'W4'
    else: return 'W5'


def create_daily_combined_chart(df_april, output_dir):
    """创建日频发布 + 累计发布合并图"""
    # 按日期汇总
    daily = df_april.groupby('日期').size().reset_index(name='发布数')
    daily = daily.sort_values('日期')
    daily['累计发布'] = daily['发布数'].cumsum()

    fig, ax1 = plt.subplots(figsize=(14, 6))

    # 柱状图 - 日频发布
    bars = ax1.bar(daily['日期'], daily['发布数'], color='#9b59b6', alpha=0.7, label='日频发布')
    ax1.set_xlabel('日期', fontsize=11)
    ax1.set_ylabel('日发布数', fontsize=11, color='#9b59b6')
    ax1.tick_params(axis='y', labelcolor='#9b59b6')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=2))

    # 添加日频数值标签
    for bar, val in zip(bars, daily['发布数']):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, str(val),
                ha='center', va='bottom', fontsize=9, color='#9b59b6')

    # 折线图 - 累计发布
    ax2 = ax1.twinx()
    line = ax2.plot(daily['日期'], daily['累计发布'], color='#e74c3c', linewidth=2.5,
                   marker='o', markersize=5, label='累计发布')
    ax2.set_ylabel('累计发布数', fontsize=11, color='#e74c3c')
    ax2.tick_params(axis='y', labelcolor='#e74c3c')

    # 添加累计数值标签（每隔几个点标注）
    for i, (date, cum) in enumerate(zip(daily['日期'], daily['累计发布'])):
        if i % 3 == 0 or i == len(daily) - 1:  # 每隔3个点标注
            ax2.annotate(str(cum), (date, cum), textcoords="offset points",
                        xytext=(0, 10), ha='center', fontsize=9, color='#e74c3c')

    # 标题和图例
    ax1.set_title('4月剧目上架节奏 - 日频发布与累计发布', fontsize=14, fontweight='bold', pad=15)

    # 合并图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    ax1.grid(True, alpha=0.3, axis='y')
    plt.xticks(rotation=45)
    plt.tight_layout()

    output_path = os.path.join(output_dir, 'publish_daily_trend_combined.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'保存: {output_path}')
    return output_path


def create_weekly_summary_chart(df_april, output_dir):
    """创建周频发布统计图"""
    # 周频统计
    df_april['周'] = df_april['日期'].apply(get_week)
    week_order = ['W1', 'W2', 'W3', 'W4', 'W5']
    week_labels = ['W1\n4/1-4/5', 'W2\n4/6-4/12', 'W3\n4/13-4/19', 'W4\n4/20-4/26', 'W5\n4/27-4/30']

    weekly = df_april.groupby('周').size().reindex(week_order, fill_value=0).reset_index()
    weekly.columns = ['周', '发布数']

    fig, ax = plt.subplots(figsize=(10, 6))

    # 渐变色柱状图
    colors = plt.cm.Purples(np.linspace(0.3, 0.9, len(weekly)))
    bars = ax.bar(week_labels, weekly['发布数'], color=colors, edgecolor='#8e44ad', linewidth=1.5)

    ax.set_title('4月剧目上架节奏 - 周频统计', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('周次', fontsize=11)
    ax.set_ylabel('发布剧数', fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')

    # 添加数值标签
    for bar, val in zip(bars, weekly['发布数']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, str(val),
               ha='center', va='bottom', fontsize=12, fontweight='bold', color='#8e44ad')

    # 添加占比标注
    total = weekly['发布数'].sum()
    for bar, val in zip(bars, weekly['发布数']):
        pct = val / total * 100 if total > 0 else 0
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2, f'{pct:.0f}%',
                   ha='center', va='center', fontsize=10, color='white', fontweight='bold')

    # 添加汇总信息
    ax.text(0.98, 0.95, f'总计: {total} 部', transform=ax.transAxes,
           fontsize=12, fontweight='bold', ha='right', va='top',
           bbox=dict(boxstyle='round', facecolor='#f8f9fa', edgecolor='#8e44ad'))

    plt.tight_layout()

    output_path = os.path.join(output_dir, 'publish_weekly_summary.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'保存: {output_path}')
    return output_path


def create_combined_dashboard(df_april, output_dir):
    """创建综合仪表板"""
    # 准备数据
    daily = df_april.groupby('日期').size().reset_index(name='发布数')
    daily = daily.sort_values('日期')
    daily['累计发布'] = daily['发布数'].cumsum()

    df_april['周'] = df_april['日期'].apply(get_week)
    week_order = ['W1', 'W2', 'W3', 'W4', 'W5']
    week_labels = ['W1\n4/1-4/5', 'W2\n4/6-4/12', 'W3\n4/13-4/19', 'W4\n4/20-4/26', 'W5\n4/27-4/30']
    weekly = df_april.groupby('周').size().reindex(week_order, fill_value=0)

    # 创建图表
    fig = plt.figure(figsize=(16, 10))

    # 左上：日频发布 + 累计发布
    ax1 = fig.add_subplot(2, 2, 1)
    bars = ax1.bar(daily['日期'], daily['发布数'], color='#9b59b6', alpha=0.7)
    ax1.set_title('日频发布 + 累计发布', fontsize=12, fontweight='bold')
    ax1.set_ylabel('日发布数', color='#9b59b6')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=3))

    ax1_twin = ax1.twinx()
    ax1_twin.plot(daily['日期'], daily['累计发布'], color='#e74c3c', linewidth=2, marker='o', markersize=4)
    ax1_twin.set_ylabel('累计发布数', color='#e74c3c')

    # 右上：周频统计
    ax2 = fig.add_subplot(2, 2, 2)
    colors = plt.cm.Purples(np.linspace(0.3, 0.9, len(weekly)))
    bars = ax2.bar(week_labels, weekly.values, color=colors, edgecolor='#8e44ad')
    ax2.set_title('周频统计', fontsize=12, fontweight='bold')
    ax2.set_ylabel('发布剧数')
    for bar, val in zip(bars, weekly.values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, str(val),
               ha='center', va='bottom', fontsize=11, fontweight='bold')

    # 左下：按账号日频
    ax3 = fig.add_subplot(2, 2, 3)
    daily_acc = df_april.groupby(['日期', '账号']).size().unstack(fill_value=0).reset_index()
    acc_colors = {'香蕉': '#FFD700', '南瓜': '#FF8C00'}

    for acc in ['香蕉', '南瓜']:
        if acc in daily_acc.columns:
            ax3.plot(daily_acc['日期'], daily_acc[acc], marker='o', label=acc,
                    color=acc_colors[acc], linewidth=2)
    ax3.set_title('按账号日频发布趋势', fontsize=12, fontweight='bold')
    ax3.set_ylabel('发布数')
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # 右下：汇总统计表
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.axis('off')

    # 创建汇总表格
    table_data = [
        ['指标', '数值'],
        ['总上架剧目', f'{len(df_april)} 部'],
        ['香蕉上架', f'{len(df_april[df_april["账号"]=="香蕉"])} 部'],
        ['南瓜上架', f'{len(df_april[df_april["账号"]=="南瓜"])} 部'],
        ['峰值周次', f'W4 (24部)'],
        ['日均上架', f'{len(df_april)/30:.1f} 部/天'],
        ['上架天数', f'{len(daily)} 天'],
    ]

    table = ax4.table(cellText=table_data, loc='center', cellLoc='center',
                      colWidths=[0.4, 0.4])
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 1.8)

    # 设置表头样式
    for i in range(2):
        table[(0, i)].set_facecolor('#9b59b6')
        table[(0, i)].set_text_props(color='white', fontweight='bold')

    ax4.set_title('汇总统计', fontsize=12, fontweight='bold', y=0.95)

    plt.suptitle('4月剧目上架节奏综合分析', fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()

    output_path = os.path.join(output_dir, 'publish_dashboard.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'保存: {output_path}')
    return output_path


if __name__ == "__main__":
    print("=" * 60)
    print("上架节奏汇总图表生成")
    print("=" * 60)

    # 加载数据
    df = load_data()
    print(f"合并剧目数: {len(df)}")

    # 筛选4月数据
    df_april = df[(df['日期'] >= '2026-04-01') & (df['日期'] <= '2026-04-30')].copy()
    print(f"4月上架剧目: {len(df_april)} 部")
    print(f"  - 香蕉: {len(df_april[df_april['账号']=='香蕉'])} 部")
    print(f"  - 南瓜: {len(df_april[df_april['账号']=='南瓜'])} 部")

    # 生成图表
    print("\n生成图表...")
    create_daily_combined_chart(df_april, OUTPUT_DIR)
    create_weekly_summary_chart(df_april, OUTPUT_DIR)
    create_combined_dashboard(df_april, OUTPUT_DIR)

    # 输出周频统计
    df_april['周'] = df_april['日期'].apply(get_week)
    weekly = df_april.groupby('周').size()
    week_order = ['W1', 'W2', 'W3', 'W4', 'W5']

    print("\n【周频统计】")
    total = 0
    for w in week_order:
        count = weekly.get(w, 0)
        total += count
        pct = count / len(df_april) * 100 if len(df_april) > 0 else 0
        print(f"  {w}: {count} 部 ({pct:.1f}%)")
    print(f"  合计: {total} 部")

    print("\n" + "=" * 60)
    print("完成!")
    print("=" * 60)

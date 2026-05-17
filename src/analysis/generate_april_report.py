# -*- coding: utf-8 -*-
"""
视频号4月数据分析报告生成
整合香蕉和南瓜两个账号的数据
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei']
matplotlib.rcParams['axes.unicode_minus'] = False

# 路径配置
DATA_DIR = r"D:\Col_tasks\report_writer\data\515_shipinhao"
MERGED_DIR = os.path.join(DATA_DIR, "merged")
OUTPUT_DIR = os.path.join(DATA_DIR, "report")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_all_data():
    """加载所有数据"""
    # 日频数据
    daily_excel = os.path.join(MERGED_DIR, "combined_april_data.xlsx")
    df_raw = pd.read_excel(daily_excel, sheet_name='原始数据')
    df_sum = pd.read_excel(daily_excel, sheet_name='剧名汇总')
    df_daily = pd.read_excel(daily_excel, sheet_name='日频明细')

    # 完整数据
    complete_excel = os.path.join(MERGED_DIR, "combined_complete_data.xlsx")
    df_follow = pd.read_excel(complete_excel, sheet_name='关注者增长')
    df_video = pd.read_excel(complete_excel, sheet_name='视频详情')
    df_mount = pd.read_excel(complete_excel, sheet_name='剧集挂载数据')
    df_tags = pd.read_excel(complete_excel, sheet_name='剧目分类标签')

    return {
        'raw': df_raw,
        'summary': df_sum,
        'daily': df_daily,
        'follow': df_follow,
        'video': df_video,
        'mount': df_mount,
        'tags': df_tags
    }


def create_account_overview_chart(data):
    """账号概览图表"""
    df_sum = data['summary']

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1. 按账号统计
    acc_stats = df_sum.groupby('账号').agg({
        '阅读量': 'sum',
        '广告收益': 'sum'
    }).reset_index()

    colors = {'南瓜': '#FF8C00', '香蕉': '#FFD700'}

    # 阅读量对比
    ax1 = axes[0, 0]
    bars = ax1.bar(acc_stats['账号'], acc_stats['阅读量'], color=[colors[a] for a in acc_stats['账号']])
    ax1.set_title('阅读量对比', fontsize=14, fontweight='bold')
    ax1.set_ylabel('阅读量')
    for bar, val in zip(bars, acc_stats['阅读量']):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{val:,.0f}',
                ha='center', va='bottom', fontsize=11)

    # 广告收益对比
    ax2 = axes[0, 1]
    bars = ax2.bar(acc_stats['账号'], acc_stats['广告收益'], color=[colors[a] for a in acc_stats['账号']])
    ax2.set_title('广告收益对比', fontsize=14, fontweight='bold')
    ax2.set_ylabel('广告收益(元)')
    for bar, val in zip(bars, acc_stats['广告收益']):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{val:.2f}',
                ha='center', va='bottom', fontsize=11)

    # 万播收益对比
    ax3 = axes[1, 0]
    acc_stats['万播收益'] = acc_stats['广告收益'] / acc_stats['阅读量'] * 10000
    bars = ax3.bar(acc_stats['账号'], acc_stats['万播收益'], color=[colors[a] for a in acc_stats['账号']])
    ax3.set_title('万播收益对比', fontsize=14, fontweight='bold')
    ax3.set_ylabel('万播收益(元)')
    for bar, val in zip(bars, acc_stats['万播收益']):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{val:.2f}',
                ha='center', va='bottom', fontsize=11)

    # 剧目数量对比
    ax4 = axes[1, 1]
    drama_count = df_sum.groupby('账号').size()
    bars = ax4.bar(drama_count.index, drama_count.values, color=[colors[a] for a in drama_count.index])
    ax4.set_title('剧目数量对比', fontsize=14, fontweight='bold')
    ax4.set_ylabel('剧目数')
    for bar, val in zip(bars, drama_count.values):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{val}',
                ha='center', va='bottom', fontsize=11)

    plt.suptitle('账号核心指标对比', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, 'account_overview.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'保存: {output_path}')
    return output_path


def create_top_dramas_chart(data):
    """广告收益Top剧目图表"""
    df_sum = data['summary'].head(15)

    fig, ax = plt.subplots(figsize=(12, 8))

    # 简化剧名
    df_sum['短名'] = df_sum['剧名'].apply(lambda x: x[:12] + '...' if len(x) > 12 else x)

    colors = [ '#FF8C00' if a == '南瓜' else '#FFD700' for a in df_sum['账号']]

    bars = ax.barh(range(len(df_sum)), df_sum['广告收益'], color=colors)
    ax.set_yticks(range(len(df_sum)))
    ax.set_yticklabels(df_sum['短名'])
    ax.invert_yaxis()
    ax.set_xlabel('广告收益(元)')
    ax.set_title('广告收益 Top 15 剧目', fontsize=14, fontweight='bold')

    # 添加数值标签
    for bar, val in zip(bars, df_sum['广告收益']):
        ax.text(bar.get_width(), bar.get_y() + bar.get_height()/2, f' {val:.2f}',
               va='center', fontsize=10)

    # 图例
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='#FF8C00', label='南瓜'),
                       Patch(facecolor='#FFD700', label='香蕉')]
    ax.legend(handles=legend_elements, loc='lower right')

    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, 'top_dramas.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'保存: {output_path}')
    return output_path


def create_genre_analysis_chart(data):
    """题材分析图表"""
    df_tags = data['tags']
    df_sum = data['summary']

    # 合并标签到汇总数据
    df_merged = df_sum.merge(df_tags, on=['剧名', '账号'], how='left')

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # 1. 题材分布
    ax1 = axes[0]
    genre_count = df_tags['题材'].value_counts()
    colors = plt.cm.Set3(np.linspace(0, 1, len(genre_count)))
    wedges, texts, autotexts = ax1.pie(genre_count.values, labels=genre_count.index,
                                        autopct='%1.1f%%', colors=colors, startangle=90)
    ax1.set_title('剧目题材分布', fontsize=14, fontweight='bold')

    # 2. 题材收益分析
    ax2 = axes[1]
    genre_revenue = df_merged.groupby('题材')['广告收益'].sum().sort_values(ascending=True)
    bars = ax2.barh(genre_revenue.index, genre_revenue.values, color=plt.cm.Set3(np.linspace(0, 1, len(genre_revenue))))
    ax2.set_xlabel('广告收益(元)')
    ax2.set_title('各题材广告收益', fontsize=14, fontweight='bold')
    for bar, val in zip(bars, genre_revenue.values):
        ax2.text(bar.get_width(), bar.get_y() + bar.get_height()/2, f' {val:.2f}',
                va='center', fontsize=10)

    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, 'genre_analysis.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'保存: {output_path}')
    return output_path


def create_daily_trend_chart(data):
    """日频趋势图表"""
    df_daily = data['daily']

    # 按日期和账号汇总
    daily_sum = df_daily.groupby(['日期', '账号']).agg({
        '阅读量': 'sum',
        '广告收益': 'sum'
    }).reset_index()

    fig, axes = plt.subplots(2, 1, figsize=(14, 8))

    colors = {'南瓜': '#FF8C00', '香蕉': '#FFD700'}

    # 1. 阅读量趋势
    ax1 = axes[0]
    for acc in ['南瓜', '香蕉']:
        df_acc = daily_sum[daily_sum['账号'] == acc].sort_values('日期')
        ax1.plot(range(len(df_acc)), df_acc['阅读量'], marker='o', label=acc, color=colors[acc])
    ax1.set_title('日阅读量趋势', fontsize=14, fontweight='bold')
    ax1.set_ylabel('阅读量')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 2. 广告收益趋势
    ax2 = axes[1]
    for acc in ['南瓜', '香蕉']:
        df_acc = daily_sum[daily_sum['账号'] == acc].sort_values('日期')
        ax2.plot(range(len(df_acc)), df_acc['广告收益'], marker='o', label=acc, color=colors[acc])
    ax2.set_title('日广告收益趋势', fontsize=14, fontweight='bold')
    ax2.set_ylabel('广告收益(元)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, 'daily_trend.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'保存: {output_path}')
    return output_path


def create_follower_chart(data):
    """关注者增长图表"""
    df_follow = data['follow']

    if df_follow.empty or df_follow['账号'].nunique() == 0:
        print('无关注者数据，跳过图表生成')
        return None

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 只显示香蕉数据
    df_banana = df_follow[df_follow['账号'] == '香蕉'].sort_values('时间')

    # 1. 关注者总数变化
    ax1 = axes[0]
    ax1.plot(range(len(df_banana)), df_banana['关注者总数'], marker='o', color='#FFD700')
    ax1.set_title('香蕉账号关注者总数变化', fontsize=14, fontweight='bold')
    ax1.set_ylabel('关注者数')
    ax1.grid(True, alpha=0.3)

    # 2. 每日净增关注
    ax2 = axes[1]
    colors = ['green' if x > 0 else 'red' for x in df_banana['净增关注']]
    ax2.bar(range(len(df_banana)), df_banana['净增关注'], color=colors)
    ax2.set_title('香蕉账号每日净增关注', fontsize=14, fontweight='bold')
    ax2.set_ylabel('净增关注')
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, 'follower_trend.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'保存: {output_path}')
    return output_path


def generate_report_text(data):
    """生成报告文本"""
    df_sum = data['summary']
    df_tags = data['tags']
    df_follow = data['follow']
    df_video = data['video']

    # 计算关键指标
    total_views = df_sum['阅读量'].sum()
    total_revenue = df_sum['广告收益'].sum()
    total_dramas = len(df_sum)

    # 按账号统计
    acc_stats = df_sum.groupby('账号').agg({
        '阅读量': 'sum',
        '广告收益': 'sum'
    }).reset_index()
    acc_stats['万播收益'] = acc_stats['广告收益'] / acc_stats['阅读量'] * 10000

    # 题材统计
    df_merged = df_sum.merge(df_tags, on=['剧名', '账号'], how='left')
    genre_revenue = df_merged.groupby('题材')['广告收益'].sum().sort_values(ascending=False)

    # Top剧目
    top_drama = df_sum.iloc[0]

    # 生成报告
    report = f"""# 视频号4月数据分析报告

## 一、总体概览

2026年4月，视频号运营覆盖 **香蕉** 和 **南瓜** 两个账号，共计 **{total_dramas}** 部剧目。

### 核心数据指标

| 指标 | 数值 |
|------|------|
| 总阅读量 | {total_views:,} |
| 总广告收益 | {total_revenue:.2f} 元 |
| 万播收益 | {total_revenue/total_views*10000:.2f} 元 |
| 剧目数量 | {total_dramas} 部 |

## 二、账号对比分析

"""

    # 添加账号对比表
    report += "| 账号 | 阅读量 | 广告收益(元) | 万播收益(元) | 剧目数 |\n"
    report += "|------|--------|--------------|--------------|--------|\n"

    for _, row in acc_stats.iterrows():
        acc = row['账号']
        drama_count = len(df_sum[df_sum['账号'] == acc])
        report += f"| {acc} | {row['阅读量']:,.0f} | {row['广告收益']:.2f} | {row['万播收益']:.2f} | {drama_count} |\n"

    # 分析结论
    pumpkin_views = acc_stats[acc_stats['账号'] == '南瓜']['阅读量'].values[0]
    banana_views = acc_stats[acc_stats['账号'] == '香蕉']['阅读量'].values[0]

    report += f"""
**分析要点：**

1. **南瓜账号表现突出**：阅读量占比 {pumpkin_views/total_views*100:.1f}%，广告收益占比 {acc_stats[acc_stats['账号']=='南瓜']['广告收益'].values[0]/total_revenue*100:.1f}%
2. **香蕉账号起步阶段**：4月为该账号运营首月，关注者从1人增长至97人
3. **万播收益差异**：南瓜({acc_stats[acc_stats['账号']=='南瓜']['万播收益'].values[0]:.2f}元) > 香蕉({acc_stats[acc_stats['账号']=='香蕉']['万播收益'].values[0]:.2f}元)

## 三、剧目表现分析

### 3.1 头部剧目

**收益冠军**：《{top_drama['剧名']}》（{top_drama['账号']}）
- 阅读量：{top_drama['阅读量']:,}
- 广告收益：{top_drama['广告收益']:.2f} 元
- 占总收益比例：{top_drama['广告收益']/total_revenue*100:.1f}%

### 3.2 Top 10 剧目

"""

    # Top 10 表格
    report += "| 排名 | 剧名 | 账号 | 阅读量 | 广告收益(元) |\n"
    report += "|------|------|------|--------|--------------|\n"
    for i, row in df_sum.head(10).iterrows():
        report += f"| {df_sum.head(10).index.get_loc(i)+1} | {row['剧名'][:15]} | {row['账号']} | {row['阅读量']:,} | {row['广告收益']:.2f} |\n"

    # 题材分析
    report += f"""
## 四、题材分析

### 4.1 题材分布

"""

    # 题材统计表
    genre_count = df_tags['题材'].value_counts()
    report += "| 题材 | 剧目数 | 占比 | 广告收益(元) |\n"
    report += "|------|--------|------|--------------|\n"
    for genre in genre_count.index:
        count = genre_count[genre]
        revenue = genre_revenue.get(genre, 0)
        report += f"| {genre} | {count} | {count/total_dramas*100:.1f}% | {revenue:.2f} |\n"

    # 频道分析
    channel_count = df_tags['频道'].value_counts()
    report += f"""
### 4.2 频道分布

| 频道 | 剧目数 | 占比 |
|------|--------|------|
| 男频 | {channel_count.get('男频', 0)} | {channel_count.get('男频', 0)/total_dramas*100:.1f}% |
| 女频 | {channel_count.get('女频', 0)} | {channel_count.get('女频', 0)/total_dramas*100:.1f}% |

## 五、关注者分析

"""

    # 关注者数据
    df_banana_follow = df_follow[df_follow['账号'] == '香蕉']
    if len(df_banana_follow) > 0:
        start_follow = df_banana_follow['关注者总数'].iloc[-1]  # 排序后最后是4月初
        end_follow = df_banana_follow['关注者总数'].iloc[0]    # 排序后第一个是4月末
        net_gain = df_banana_follow['净增关注'].sum()

        report += f"""### 香蕉账号

- 月初关注者：{start_follow:.0f} 人
- 月末关注者：{end_follow:.0f} 人
- 净增关注：{net_gain:.0f} 人

**注意**：南瓜账号暂无关注者增长数据。

## 六、总结与建议

### 6.1 主要发现

1. **南瓜账号成熟稳定**：内容定位清晰，收益表现优异
2. **香蕉账号处于孵化期**：内容以男频玄幻为主，用户积累初期
3. **女频题材收益更佳**：女频题材剧目虽少但单剧收益更高
4. **题材差异化明显**：南瓜偏女频都市，香蕉专注男频玄幻

### 6.2 优化建议

1. **南瓜账号**：继续深耕女频都市题材，保持内容质量
2. **香蕉账号**：加强用户运营，提升关注转化率
3. **题材拓展**：考虑在玄安卓材中探索高收益细分赛道
4. **数据监控**：完善南瓜账号的关注者数据采集

---
*报告生成时间：2026年5月16日*
"""

    return report


if __name__ == "__main__":
    print("=" * 60)
    print("视频号4月数据分析报告生成")
    print("=" * 60)

    # 加载数据
    print("\n加载数据...")
    data = load_all_data()
    print(f"  剧目汇总: {len(data['summary'])} 部")
    print(f"  日频明细: {len(data['daily'])} 条")
    print(f"  分类标签: {len(data['tags'])} 条")

    # 生成图表
    print("\n生成图表...")
    create_account_overview_chart(data)
    create_top_dramas_chart(data)
    create_genre_analysis_chart(data)
    create_daily_trend_chart(data)
    create_follower_chart(data)

    # 生成报告
    print("\n生成报告文本...")
    report_text = generate_report_text(data)

    report_path = os.path.join(OUTPUT_DIR, "april_analysis_report.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_text)
    print(f"保存: {report_path}")

    print("\n" + "=" * 60)
    print("报告生成完成!")
    print(f"输出目录: {OUTPUT_DIR}")
    print("=" * 60)

    # 显示报告预览
    print("\n" + report_text[:2000] + "\n...")

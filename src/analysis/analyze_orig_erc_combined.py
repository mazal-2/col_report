# -*- coding: utf-8 -*-
"""
合并两个账号的原创/二创对比分析
四个核心账号：香蕉轻漫剧场(原创)、南瓜动漫短剧场(原创)、馒头动漫短剧场(二创)、飞姐漫剧推荐(二创)
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
DATA_DIR = r"D:\Col_tasks\report_writer\data\515_shipinhao"
OUTPUT_DIR = r"D:\Col_tasks\report_writer\assets\charts\合并"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 核心账号定义
CORE_ACCOUNTS = {
    '香蕉轻漫剧场': {'类型': '原创', '归属': '香蕉'},
    '南瓜动漫短剧场': {'类型': '原创', '归属': '南瓜'},
    '馒头动漫短剧场': {'类型': '二创', '归属': '香蕉'},
    '爱动漫微剧场': {'类型': '二创', '归属': '南瓜'},
}


def load_and_merge_data():
    """加载并合并两份数据"""
    df_banana = pd.read_excel(
        os.path.join(DATA_DIR, "4_香蕉", "xj_april_erchaung_yuanju.xlsx"),
        sheet_name='原生剧集挂载数据明细'
    )
    df_pumpkin = pd.read_excel(
        os.path.join(DATA_DIR, "4_南瓜", "南瓜-视频号4月剧集数据统计_2026-05-11-5 copy.xlsx"),
        sheet_name='原生剧集挂载数据明细'
    )

    df = pd.concat([df_banana, df_pumpkin], ignore_index=True)
    return df


def process_core_accounts(df):
    """处理四个核心账号数据"""
    # 筛选核心账号
    df_core = df[df['视频号昵称'].isin(CORE_ACCOUNTS.keys())].copy()

    # 添加账号类型和归属
    df_core['账号类型'] = df_core['视频号昵称'].map(lambda x: CORE_ACCOUNTS[x]['类型'])
    df_core['归属账号'] = df_core['视频号昵称'].map(lambda x: CORE_ACCOUNTS[x]['归属'])

    # 计算万播收益
    df_core['万播收益'] = df_core['广告收益'] / df_core['剧集播放量'] * 10000
    df_core['万播收益'] = df_core['万播收益'].replace([np.inf, -np.inf], np.nan)

    return df_core


def analyze_by_account_type(df_core):
    """按原创/二创分组分析"""
    # 按账号类型汇总
    summary = df_core.groupby('账号类型').agg({
        '视频播放量': 'sum',
        '剧集播放量': 'sum',
        '广告收益': 'sum'
    }).reset_index()
    summary['万播收益'] = summary['广告收益'] / summary['剧集播放量'] * 10000

    return summary


def analyze_by_account(df_core):
    """按单个账号分析"""
    # 按视频号昵称汇总
    summary = df_core.groupby(['视频号昵称', '账号类型', '归属账号']).agg({
        '视频播放量': 'sum',
        '剧集播放量': 'sum',
        '广告收益': 'sum'
    }).reset_index()
    summary['万播收益'] = summary['广告收益'] / summary['剧集播放量'] * 10000
    summary = summary.sort_values(['账号类型', '广告收益'], ascending=[True, False])

    return summary


def analyze_drama_overlap(df_core):
    """分析原创二创剧目重叠"""
    # 获取各类型剧目列表
    yuan_dramas = set(df_core[df_core['账号类型'] == '原创']['剧目名称'].unique())
    erc_dramas = set(df_core[df_core['账号类型'] == '二创']['剧目名称'].unique())

    overlap_dramas = yuan_dramas & erc_dramas

    print(f"原创剧目数: {len(yuan_dramas)}")
    print(f"二创剧目数: {len(erc_dramas)}")
    print(f"重叠剧目数: {len(overlap_dramas)}")

    # 筛选重叠剧目数据
    df_overlap = df_core[df_core['剧目名称'].isin(overlap_dramas)]

    # 按剧目和类型汇总
    drama_summary = df_overlap.groupby(['剧目名称', '账号类型']).agg({
        '视频播放量': 'sum',
        '剧集播放量': 'sum',
        '广告收益': 'sum'
    }).reset_index()
    drama_summary['万播收益'] = drama_summary['广告收益'] / drama_summary['剧集播放量'] * 10000
    drama_summary['万播收益'] = drama_summary['万播收益'].replace([np.inf, -np.inf], np.nan)

    return overlap_dramas, drama_summary


def create_comparison_chart(summary_by_type, output_dir):
    """创建原创/二创对比图表"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    colors = {'原创': '#3498db', '二创': '#e74c3c'}

    # 1. 剧集播放量
    ax1 = axes[0]
    x = range(len(summary_by_type))
    bars = ax1.bar(x, summary_by_type['剧集播放量'], color=[colors[t] for t in summary_by_type['账号类型']])
    ax1.set_xticks(x)
    ax1.set_xticklabels(summary_by_type['账号类型'], fontsize=12)
    ax1.set_title('剧集播放量对比', fontsize=14, fontweight='bold')
    ax1.set_ylabel('剧集播放量')
    ax1.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars, summary_by_type['剧集播放量']):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{val:,.0f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

    # 2. 广告收益
    ax2 = axes[1]
    bars = ax2.bar(x, summary_by_type['广告收益'], color=[colors[t] for t in summary_by_type['账号类型']])
    ax2.set_xticks(x)
    ax2.set_xticklabels(summary_by_type['账号类型'], fontsize=12)
    ax2.set_title('广告收益对比', fontsize=14, fontweight='bold')
    ax2.set_ylabel('广告收益（元）')
    ax2.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars, summary_by_type['广告收益']):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{val:.2f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

    # 3. 万播收益
    ax3 = axes[2]
    bars = ax3.bar(x, summary_by_type['万播收益'], color=[colors[t] for t in summary_by_type['账号类型']])
    ax3.set_xticks(x)
    ax3.set_xticklabels(summary_by_type['账号类型'], fontsize=12)
    ax3.set_title('万播收益对比', fontsize=14, fontweight='bold')
    ax3.set_ylabel('万播收益（元/万播）')
    ax3.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars, summary_by_type['万播收益']):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{val:.2f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.suptitle('原创账号 vs 二创账号 核心指标对比', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()

    output_path = os.path.join(output_dir, 'orig_vs_erc_combined.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'保存: {output_path}')
    return output_path


def create_account_chart(summary_by_account, output_dir):
    """创建四个账号对比图表"""
    fig, axes = plt.subplots(1, 3, figsize=(16, 6))

    colors = {'原创': '#3498db', '二创': '#e74c3c'}

    # 准备数据
    accounts = summary_by_account['视频号昵称'].tolist()
    types = summary_by_account['账号类型'].tolist()

    x = np.arange(len(accounts))
    width = 0.6

    # 1. 剧集播放量
    ax1 = axes[0]
    bars = ax1.bar(x, summary_by_account['剧集播放量'],
                   color=[colors[t] for t in types], width=width)
    ax1.set_xticks(x)
    ax1.set_xticklabels(accounts, rotation=20, ha='right', fontsize=10)
    ax1.set_title('剧集播放量', fontsize=13, fontweight='bold')
    ax1.set_ylabel('播放量')
    ax1.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars, summary_by_account['剧集播放量']):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{val/1000:.1f}k',
                ha='center', va='bottom', fontsize=9)

    # 2. 广告收益
    ax2 = axes[1]
    bars = ax2.bar(x, summary_by_account['广告收益'],
                   color=[colors[t] for t in types], width=width)
    ax2.set_xticks(x)
    ax2.set_xticklabels(accounts, rotation=20, ha='right', fontsize=10)
    ax2.set_title('广告收益', fontsize=13, fontweight='bold')
    ax2.set_ylabel('收益（元）')
    ax2.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars, summary_by_account['广告收益']):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{val:.1f}',
                ha='center', va='bottom', fontsize=9)

    # 3. 万播收益
    ax3 = axes[2]
    bars = ax3.bar(x, summary_by_account['万播收益'],
                   color=[colors[t] for t in types], width=width)
    ax3.set_xticks(x)
    ax3.set_xticklabels(accounts, rotation=20, ha='right', fontsize=10)
    ax3.set_title('万播收益', fontsize=13, fontweight='bold')
    ax3.set_ylabel('元/万播')
    ax3.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars, summary_by_account['万播收益']):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{val:.1f}',
                ha='center', va='bottom', fontsize=9)

    # 图例
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='#3498db', label='原创'),
                       Patch(facecolor='#e74c3c', label='二创')]
    fig.legend(handles=legend_elements, loc='upper right', fontsize=11)

    plt.suptitle('四个核心账号指标对比', fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()

    output_path = os.path.join(output_dir, 'four_accounts_compare.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'保存: {output_path}')
    return output_path


def create_drama_comparison_chart(drama_summary, output_dir, top_n=5):
    """创建剧目对比图表"""
    # 找万播收益最高的剧目
    yuan_df = drama_summary[drama_summary['账号类型'] == '原创'].copy()
    top_dramas = yuan_df.nlargest(top_n, '万播收益')['剧目名称'].tolist()

    df_top = drama_summary[drama_summary['剧目名称'].isin(top_dramas)]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    colors = {'原创': '#3498db', '二创': '#e74c3c'}

    # 准备数据
    dramas = []
    yuan_wan = []
    erc_wan = []
    yuan_rev = []
    erc_rev = []

    for drama in top_dramas:
        d_yuan = df_top[(df_top['剧目名称'] == drama) & (df_top['账号类型'] == '原创')]
        d_erc = df_top[(df_top['剧目名称'] == drama) & (df_top['账号类型'] == '二创')]

        if len(d_yuan) > 0:
            dramas.append(drama[:10] + '...' if len(drama) > 10 else drama)
            yuan_wan.append(d_yuan['万播收益'].values[0])
            yuan_rev.append(d_yuan['广告收益'].values[0])
            erc_wan.append(d_erc['万播收益'].sum() if len(d_erc) > 0 else 0)
            erc_rev.append(d_erc['广告收益'].sum() if len(d_erc) > 0 else 0)

    x = np.arange(len(dramas))
    width = 0.35

    # 万播收益对比
    ax1 = axes[0]
    ax1.bar(x - width/2, yuan_wan, width, label='原创', color=colors['原创'])
    ax1.bar(x + width/2, erc_wan, width, label='二创', color=colors['二创'])
    ax1.set_xticks(x)
    ax1.set_xticklabels(dramas, rotation=15, ha='right')
    ax1.set_ylabel('万播收益（元/万播）')
    ax1.set_title(f'Top{top_n}剧目 万播收益对比', fontsize=13, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')

    # 广告收益对比
    ax2 = axes[1]
    ax2.bar(x - width/2, yuan_rev, width, label='原创', color=colors['原创'])
    ax2.bar(x + width/2, erc_rev, width, label='二创', color=colors['二创'])
    ax2.set_xticks(x)
    ax2.set_xticklabels(dramas, rotation=15, ha='right')
    ax2.set_ylabel('广告收益（元）')
    ax2.set_title(f'Top{top_n}剧目 广告收益对比', fontsize=13, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    output_path = os.path.join(output_dir, 'drama_orig_vs_erc.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'保存: {output_path}')
    return output_path


if __name__ == "__main__":
    print("=" * 60)
    print("原创/二创账号合并对比分析")
    print("=" * 60)

    # 加载数据
    print("\n加载数据...")
    df = load_and_merge_data()
    print(f"合并数据: {len(df)} 条")

    # 处理核心账号
    df_core = process_core_accounts(df)
    print(f"核心账号数据: {len(df_core)} 条")

    print("\n核心账号数据分布:")
    print(df_core['视频号昵称'].value_counts())

    # 按账号类型分析
    print("\n" + "=" * 60)
    print("一、按原创/二创分组汇总")
    print("=" * 60)
    summary_by_type = analyze_by_account_type(df_core)
    print(summary_by_type.to_string(index=False))

    # 计算对比数据
    yuan_data = summary_by_type[summary_by_type['账号类型'] == '原创'].iloc[0]
    erc_data = summary_by_type[summary_by_type['账号类型'] == '二创'].iloc[0]

    print(f"\n【关键发现】")
    print(f"原创总播放量: {yuan_data['剧集播放量']:,.0f}")
    print(f"二创总播放量: {erc_data['剧集播放量']:,.0f} (原创的{erc_data['剧集播放量']/yuan_data['剧集播放量']*100:.1f}%)")
    print(f"原创总收益: {yuan_data['广告收益']:.2f}元")
    print(f"二创总收益: {erc_data['广告收益']:.2f}元 (原创的{erc_data['广告收益']/yuan_data['广告收益']*100:.1f}%)")
    print(f"原创万播收益: {yuan_data['万播收益']:.2f}元/万播")
    print(f"二创万播收益: {erc_data['万播收益']:.2f}元/万播 (原创的{erc_data['万播收益']/yuan_data['万播收益']*100:.1f}%)")

    # 按单个账号分析
    print("\n" + "=" * 60)
    print("二、按单个账号汇总")
    print("=" * 60)
    summary_by_account = analyze_by_account(df_core)
    print(summary_by_account.to_string(index=False))

    # 剧目重叠分析
    print("\n" + "=" * 60)
    print("三、剧目重叠分析")
    print("=" * 60)
    overlap_dramas, drama_summary = analyze_drama_overlap(df_core)

    # 生成图表
    print("\n" + "=" * 60)
    print("生成图表")
    print("=" * 60)

    create_comparison_chart(summary_by_type, OUTPUT_DIR)
    create_account_chart(summary_by_account, OUTPUT_DIR)
    create_drama_comparison_chart(drama_summary, OUTPUT_DIR)

    # 保存汇总数据
    print("\n保存汇总数据...")

    # 合并汇总表
    final_summary = pd.concat([
        summary_by_type.assign(分组='账号类型'),
        summary_by_account[['视频号昵称', '账号类型', '剧集播放量', '广告收益', '万播收益']].assign(分组='单个账号').rename(columns={'视频号昵称': '名称'})
    ], ignore_index=True)

    output_csv = os.path.join(OUTPUT_DIR, 'orig_erc_combined_summary.csv')
    final_summary.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"保存: {output_csv}")

    print("\n" + "=" * 60)
    print("分析完成!")
    print("=" * 60)

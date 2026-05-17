# -*- coding: utf-8 -*-
"""
原创/二创账号对比分析
处理香蕉和南瓜两个账号的二创数据
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

# 原创账号定义
ORIGINAL_ACCOUNTS = {
    '香蕉': ['香蕉轻漫剧场'],
    '南瓜': ['南瓜动漫短剧场', '飞姐漫剧推荐']
}


def load_and_process_data(file_path, account_name):
    """加载并处理单个账号的数据"""
    df = pd.read_excel(file_path, sheet_name='原生剧集挂载数据明细')

    # 添加账号标识
    df['账号'] = account_name

    # 判断原创/二创
    original_list = ORIGINAL_ACCOUNTS.get(account_name, [])
    df['账号类型'] = df['视频号昵称'].apply(lambda x: '原创' if x in original_list else '二创')

    # 计算万播收益
    df['万播收益'] = df['广告收益'] / df['剧集播放量'] * 10000
    df['万播收益'] = df['万播收益'].replace([np.inf, -np.inf], np.nan)

    return df


def analyze_erchuang(df, account_name):
    """
    分析单个账号的原创/二创数据
    """
    print(f"\n{'='*60}")
    print(f"分析账号: {account_name}")
    print(f"{'='*60}")

    # 1. 按账号类型汇总
    summary_by_type = df.groupby('账号类型').agg({
        '视频播放量': 'sum',
        '剧集播放量': 'sum',
        '广告收益': 'sum'
    }).reset_index()
    summary_by_type['万播收益'] = summary_by_type['广告收益'] / summary_by_type['剧集播放量'] * 10000

    print("\n【按账号类型汇总】")
    print(summary_by_type.to_string(index=False))

    # 2. 找出有二创参与的剧目
    dramas_with_erchuang = df[df['账号类型'] == '二创']['剧目名称'].unique()
    print(f"\n【有二创参与的剧目数】: {len(dramas_with_erchuang)}")

    # 3. 筛选这些剧目的所有数据
    df_erchuang_dramas = df[df['剧目名称'].isin(dramas_with_erchuang)]

    # 4. 按剧目和账号类型汇总
    drama_compare = df_erchuang_dramas.groupby(['剧目名称', '账号类型']).agg({
        '视频播放量': 'sum',
        '剧集播放量': 'sum',
        '广告收益': 'sum'
    }).reset_index()
    drama_compare['万播收益'] = drama_compare['广告收益'] / drama_compare['剧集播放量'] * 10000
    drama_compare['万播收益'] = drama_compare['万播收益'].replace([np.inf, -np.inf], np.nan)

    # 5. 找出同时有原创和二创的剧目
    drama_types = drama_compare.groupby('剧目名称')['账号类型'].apply(set).reset_index()
    both_types = drama_types[drama_types['账号类型'].apply(lambda x: '原创' in x and '二创' in x)]
    both_drama_names = both_types['剧目名称'].tolist()

    print(f"【同时有原创和二创的剧目数】: {len(both_drama_names)}")

    # 6. 对比表格
    if both_drama_names:
        df_compare = drama_compare[drama_compare['剧目名称'].isin(both_drama_names)]
        print("\n【剧目对比数据】")
        print(df_compare.to_string(index=False))

        # 找万播收益最高的剧目
        yuan_dramas = df_compare[df_compare['账号类型'] == '原创'].copy()
        erc_dramas = df_compare[df_compare['账号类型'] == '二创'].copy()

        # 合并对比
        compare_pivot = df_compare.pivot_table(
            index='剧目名称',
            columns='账号类型',
            values=['剧集播放量', '广告收益', '万播收益'],
            aggfunc='sum'
        ).reset_index()

        print("\n【对比透视表】")
        print(compare_pivot.to_string())

    return {
        'summary_by_type': summary_by_type,
        'drama_compare': drama_compare,
        'both_drama_names': both_drama_names,
        'df_compare': df_compare if both_drama_names else None
    }


def create_comparison_chart(results, account_name, output_dir):
    """创建对比图表"""
    summary = results['summary_by_type']

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    colors = {'原创': '#3498db', '二创': '#e74c3c'}

    # 1. 剧集播放量对比
    ax1 = axes[0]
    x = range(len(summary))
    bars = ax1.bar(x, summary['剧集播放量'], color=[colors[t] for t in summary['账号类型']])
    ax1.set_xticks(x)
    ax1.set_xticklabels(summary['账号类型'])
    ax1.set_title(f'{account_name} - 剧集播放量对比', fontsize=12, fontweight='bold')
    ax1.set_ylabel('剧集播放量')
    for bar, val in zip(bars, summary['剧集播放量']):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{val:,.0f}',
                ha='center', va='bottom', fontsize=10)

    # 2. 广告收益对比
    ax2 = axes[1]
    bars = ax2.bar(x, summary['广告收益'], color=[colors[t] for t in summary['账号类型']])
    ax2.set_xticks(x)
    ax2.set_xticklabels(summary['账号类型'])
    ax2.set_title(f'{account_name} - 广告收益对比', fontsize=12, fontweight='bold')
    ax2.set_ylabel('广告收益（元）')
    for bar, val in zip(bars, summary['广告收益']):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{val:.2f}',
                ha='center', va='bottom', fontsize=10)

    # 3. 万播收益对比
    ax3 = axes[2]
    bars = ax3.bar(x, summary['万播收益'], color=[colors[t] for t in summary['账号类型']])
    ax3.set_xticks(x)
    ax3.set_xticklabels(summary['账号类型'])
    ax3.set_title(f'{account_name} - 万播收益对比', fontsize=12, fontweight='bold')
    ax3.set_ylabel('万播收益（元/万播）')
    for bar, val in zip(bars, summary['万播收益']):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{val:.2f}',
                ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    output_path = os.path.join(output_dir, f'{account_name}_orig_vs_erc.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"保存: {output_path}")
    return output_path


def create_drama_top_chart(results, account_name, output_dir, top_n=3):
    """创建剧目对比图表（万播收益Top N）"""
    if results['df_compare'] is None or len(results['df_compare']) == 0:
        print(f"{account_name}: 无同时有原创和二创的剧目，跳过图表")
        return None

    df = results['df_compare']

    # 找原创账号中万播收益最高的剧目
    yuan_df = df[df['账号类型'] == '原创'].nlargest(top_n, '万播收益')
    top_dramas = yuan_df['剧目名称'].tolist()

    if not top_dramas:
        return None

    # 筛选这些剧目的数据
    df_top = df[df['剧目名称'].isin(top_dramas)]

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
    ax1.set_title(f'{account_name} - Top{top_n}剧目 万播收益对比', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')

    # 广告收益对比
    ax2 = axes[1]
    ax2.bar(x - width/2, yuan_rev, width, label='原创', color=colors['原创'])
    ax2.bar(x + width/2, erc_rev, width, label='二创', color=colors['二创'])
    ax2.set_xticks(x)
    ax2.set_xticklabels(dramas, rotation=15, ha='right')
    ax2.set_ylabel('广告收益（元）')
    ax2.set_title(f'{account_name} - Top{top_n}剧目 广告收益对比', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    output_path = os.path.join(output_dir, f'{account_name}_drama_compare.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"保存: {output_path}")
    return output_path


def create_combined_chart(banana_result, pumpkin_result, output_dir):
    """创建合并对比图表"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    colors = {'原创': '#3498db', '二创': '#e74c3c'}

    # 准备数据
    accounts = ['香蕉', '南瓜']
    metrics = ['剧集播放量', '广告收益', '万播收益']

    for i, metric in enumerate(metrics):
        ax = axes[i]

        x = np.arange(len(accounts))
        width = 0.35

        yuan_vals = []
        erc_vals = []

        for acc in accounts:
            if acc == '香蕉' and banana_result:
                summary = banana_result['summary_by_type']
            elif acc == '南瓜' and pumpkin_result:
                summary = pumpkin_result['summary_by_type']
            else:
                yuan_vals.append(0)
                erc_vals.append(0)
                continue

            yuan_val = summary[summary['账号类型'] == '原创'][metric].values
            erc_val = summary[summary['账号类型'] == '二创'][metric].values

            yuan_vals.append(yuan_val[0] if len(yuan_val) > 0 else 0)
            erc_vals.append(erc_val[0] if len(erc_val) > 0 else 0)

        bars1 = ax.bar(x - width/2, yuan_vals, width, label='原创', color=colors['原创'])
        bars2 = ax.bar(x + width/2, erc_vals, width, label='二创', color=colors['二创'])

        ax.set_xticks(x)
        ax.set_xticklabels(accounts)
        ax.set_ylabel(metric)
        ax.set_title(f'原创/二创 {metric}对比', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        # 添加数值标签
        for bar, val in zip(bars1, yuan_vals):
            if val > 0:
                label = f'{val:,.0f}' if metric != '广告收益' else f'{val:.2f}'
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), label,
                       ha='center', va='bottom', fontsize=9)
        for bar, val in zip(bars2, erc_vals):
            if val > 0:
                label = f'{val:,.0f}' if metric != '广告收益' else f'{val:.2f}'
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), label,
                       ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    output_path = os.path.join(output_dir, 'combined_orig_vs_erc.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"保存: {output_path}")
    return output_path


if __name__ == "__main__":
    print("=" * 60)
    print("原创/二创账号对比分析")
    print("=" * 60)

    # 文件路径
    banana_file = os.path.join(DATA_DIR, "4_香蕉", "xj_april_erchaung_yuanju.xlsx")
    pumpkin_file = os.path.join(DATA_DIR, "4_南瓜", "南瓜-视频号4月剧集数据统计_2026-05-11-5 copy.xlsx")

    # 加载数据
    print("\n加载数据...")
    df_banana = load_and_process_data(banana_file, '香蕉')
    df_pumpkin = load_and_process_data(pumpkin_file, '南瓜')

    print(f"香蕉数据: {len(df_banana)} 条")
    print(f"南瓜数据: {len(df_pumpkin)} 条")

    # 分析各账号
    banana_result = analyze_erchuang(df_banana, '香蕉')
    pumpkin_result = analyze_erchuang(df_pumpkin, '南瓜')

    # 生成图表
    print("\n" + "=" * 60)
    print("生成图表")
    print("=" * 60)

    create_comparison_chart(banana_result, '香蕉', OUTPUT_DIR)
    create_comparison_chart(pumpkin_result, '南瓜', OUTPUT_DIR)

    create_drama_top_chart(banana_result, '香蕉', OUTPUT_DIR)
    create_drama_top_chart(pumpkin_result, '南瓜', OUTPUT_DIR)

    create_combined_chart(banana_result, pumpkin_result, OUTPUT_DIR)

    # 输出汇总表格
    print("\n" + "=" * 60)
    print("汇总表格")
    print("=" * 60)

    print("\n【香蕉 原创/二创 汇总】")
    print(banana_result['summary_by_type'].to_string(index=False))

    print("\n【南瓜 原创/二创 汇总】")
    print(pumpkin_result['summary_by_type'].to_string(index=False))

    # 合并汇总
    combined_summary = pd.concat([
        banana_result['summary_by_type'].assign(账号='香蕉'),
        pumpkin_result['summary_by_type'].assign(账号='南瓜')
    ], ignore_index=True)

    print("\n【合并汇总】")
    print(combined_summary.to_string(index=False))

    # 保存汇总数据
    output_csv = os.path.join(OUTPUT_DIR, 'orig_erc_summary.csv')
    combined_summary.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\n汇总数据已保存: {output_csv}")

    print("\n" + "=" * 60)
    print("分析完成!")
    print("=" * 60)

# -*- coding: utf-8 -*-
"""
用户画像数据汇总与图表生成
整合香蕉和南瓜两个账号的用户年龄与性别数据
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

# 输出目录
OUTPUT_DIR = r"D:\Col_tasks\report_writer\assets\charts\合并"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ===================== 数据定义 =====================
# 香蕉用户数据
banana_gender = {
    '男性': 92,
    '女性': 17,
    '未知': 8
}

banana_age = {
    '17岁以下': 4,
    '18-24岁': 15,
    '25-29岁': 10,
    '30-39岁': 62,
    '40-49岁': 16,
    '50岁以上': 6,
    '未知': 4
}

# 南瓜用户数据（年龄档次对应：第一档=17岁以下, 第二档=18-24岁, ...）
pumpkin_gender = {
    '男性': 169,
    '女性': 643,
    '未知': 98
}

pumpkin_age = {
    '17岁以下': 83,
    '18-24岁': 50,
    '25-29岁': 94,
    '30-39岁': 342,
    '40-49岁': 213,
    '50岁以上': 101,
    '未知': 27
}

# ===================== 数据整理 =====================
def create_summary_tables():
    """创建汇总表格"""
    # 性别汇总
    gender_data = []
    for gender in ['男性', '女性', '未知']:
        gender_data.append({
            '性别': gender,
            '香蕉': banana_gender.get(gender, 0),
            '南瓜': pumpkin_gender.get(gender, 0)
        })

    df_gender = pd.DataFrame(gender_data)
    df_gender['合计'] = df_gender['香蕉'] + df_gender['南瓜']
    df_gender['香蕉占比'] = df_gender['香蕉'] / df_gender['香蕉'].sum() * 100
    df_gender['南瓜占比'] = df_gender['南瓜'] / df_gender['南瓜'].sum() * 100
    df_gender['合计占比'] = df_gender['合计'] / df_gender['合计'].sum() * 100

    # 年龄汇总
    age_order = ['17岁以下', '18-24岁', '25-29岁', '30-39岁', '40-49岁', '50岁以上', '未知']
    age_data = []
    for age in age_order:
        age_data.append({
            '年龄段': age,
            '香蕉': banana_age.get(age, 0),
            '南瓜': pumpkin_age.get(age, 0)
        })

    df_age = pd.DataFrame(age_data)
    df_age['合计'] = df_age['香蕉'] + df_age['南瓜']
    df_age['香蕉占比'] = df_age['香蕉'] / df_age['香蕉'].sum() * 100
    df_age['南瓜占比'] = df_age['南瓜'] / df_age['南瓜'].sum() * 100
    df_age['合计占比'] = df_age['合计'] / df_age['合计'].sum() * 100

    return df_gender, df_age


def create_gender_charts(df_gender):
    """生成性别分布饼图"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    colors = ['#3498db', '#e74c3c', '#95a5a6']  # 男性蓝, 女性红, 未知灰

    # 香蕉性别分布
    ax1 = axes[0]
    ax1.pie(df_gender['香蕉'], labels=df_gender['性别'], autopct='%1.1f%%',
            colors=colors, startangle=90)
    ax1.set_title('香蕉账号 - 用户性别分布', fontsize=13, fontweight='bold')

    # 南瓜性别分布
    ax2 = axes[1]
    ax2.pie(df_gender['南瓜'], labels=df_gender['性别'], autopct='%1.1f%%',
            colors=colors, startangle=90)
    ax2.set_title('南瓜账号 - 用户性别分布', fontsize=13, fontweight='bold')

    # 合并性别分布
    ax3 = axes[2]
    ax3.pie(df_gender['合计'], labels=df_gender['性别'], autopct='%1.1f%%',
            colors=colors, startangle=90)
    ax3.set_title('合并 - 用户性别分布', fontsize=13, fontweight='bold')

    plt.suptitle('用户性别分布对比', fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, 'user_gender_distribution.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'保存: {output_path}')
    return output_path


def create_age_charts(df_age):
    """生成年龄分布柱状图"""
    fig, axes = plt.subplots(1, 3, figsize=(16, 6))

    x = np.arange(len(df_age))
    width = 0.6
    colors = ['#2ecc71', '#3498db', '#9b59b6', '#e74c3c', '#f39c12', '#1abc9c', '#95a5a6']

    # 香蕉年龄分布
    ax1 = axes[0]
    bars = ax1.bar(x, df_age['香蕉'], color=colors, width=width)
    ax1.set_xticks(x)
    ax1.set_xticklabels(df_age['年龄段'], rotation=30, ha='right', fontsize=9)
    ax1.set_title('香蕉账号 - 用户年龄分布', fontsize=13, fontweight='bold')
    ax1.set_ylabel('人数')
    ax1.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars, df_age['香蕉']):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height(), str(val),
                ha='center', va='bottom', fontsize=9)

    # 南瓜年龄分布
    ax2 = axes[1]
    bars = ax2.bar(x, df_age['南瓜'], color=colors, width=width)
    ax2.set_xticks(x)
    ax2.set_xticklabels(df_age['年龄段'], rotation=30, ha='right', fontsize=9)
    ax2.set_title('南瓜账号 - 用户年龄分布', fontsize=13, fontweight='bold')
    ax2.set_ylabel('人数')
    ax2.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars, df_age['南瓜']):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(), str(val),
                ha='center', va='bottom', fontsize=9)

    # 合并年龄分布
    ax3 = axes[2]
    bars = ax3.bar(x, df_age['合计'], color=colors, width=width)
    ax3.set_xticks(x)
    ax3.set_xticklabels(df_age['年龄段'], rotation=30, ha='right', fontsize=9)
    ax3.set_title('合并 - 用户年龄分布', fontsize=13, fontweight='bold')
    ax3.set_ylabel('人数')
    ax3.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars, df_age['合计']):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height(), str(val),
                ha='center', va='bottom', fontsize=9)

    plt.suptitle('用户年龄分布对比', fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, 'user_age_distribution.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'保存: {output_path}')
    return output_path


def create_combined_comparison(df_gender, df_age):
    """生成合并对比图"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # 性别对比（分组柱状图）
    ax1 = axes[0]
    x = np.arange(len(df_gender))
    width = 0.35
    bars1 = ax1.bar(x - width/2, df_gender['香蕉'], width, label='香蕉', color='#FFD700')
    bars2 = ax1.bar(x + width/2, df_gender['南瓜'], width, label='南瓜', color='#FF8C00')
    ax1.set_xticks(x)
    ax1.set_xticklabels(df_gender['性别'])
    ax1.set_title('用户性别对比', fontsize=13, fontweight='bold')
    ax1.set_ylabel('人数')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars1, df_gender['香蕉']):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height(), str(val),
                ha='center', va='bottom', fontsize=10)
    for bar, val in zip(bars2, df_gender['南瓜']):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height(), str(val),
                ha='center', va='bottom', fontsize=10)

    # 年龄对比（分组柱状图）
    ax2 = axes[1]
    x = np.arange(len(df_age))
    width = 0.35
    bars1 = ax2.bar(x - width/2, df_age['香蕉'], width, label='香蕉', color='#FFD700')
    bars2 = ax2.bar(x + width/2, df_age['南瓜'], width, label='南瓜', color='#FF8C00')
    ax2.set_xticks(x)
    ax2.set_xticklabels(df_age['年龄段'], rotation=30, ha='right', fontsize=9)
    ax2.set_title('用户年龄对比', fontsize=13, fontweight='bold')
    ax2.set_ylabel('人数')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, 'user_demographics_comparison.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'保存: {output_path}')
    return output_path


if __name__ == "__main__":
    print("=" * 60)
    print("用户画像数据汇总与图表生成")
    print("=" * 60)

    # 创建汇总表
    df_gender, df_age = create_summary_tables()

    print("\n【性别分布汇总】")
    print(df_gender.to_string(index=False))

    print("\n【年龄分布汇总】")
    print(df_age.to_string(index=False))

    # 计算关键统计
    banana_total = df_gender['香蕉'].sum()
    pumpkin_total = df_gender['南瓜'].sum()
    combined_total = df_gender['合计'].sum()

    print("\n【用户总数】")
    print(f"香蕉: {banana_total} 人")
    print(f"南瓜: {pumpkin_total} 人")
    print(f"合计: {combined_total} 人")

    print("\n【关键发现】")
    # 性别特征
    banana_male_pct = df_gender[df_gender['性别'] == '男性']['香蕉占比'].values[0]
    pumpkin_female_pct = df_gender[df_gender['性别'] == '女性']['南瓜占比'].values[0]
    print(f"1. 香蕉账号: 男性主导 ({banana_male_pct:.1f}%)")
    print(f"2. 南瓜账号: 女性主导 ({pumpkin_female_pct:.1f}%)")

    # 年龄特征
    banana_peak_age = df_age.loc[df_age['香蕉'].idxmax(), '年龄段']
    pumpkin_peak_age = df_age.loc[df_age['南瓜'].idxmax(), '年龄段']
    print(f"3. 香蕉主力年龄段: {banana_peak_age}")
    print(f"4. 南瓜主力年龄段: {pumpkin_peak_age}")

    # 生成图表
    print("\n" + "=" * 60)
    print("生成图表")
    print("=" * 60)

    create_gender_charts(df_gender)
    create_age_charts(df_age)
    create_combined_comparison(df_gender, df_age)

    # 保存汇总数据
    output_csv = os.path.join(OUTPUT_DIR, 'user_demographics_summary.csv')
    with open(output_csv, 'w', encoding='utf-8-sig') as f:
        f.write("# 用户画像数据汇总\n\n")
        f.write("## 性别分布\n")
        df_gender.to_csv(f, index=False)
        f.write("\n## 年龄分布\n")
        df_age.to_csv(f, index=False)
    print(f'\n汇总数据保存: {output_csv}')

    print("\n" + "=" * 60)
    print("完成!")
    print("=" * 60)

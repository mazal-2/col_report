# -*- coding: utf-8 -*-
"""
用户画像综合仪表板
整合香蕉和南瓜两个账号的用户年龄与性别数据
生成四面板dashboard
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
banana_gender = {'男性': 92, '女性': 17, '未知': 8}
banana_age = {'17岁以下': 4, '18-24岁': 15, '25-29岁': 10, '30-39岁': 62, '40-49岁': 16, '50岁以上': 6, '未知': 4}

# 南瓜用户数据
pumpkin_gender = {'男性': 169, '女性': 643, '未知': 98}
pumpkin_age = {'17岁以下': 83, '18-24岁': 50, '25-29岁': 94, '30-39岁': 342, '40-49岁': 213, '50岁以上': 101, '未知': 27}


def create_demographics_dashboard():
    """创建用户画像综合仪表板"""
    # 准备数据
    gender_order = ['男性', '女性', '未知']
    age_order = ['17岁以下', '18-24岁', '25-29岁', '30-39岁', '40-49岁', '50岁以上', '未知']

    # 性别数据
    banana_g = [banana_gender.get(g, 0) for g in gender_order]
    pumpkin_g = [pumpkin_gender.get(g, 0) for g in gender_order]
    total_g = [b + p for b, p in zip(banana_g, pumpkin_g)]

    # 年龄数据
    banana_a = [banana_age.get(a, 0) for a in age_order]
    pumpkin_a = [pumpkin_age.get(a, 0) for a in age_order]
    total_a = [b + p for b, p in zip(banana_a, pumpkin_a)]

    # 总人数
    banana_total = sum(banana_g)
    pumpkin_total = sum(pumpkin_g)
    combined_total = sum(total_g)

    # 创建图表
    fig = plt.figure(figsize=(16, 12))

    # ========== 左上：性别分布饼图 ==========
    ax1 = fig.add_subplot(2, 2, 1)
    colors_gender = ['#3498db', '#e74c3c', '#95a5a6']

    # 绘制三个饼图（嵌套）
    sizes = [total_g, pumpkin_g, banana_g]
    labels_list = [gender_order, gender_order, gender_order]
    titles = ['合并', '南瓜', '香蕉']
    positions = [(0, 0), (0.35, 0), (-0.35, 0)]

    # 简化：绘制合并饼图
    wedges, texts, autotexts = ax1.pie(total_g, labels=gender_order, autopct='%1.1f%%',
                                        colors=colors_gender, startangle=90,
                                        explode=(0.02, 0.02, 0.02))
    ax1.set_title('用户性别分布（合并）', fontsize=13, fontweight='bold')

    # 添加数值标注
    centre_circle = plt.Circle((0, 0), 0.50, fc='white')
    ax1.add_artist(centre_circle)
    ax1.text(0, 0, f'{combined_total}人', ha='center', va='center', fontsize=14, fontweight='bold')

    # ========== 右上：年龄分布柱状图 ==========
    ax2 = fig.add_subplot(2, 2, 2)
    x = np.arange(len(age_order))
    width = 0.35

    bars1 = ax2.bar(x - width/2, banana_a, width, label='香蕉', color='#FFD700', edgecolor='#DAA520')
    bars2 = ax2.bar(x + width/2, pumpkin_a, width, label='南瓜', color='#FF8C00', edgecolor='#CD6600')

    ax2.set_xticks(x)
    ax2.set_xticklabels(age_order, rotation=25, ha='right', fontsize=9)
    ax2.set_title('用户年龄分布对比', fontsize=13, fontweight='bold')
    ax2.set_ylabel('人数')
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3, axis='y')

    # 添加数值标签
    for bar, val in zip(bars1, banana_a):
        if val > 0:
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3, str(val),
                    ha='center', va='bottom', fontsize=8)
    for bar, val in zip(bars2, pumpkin_a):
        if val > 0:
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3, str(val),
                    ha='center', va='bottom', fontsize=8)

    # ========== 左下：性别对比分组柱状图 ==========
    ax3 = fig.add_subplot(2, 2, 3)
    x = np.arange(len(gender_order))
    width = 0.35

    bars1 = ax3.bar(x - width/2, banana_g, width, label='香蕉', color='#FFD700', edgecolor='#DAA520')
    bars2 = ax3.bar(x + width/2, pumpkin_g, width, label='南瓜', color='#FF8C00', edgecolor='#CD6600')

    ax3.set_xticks(x)
    ax3.set_xticklabels(gender_order)
    ax3.set_title('用户性别对比', fontsize=13, fontweight='bold')
    ax3.set_ylabel('人数')
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')

    # 添加数值标签和占比
    for i, (bar, val) in enumerate(zip(bars1, banana_g)):
        pct = val / banana_total * 100 if banana_total > 0 else 0
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, f'{val}\n({pct:.1f}%)',
                ha='center', va='bottom', fontsize=9)
    for i, (bar, val) in enumerate(zip(bars2, pumpkin_g)):
        pct = val / pumpkin_total * 100 if pumpkin_total > 0 else 0
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, f'{val}\n({pct:.1f}%)',
                ha='center', va='bottom', fontsize=9)

    # ========== 右下：汇总统计表 ==========
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.axis('off')

    # 计算关键指标
    banana_male_pct = banana_gender['男性'] / banana_total * 100
    pumpkin_female_pct = pumpkin_gender['女性'] / pumpkin_total * 100
    banana_peak_age = age_order[banana_a.index(max(banana_a))]
    pumpkin_peak_age = age_order[pumpkin_a.index(max(pumpkin_a))]

    # 创建汇总表格
    table_data = [
        ['指标', '香蕉', '南瓜', '合并'],
        ['用户总数', f'{banana_total}人', f'{pumpkin_total}人', f'{combined_total}人'],
        ['男性占比', f'{banana_male_pct:.1f}%', f'{pumpkin_gender["男性"]/pumpkin_total*100:.1f}%', f'{sum([banana_gender["男性"],pumpkin_gender["男性"]])/combined_total*100:.1f}%'],
        ['女性占比', f'{banana_gender["女性"]/banana_total*100:.1f}%', f'{pumpkin_female_pct:.1f}%', f'{sum([banana_gender["女性"],pumpkin_gender["女性"]])/combined_total*100:.1f}%'],
        ['主力年龄段', banana_peak_age, pumpkin_peak_age, '30-39岁'],
        ['30-39岁占比', f'{banana_a[3]/banana_total*100:.1f}%', f'{pumpkin_a[3]/pumpkin_total*100:.1f}%', f'{total_a[3]/combined_total*100:.1f}%'],
        ['性别特征', '男性主导', '女性主导', '女性主导'],
    ]

    table = ax4.table(cellText=table_data, loc='center', cellLoc='center',
                      colWidths=[0.25, 0.2, 0.2, 0.2])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.3, 2.0)

    # 设置表头样式
    for i in range(4):
        table[(0, i)].set_facecolor('#9b59b6')
        table[(0, i)].set_text_props(color='white', fontweight='bold')

    # 设置首列样式
    for i in range(1, len(table_data)):
        table[(i, 0)].set_facecolor('#f8f9fa')
        table[(i, 0)].set_text_props(fontweight='bold')

    ax4.set_title('用户画像汇总统计', fontsize=13, fontweight='bold', y=0.95)

    plt.suptitle('用户画像综合分析 Dashboard', fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, 'user_demographics_dashboard.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'保存: {output_path}')
    return output_path


def create_gender_pie_dashboard():
    """创建性别分布三联饼图"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    colors = ['#3498db', '#e74c3c', '#95a5a6']
    gender_order = ['男性', '女性', '未知']

    # 香蕉
    ax1 = axes[0]
    vals = [banana_gender[g] for g in gender_order]
    total = sum(vals)
    wedges, texts, autotexts = ax1.pie(vals, labels=gender_order, autopct='%1.1f%%',
                                        colors=colors, startangle=90)
    ax1.set_title(f'香蕉 ({total}人)', fontsize=13, fontweight='bold')

    # 南瓜
    ax2 = axes[1]
    vals = [pumpkin_gender[g] for g in gender_order]
    total = sum(vals)
    ax2.pie(vals, labels=gender_order, autopct='%1.1f%%', colors=colors, startangle=90)
    ax2.set_title(f'南瓜 ({total}人)', fontsize=13, fontweight='bold')

    # 合并
    ax3 = axes[2]
    vals = [banana_gender[g] + pumpkin_gender[g] for g in gender_order]
    total = sum(vals)
    ax3.pie(vals, labels=gender_order, autopct='%1.1f%%', colors=colors, startangle=90)
    ax3.set_title(f'合并 ({total}人)', fontsize=13, fontweight='bold')

    plt.suptitle('用户性别分布对比', fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, 'user_gender_pie_dashboard.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'保存: {output_path}')
    return output_path


def create_age_bar_dashboard():
    """创建年龄分布三联柱状图"""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    age_order = ['17岁以下', '18-24岁', '25-29岁', '30-39岁', '40-49岁', '50岁以上', '未知']
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(age_order)))

    x = np.arange(len(age_order))
    width = 0.6

    # 香蕉
    ax1 = axes[0]
    vals = [banana_age[a] for a in age_order]
    bars = ax1.bar(x, vals, color=colors, width=width)
    ax1.set_xticks(x)
    ax1.set_xticklabels(age_order, rotation=30, ha='right', fontsize=8)
    ax1.set_title(f'香蕉 ({sum(vals)}人)', fontsize=13, fontweight='bold')
    ax1.set_ylabel('人数')
    ax1.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars, vals):
        if val > 0:
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, str(val),
                    ha='center', va='bottom', fontsize=8)

    # 南瓜
    ax2 = axes[1]
    vals = [pumpkin_age[a] for a in age_order]
    bars = ax2.bar(x, vals, color=colors, width=width)
    ax2.set_xticks(x)
    ax2.set_xticklabels(age_order, rotation=30, ha='right', fontsize=8)
    ax2.set_title(f'南瓜 ({sum(vals)}人)', fontsize=13, fontweight='bold')
    ax2.set_ylabel('人数')
    ax2.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars, vals):
        if val > 0:
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3, str(val),
                    ha='center', va='bottom', fontsize=8)

    # 合并
    ax3 = axes[2]
    vals = [banana_age[a] + pumpkin_age[a] for a in age_order]
    bars = ax3.bar(x, vals, color=colors, width=width)
    ax3.set_xticks(x)
    ax3.set_xticklabels(age_order, rotation=30, ha='right', fontsize=8)
    ax3.set_title(f'合并 ({sum(vals)}人)', fontsize=13, fontweight='bold')
    ax3.set_ylabel('人数')
    ax3.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars, vals):
        if val > 0:
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3, str(val),
                    ha='center', va='bottom', fontsize=8)

    plt.suptitle('用户年龄分布对比', fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, 'user_age_bar_dashboard.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'保存: {output_path}')
    return output_path


if __name__ == "__main__":
    print("=" * 60)
    print("用户画像综合仪表板生成")
    print("=" * 60)

    # 计算基本统计
    banana_total = sum(banana_gender.values())
    pumpkin_total = sum(pumpkin_gender.values())
    combined_total = banana_total + pumpkin_total

    print(f"\n用户总数:")
    print(f"  香蕉: {banana_total} 人")
    print(f"  南瓜: {pumpkin_total} 人")
    print(f"  合并: {combined_total} 人")

    print(f"\n性别特征:")
    print(f"  香蕉: 男性 {banana_gender['男性']/banana_total*100:.1f}% (主导)")
    print(f"  南瓜: 女性 {pumpkin_gender['女性']/pumpkin_total*100:.1f}% (主导)")

    print("\n生成图表...")
    create_demographics_dashboard()
    create_gender_pie_dashboard()
    create_age_bar_dashboard()

    print("\n" + "=" * 60)
    print("完成!")
    print("=" * 60)

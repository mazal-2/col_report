# -*- coding: utf-8 -*-
"""
合并香蕉和南瓜的4月数据
- 统一广告收益单位为"元"
- 添加账号标识字段
"""
import pandas as pd
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

# ===================== 路径配置 =====================
BANANA_PATH = r"D:\Col_tasks\report_writer\data\515_shipinhao\4_香蕉\april_daily_data.xlsx"
PUMPKIN_PATH = r"D:\Col_tasks\report_writer\data\515_shipinhao\4_南瓜\april_daily_data.xlsx"
OUTPUT_DIR = r"D:\Col_tasks\report_writer\data\515_shipinhao\merged"
OUTPUT_EXCEL = os.path.join(OUTPUT_DIR, "combined_april_data.xlsx")


def load_and_process_data(path, account_name, convert_revenue=False):
    """
    加载数据并添加账号标识
    convert_revenue: 是否需要将广告收益从分转换为元
    """
    xl = pd.ExcelFile(path)

    # 原始数据
    df_raw = xl.parse('原始数据')

    # 广告收益单位转换（分 -> 元）
    if convert_revenue:
        df_raw['广告收益'] = df_raw['广告收益'] / 100
        print(f"  [{account_name}] 广告收益已从分转换为元")

    # 添加账号标识
    df_raw['账号'] = account_name

    # 重新排列列顺序
    cols = ['账号'] + [c for c in df_raw.columns if c != '账号']
    df_raw = df_raw[cols]

    # 剧名汇总
    df_sum = xl.parse('剧名汇总')
    if convert_revenue:
        df_sum['广告收益'] = df_sum['广告收益'] / 100
    df_sum['账号'] = account_name
    cols = ['账号'] + [c for c in df_sum.columns if c != '账号']
    df_sum = df_sum[cols]

    # 日频数据
    df_read = xl.parse('阅读量(日频)')
    df_like = xl.parse('点赞数(日频)')
    df_revenue = xl.parse('广告收益(日频)')
    if convert_revenue:
        df_revenue.iloc[:, 1:] = df_revenue.iloc[:, 1:] / 100

    return df_raw, df_sum, df_read, df_like, df_revenue


if __name__ == "__main__":
    print("=" * 60)
    print("合并香蕉和南瓜的4月数据")
    print("=" * 60)

    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 加载香蕉数据（已经是元）
    print("\n加载香蕉数据...")
    b_raw, b_sum, b_read, b_like, b_rev = load_and_process_data(
        BANANA_PATH, "香蕉", convert_revenue=False
    )
    print(f"  原始数据: {b_raw.shape}, 剧目数: {b_sum.shape[0]}")

    # 加载南瓜数据（需要从分转换为元）
    print("\n加载南瓜数据...")
    p_raw, p_sum, p_read, p_like, p_rev = load_and_process_data(
        PUMPKIN_PATH, "南瓜", convert_revenue=True
    )
    print(f"  原始数据: {p_raw.shape}, 剧目数: {p_sum.shape[0]}")

    # ===================== 合并数据 =====================
    print("\n" + "=" * 60)
    print("合并数据")
    print("=" * 60)

    # 合并原始数据
    df_raw_combined = pd.concat([b_raw, p_raw], ignore_index=True)
    df_raw_combined = df_raw_combined.sort_values(['日期', '账号', '剧名'])
    print(f"\n合并后原始数据: {df_raw_combined.shape}")

    # 合并剧名汇总
    df_sum_combined = pd.concat([b_sum, p_sum], ignore_index=True)
    df_sum_combined = df_sum_combined.sort_values('广告收益', ascending=False)
    print(f"合并后剧名汇总: {df_sum_combined.shape}")

    # 日频数据需要添加账号标识后合并
    b_read_melt = b_read.melt(id_vars='剧名', var_name='日期', value_name='阅读量')
    b_read_melt['账号'] = '香蕉'
    p_read_melt = p_read.melt(id_vars='剧名', var_name='日期', value_name='阅读量')
    p_read_melt['账号'] = '南瓜'

    b_like_melt = b_like.melt(id_vars='剧名', var_name='日期', value_name='点赞数')
    b_like_melt['账号'] = '香蕉'
    p_like_melt = p_like.melt(id_vars='剧名', var_name='日期', value_name='点赞数')
    p_like_melt['账号'] = '南瓜'

    b_rev_melt = b_rev.melt(id_vars='剧名', var_name='日期', value_name='广告收益')
    b_rev_melt['账号'] = '香蕉'
    p_rev_melt = p_rev.melt(id_vars='剧名', var_name='日期', value_name='广告收益')
    p_rev_melt['账号'] = '南瓜'

    # 合并日频数据
    df_daily = b_read_melt.merge(b_like_melt, on=['剧名', '日期', '账号'])
    df_daily = df_daily.merge(b_rev_melt, on=['剧名', '日期', '账号'])

    p_daily = p_read_melt.merge(p_like_melt, on=['剧名', '日期', '账号'])
    p_daily = p_daily.merge(p_rev_melt, on=['剧名', '日期', '账号'])

    df_daily_combined = pd.concat([df_daily, p_daily], ignore_index=True)
    df_daily_combined = df_daily_combined.sort_values(['日期', '账号', '剧名'])
    print(f"合并后日频数据: {df_daily_combined.shape}")

    # ===================== 按账号汇总 =====================
    print("\n" + "=" * 60)
    print("按账号汇总")
    print("=" * 60)

    summary_by_account = df_sum_combined.groupby('账号').agg({
        '阅读量': 'sum',
        '点赞数': 'sum',
        '收藏数': 'sum',
        '广告收益': 'sum',
    }).reset_index()
    summary_by_account['万播收益'] = summary_by_account['广告收益'] / summary_by_account['阅读量'] * 10000
    summary_by_account = summary_by_account.round(2)

    print("\n按账号汇总:")
    print(summary_by_account.to_string(index=False))

    # ===================== 保存合并数据 =====================
    print("\n" + "=" * 60)
    print("保存合并数据")
    print("=" * 60)

    with pd.ExcelWriter(OUTPUT_EXCEL, engine="openpyxl") as writer:
        df_raw_combined.to_excel(writer, sheet_name="原始数据", index=False)
        df_sum_combined.to_excel(writer, sheet_name="剧名汇总", index=False)
        df_daily_combined.to_excel(writer, sheet_name="日频明细", index=False)
        summary_by_account.to_excel(writer, sheet_name="账号汇总", index=False)

        # 保留原有的透视表格式（分账号）
        b_read.to_excel(writer, sheet_name="香蕉_阅读量日频", index=False)
        b_like.to_excel(writer, sheet_name="香蕉_点赞数日频", index=False)
        b_rev.to_excel(writer, sheet_name="香蕉_广告收益日频", index=False)
        p_read.to_excel(writer, sheet_name="南瓜_阅读量日频", index=False)
        p_like.to_excel(writer, sheet_name="南瓜_点赞数日频", index=False)
        p_rev.to_excel(writer, sheet_name="南瓜_广告收益日频", index=False)

    print(f"\n已保存到: {OUTPUT_EXCEL}")

    # ===================== 显示最终结果 =====================
    print("\n" + "=" * 60)
    print("合并后数据概览")
    print("=" * 60)

    print(f"\n总剧目数: {df_sum_combined.shape[0]} 部")
    print(f"  - 香蕉: {b_sum.shape[0]} 部")
    print(f"  - 南瓜: {p_sum.shape[0]} 部")

    print(f"\n总阅读量: {df_sum_combined['阅读量'].sum():,}")
    print(f"总广告收益: {df_sum_combined['广告收益'].sum():.2f} 元")

    print("\n广告收益 Top 10:")
    print(df_sum_combined.head(10).to_string(index=False))

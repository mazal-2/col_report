# -*- coding: utf-8 -*-
"""
合并香蕉和南瓜的完整数据：
1. 日频数据（阅读量、点赞数、广告收益）- 已完成
2. 视频详情数据（播放、推荐、喜欢、评论、分享、关注）
3. 关注者增长数据（净增关注、新增关注、取消关注、关注者总数）
4. 剧集挂载数据明细
"""
import pandas as pd
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = r"D:\Col_tasks\report_writer\data\515_shipinhao\merged"

def merge_follower_growth():
    """合并关注者增长数据"""
    print("\n=== 合并关注者增长数据 ===")

    # 香蕉关注者增长数据
    b_follow = pd.read_csv(
        r"D:\Col_tasks\report_writer\data\515_shipinhao\4_香蕉\april_视频号关注者增长详情数据.csv",
        skiprows=2, header=None, names=['时间', '净增关注', '新增关注', '取消关注', '关注者总数']
    )
    # 跳过标题行
    b_follow = b_follow[b_follow['时间'] != '时间'].copy()
    b_follow['账号'] = '香蕉'
    print(f"  香蕉: {len(b_follow)} 天数据")

    # 南瓜关注者增长数据 - 检查是否存在
    pumpkin_follow_path = r"D:\Col_tasks\report_writer\data\515_shipinhao\4_南瓜\april_视频号关注者增长详情数据.csv"
    if os.path.exists(pumpkin_follow_path):
        p_follow = pd.read_csv(pumpkin_follow_path, skiprows=2, header=None,
                               names=['时间', '净增关注', '新增关注', '取消关注', '关注者总数'])
        p_follow = p_follow[p_follow['时间'] != '时间'].copy()
        p_follow['账号'] = '南瓜'
        print(f"  南瓜: {len(p_follow)} 天数据")
    else:
        print("  南瓜: 无关注者增长数据文件")
        p_follow = pd.DataFrame()

    # 合并
    if len(p_follow) > 0:
        df_combined = pd.concat([b_follow, p_follow], ignore_index=True)
    else:
        df_combined = b_follow

    # 转换数据类型
    for col in ['净增关注', '新增关注', '取消关注', '关注者总数']:
        df_combined[col] = pd.to_numeric(df_combined[col], errors='coerce')

    return df_combined


def merge_video_detail():
    """合并视频详情数据"""
    print("\n=== 合并视频详情数据 ===")

    # 香蕉视频详情数据
    b_video = pd.read_csv(
        r"D:\Col_tasks\report_writer\data\515_shipinhao\4_香蕉\april_视频号视频详情数据.csv",
        skiprows=2, header=None, names=['时间', '播放', '推荐', '喜欢', '评论', '分享', '关注']
    )
    b_video = b_video[b_video['时间'] != '时间'].copy()
    b_video['账号'] = '香蕉'
    print(f"  香蕉: {len(b_video)} 天数据")

    # 南瓜视频详情数据 - 检查是否存在
    pumpkin_video_path = r"D:\Col_tasks\report_writer\data\515_shipinhao\4_南瓜\april_视频号视频详情数据.csv"
    if os.path.exists(pumpkin_video_path):
        p_video = pd.read_csv(pumpkin_video_path, skiprows=2, header=None,
                              names=['时间', '播放', '推荐', '喜欢', '评论', '分享', '关注'])
        p_video = p_video[p_video['时间'] != '时间'].copy()
        p_video['账号'] = '南瓜'
        print(f"  南瓜: {len(p_video)} 天数据")
    else:
        print("  南瓜: 无视频详情数据文件")
        p_video = pd.DataFrame()

    # 合并
    if len(p_video) > 0:
        df_combined = pd.concat([b_video, p_video], ignore_index=True)
    else:
        df_combined = b_video

    # 转换数据类型
    for col in ['播放', '推荐', '喜欢', '评论', '分享', '关注']:
        df_combined[col] = pd.to_numeric(df_combined[col], errors='coerce')

    return df_combined


def merge_drama_mount_data():
    """合并剧集挂载数据明细"""
    print("\n=== 合并剧集挂载数据明细 ===")

    # 香蕉剧集挂载数据
    b_mount = pd.read_excel(
        r"D:\Col_tasks\report_writer\data\515_shipinhao\4_香蕉\april_收入剧集数据统计_2026-05-16.xlsx",
        sheet_name='原生剧集挂载数据明细'
    )
    b_mount['账号'] = '香蕉'
    # 广告收益从分转换为元
    if '广告收益' in b_mount.columns:
        b_mount['广告收益'] = b_mount['广告收益'] / 100
    print(f"  香蕉: {len(b_mount)} 条记录")

    # 南瓜剧集挂载数据
    p_mount = pd.read_excel(
        r"D:\Col_tasks\report_writer\data\515_shipinhao\4_南瓜\南瓜-视频号4月剧集数据统计_2026-05-11-5 copy.xlsx",
        sheet_name='原生剧集挂载数据明细'
    )
    p_mount['账号'] = '南瓜'
    # 广告收益从分转换为元
    if '广告收益' in p_mount.columns:
        p_mount['广告收益'] = p_mount['广告收益'] / 100
    print(f"  南瓜: {len(p_mount)} 条记录")

    # 合并
    df_combined = pd.concat([b_mount, p_mount], ignore_index=True)

    return df_combined


if __name__ == "__main__":
    print("=" * 60)
    print("合并香蕉和南瓜的完整数据")
    print("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. 合并关注者增长数据
    df_follow = merge_follower_growth()
    print(f"\n关注者增长数据总计: {len(df_follow)} 条")
    print(df_follow.groupby('账号').agg({
        '净增关注': 'sum',
        '新增关注': 'sum',
        '取消关注': 'sum',
        '关注者总数': 'last'
    }).to_string())

    # 2. 合并视频详情数据
    df_video = merge_video_detail()
    print(f"\n视频详情数据总计: {len(df_video)} 条")
    print(df_video.groupby('账号').agg({
        '播放': 'sum',
        '推荐': 'sum',
        '喜欢': 'sum',
        '评论': 'sum',
        '分享': 'sum',
        '关注': 'sum'
    }).to_string())

    # 3. 合并剧集挂载数据
    df_mount = merge_drama_mount_data()
    print(f"\n剧集挂载数据总计: {len(df_mount)} 条")

    # 保存到Excel
    output_excel = os.path.join(OUTPUT_DIR, "combined_complete_data.xlsx")
    with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
        df_follow.to_excel(writer, sheet_name="关注者增长", index=False)
        df_video.to_excel(writer, sheet_name="视频详情", index=False)
        df_mount.to_excel(writer, sheet_name="剧集挂载数据", index=False)

    print(f"\n已保存到: {output_excel}")

    # 显示汇总统计
    print("\n" + "=" * 60)
    print("数据汇总")
    print("=" * 60)

    print("\n【关注者增长统计】")
    for acc in df_follow['账号'].unique():
        df_acc = df_follow[df_follow['账号'] == acc]
        print(f"  {acc}: 净增{df_acc['净增关注'].sum():.0f}人, 当前{df_acc['关注者总数'].iloc[-1]:.0f}人")

    print("\n【视频详情统计】")
    for acc in df_video['账号'].unique():
        df_acc = df_video[df_video['账号'] == acc]
        print(f"  {acc}: 播放{df_acc['播放'].sum():,.0f}次, 喜欢{df_acc['喜欢'].sum():.0f}次")

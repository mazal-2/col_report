# -*- coding: utf-8 -*-
"""
抓取香蕉账号的剧集日频数据
输出格式参考南瓜的 april_daily_data.xlsx
"""
import requests
import json
import time
import os
import pandas as pd
from datetime import datetime, timezone, timedelta

# ===================== 配置区 =====================
# 从 xj_data_cookie_payload.md 获取
COOKIE = "RK=JSWIhha/uV; ptcz=072d2e1d4e8354f6697295a99227571be7af8505cbd5f899333803e88c0b625c; yyb_muid=1FF1247268AA67DC20AE32F9698466B6; logTrackKey=9af950a492f143848ca287dc597fa2f3; pac_uid=0_ws4yMGH2EW5cZ; _qimei_uuid42=19b0c1521271008b6607aa306cc960daae8371fc62; _qimei_h38=19c530256607aa306cc960da0200000c419b0c; omgid=0_ws4yMGH2EW5cZ; _qimei_q32=6ed33478541ce656253a78ba9982d75a; _qimei_q36=7893a930e22957a997cfb47a300016a19a1a; qq_domain_video_guid_verify=ba860f6e4f3f3c8d; _qimei_i_3=77d266d1910b59d9c79ef662088c27e2a5eda4f7135250d0e0dd290c2297726e336661943c89e299df8a; pgv_pvid=5937006136; promotewebsessionid=BgAAWeQEzj8z7GYS4ir9fpaj6WkI6X1r5J2%2FGx4jugyL26z0Gg1Ayyljc7ur5aRWTy635aU3kjMe%2ByB057qO5dn8tcEgt1h1v2CEXvNRIDwf; _qpsvr_localtk=0.9278616718730706; pgv_info=ssid=s1020897847; _qimei_fingerprint=afbfd443185dc8c3591d9671e4a09c30; _qimei_i_2=64ef64859d53538ac894fe6559867ae5f0bfadf8150855d0b088795b2693206d6732369c6988b3de95b0; _qimei_i_1=2cd979839c0955d8c195fb365d8474b1a6eda4f741080a84b4db79582493206c616364913980b0dc8590a4d9; ptui_loginuin=3877417963; sessionid=BgAAgXT0sS3CscczSFOElfj%2FDjET%2BmlLg3jSXmai0aqGI5a8EhDLAOgo%2BZ8uDJAYB%2FVUn90cICbK8na2yOflsAG0mpmmAUbSHj%2BNLRb4q1Ga; wxuin=3981915199"

FINGER_PRINT_DEVICE_ID = "11257a117b56412b6ed9b9a8270fdbf0"
X_WECHAT_UIN = "845252188"
FINDER_ID = "v2_060000231003b20faec8c5e38818c3dcc802ee30b077c324fb175e911ac9c4045e7ee0105a42@finder"

# 时间范围：2026年4月
START_DT = datetime(2026, 4, 1, 0, 0, 0, tzinfo=timezone(timedelta(hours=8)))
END_DT = datetime(2026, 4, 30, 23, 59, 59, tzinfo=timezone(timedelta(hours=8)))
START_TS = int(START_DT.timestamp())
DAYS = 30
PAGE_SIZE = 50

# API 配置
BASE_URL = "https://channels.weixin.qq.com"
PATH = "/micro/content/cgi-bin/mmfinderassistant-bin/component/get-finder-native-drama-statistics-list"
URL = f"{BASE_URL}{PATH}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0",
    "Cookie": COOKIE,
    "Content-Type": "application/json",
    "Origin": "https://channels.weixin.qq.com",
    "Referer": "https://channels.weixin.qq.com/micro/content/playlet/statistic",
    "X-WECHAT-UIN": X_WECHAT_UIN,
    "finger-print-device-id": FINGER_PRINT_DEVICE_ID,
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9,en-GB;q=0.8,zh-CN;q=0.7,zh-TW;q=0.6,zh;q=0.5",
    "sec-ch-ua": '"Chromium";v="148", "Microsoft Edge";v="148", "Not/A)Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
}

# 输出目录
OUTPUT_DIR = r"D:\Col_tasks\report_writer\data\515_shipinhao\4_香蕉"


def fetch_day(day_offset, page=1):
    """抓取某一天某一页的数据"""
    ts_start = START_TS + day_offset * 86400
    ts_end = ts_start + 86400

    payload = {
        "pageSize": PAGE_SIZE,
        "currentPage": page,
        "startTs": str(ts_start),
        "endTs": str(ts_end),
        "queryString": "",
        "pluginSessionId": None,
        "rawKeyBuff": None,
        "reqScene": 7,
        "scene": 7,
        "timestamp": str(int(time.time() * 1000)),
        "_log_finder_id": FINDER_ID,
        "_log_finder_uin": "",
    }

    resp = requests.post(URL, headers=HEADERS, json=payload, timeout=30)
    return resp.json()


def ts_to_date(ts):
    """时间戳转日期字符串"""
    dt = datetime.fromtimestamp(int(ts), tz=timezone(timedelta(hours=8)))
    return dt.strftime("%Y-%m-%d")


def fetch_all_pages(day_offset):
    """抓取某一天的所有页数据"""
    date_str = ts_to_date(START_TS + day_offset * 86400)
    all_items = []
    page = 1

    while True:
        try:
            data = fetch_day(day_offset, page)
            errCode = data.get("errCode")
            if errCode != 0:
                print(f"  [Page {page}] 请求失败: errCode={errCode}")
                break

            item_list = data.get("data", {}).get("list", [])
            if not item_list:
                break

            all_items.extend(item_list)

            # 检查是否还有更多页
            total = data.get("data", {}).get("total", 0)
            if total is None or len(all_items) >= total or len(item_list) < PAGE_SIZE:
                break

            page += 1
            time.sleep(1.5)
        except Exception as e:
            print(f"  [Page {page}] 异常: {e}")
            break

    return all_items


def safe_int(val, default=0):
    """安全转换为整数"""
    if val is None:
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def safe_float(val, default=0.0):
    """安全转换为浮点数"""
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def process_to_dataframe(all_data):
    """
    将原始数据转换为DataFrame，参考南瓜的数据结构
    广告收益单位从分转换为元
    """
    records = []
    for day_data in all_data:
        date = day_data["date"]
        for item in day_data["data"]:
            drama_info = item.get("dramaInfo", {})

            # 广告收益从分转换为元
            iaa_profit = safe_float(item.get("iaaProfit", 0)) / 100
            iap_profit = safe_float(item.get("iapProfit", 0)) / 100
            promotion_profit = safe_float(item.get("promotionProfit", 0)) / 100
            attach_profit = safe_float(item.get("attachProfit", 0)) / 100

            records.append({
                "日期": date,
                "剧名": drama_info.get("dramaName", ""),
                "剧ID": drama_info.get("dramaUuid", ""),
                "集数": safe_int(drama_info.get("mediaCount", 0)),
                "备案号": drama_info.get("registerNo", ""),
                "阅读量": safe_int(item.get("readCount", 0)),
                "点赞数": safe_int(item.get("likeCount", 0)),
                "收藏数": safe_int(item.get("favCount", 0)),
                "广告收益": iaa_profit,  # 已转换为元
                "付费收益": iap_profit,
                "推广收益": promotion_profit,
                "附加收益": attach_profit,
                "发帖数": safe_int(item.get("attachPostCount", 0)),
            })

    return pd.DataFrame(records)


def create_daily_sheets(df, date_range):
    """
    创建日频透视表（阅读量、点赞数、广告收益）
    类似南瓜的 april_daily_data.xlsx 结构
    """
    date_cols = [d.strftime("%Y-%m-%d") for d in date_range]

    # 阅读量日频
    df_read = df.pivot_table(
        index="剧名",
        columns="日期",
        values="阅读量",
        aggfunc="sum",
        fill_value=0
    ).reset_index()
    # 确保所有日期列都存在
    for col in date_cols:
        if col not in df_read.columns:
            df_read[col] = 0
    df_read = df_read[["剧名"] + date_cols]
    df_read = df_read.fillna(0).astype(int, errors="ignore")

    # 点赞数日频
    df_like = df.pivot_table(
        index="剧名",
        columns="日期",
        values="点赞数",
        aggfunc="sum",
        fill_value=0
    ).reset_index()
    for col in date_cols:
        if col not in df_like.columns:
            df_like[col] = 0
    df_like = df_like[["剧名"] + date_cols]
    df_like = df_like.fillna(0).astype(int, errors="ignore")

    # 广告收益日频（已转换为元）
    df_revenue = df.pivot_table(
        index="剧名",
        columns="日期",
        values="广告收益",
        aggfunc="sum",
        fill_value=0
    ).reset_index()
    for col in date_cols:
        if col not in df_revenue.columns:
            df_revenue[col] = 0.0
    df_revenue = df_revenue[["剧名"] + date_cols]
    df_revenue = df_revenue.fillna(0).round(2)

    # 剧名汇总
    df_summary = df.groupby("剧名").agg({
        "阅读量": "sum",
        "点赞数": "sum",
        "收藏数": "sum",
        "广告收益": "sum",
        "付费收益": "sum",
        "推广收益": "sum",
    }).reset_index()
    df_summary = df_summary.sort_values("广告收益", ascending=False)
    df_summary["广告收益"] = df_summary["广告收益"].round(2)

    return df_read, df_like, df_revenue, df_summary


if __name__ == "__main__":
    print(f"起始时间: {START_DT.strftime('%Y-%m-%d')}")
    print(f"结束时间: {END_DT.strftime('%Y-%m-%d')}")
    print(f"目标: 抓取 2026-04-01 至 2026-04-30 共 {DAYS} 天数据\n")

    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 抓取数据
    all_data = []
    for i in range(DAYS):
        try:
            date_str = ts_to_date(START_TS + i * 86400)
            print(f"[{date_str}] 开始抓取...")
            items = fetch_all_pages(i)
            print(f"[{date_str}] 完成, 共 {len(items)} 条数据")
            if items:
                all_data.append({"date": date_str, "data": items})
            time.sleep(1.5)
        except Exception as e:
            print(f"[Day {i}] 异常: {e}")
            time.sleep(2)

    print(f"\n=== 数据处理 ===")
    print(f"总共抓取 {len(all_data)} 天的数据")

    if not all_data:
        print("没有抓取到数据，退出")
        exit(1)

    # 转换为DataFrame
    df_raw = process_to_dataframe(all_data)
    print(f"原始数据: {df_raw.shape[0]} 条记录")

    # 创建日期范围
    date_range = pd.date_range("2026-04-01", "2026-04-30", freq="D")

    # 创建各Sheet
    df_read, df_like, df_revenue, df_summary = create_daily_sheets(df_raw, date_range)

    # 保存为Excel
    output_excel = os.path.join(OUTPUT_DIR, "april_daily_data.xlsx")
    with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
        df_raw.to_excel(writer, sheet_name="原始数据", index=False)
        df_read.to_excel(writer, sheet_name="阅读量(日频)", index=False)
        df_like.to_excel(writer, sheet_name="点赞数(日频)", index=False)
        df_revenue.to_excel(writer, sheet_name="广告收益(日频)", index=False)
        df_summary.to_excel(writer, sheet_name="剧名汇总", index=False)

    print(f"\n已保存到: {output_excel}")
    print(f"\n=== 剧名汇总 (Top 10) ===")
    print(df_summary.head(10).to_string(index=False))

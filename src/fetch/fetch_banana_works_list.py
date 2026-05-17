# -*- coding: utf-8 -*-
"""
抓取香蕉账号的剧目列表（包含上架时间）
"""
import requests
import json
import time
import os
import pandas as pd
from datetime import datetime, timezone, timedelta

# ===================== 配置区 =====================
# 上架日期 API 的 cookie（注意 sessionid 和 wxuin 与统计数据不同）
COOKIE = "RK=JSWIhha/uV; ptcz=072d2e1d4e8354f6697295a99227571be7af8505cbd5f899333803e88c0b625c; yyb_muid=1FF1247268AA67DC20AE32F9698466B6; logTrackKey=9af950a492f143848ca287dc597fa2f3; pac_uid=0_ws4yMGH2EW5cZ; _qimei_uuid42=19b0c1521271008b6607aa306cc960daae8371fc62; _qimei_h38=19c530256607aa306cc960da0200000c419b0c; omgid=0_ws4yMGH2EW5cZ; _qimei_q32=6ed33478541ce656253a78ba9982d75a; _qimei_q36=7893a930e22957a997cfb47a300016a19a1a; qq_domain_video_guid_verify=ba860f6e4f3f3c8d; _qimei_i_3=77d266d1910b59d9c79ef662088c27e2a5eda4f7135250d0e0dd290c2297726e336661943c89e299df8a; pgv_pvid=5937006136; promotewebsessionid=BgAAWeQEzj8z7GYS4ir9fpaj6WkI6X1r5J2%2FGx4jugyL26z0Gg1Ayyljc7ur5aRWTy635aU3kjMe%2ByB057qO5dn8tcEgt1h1v2CEXvNRIDwf; _qpsvr_localtk=0.9278616718730706; pgv_info=ssid=s1020897847; _qimei_fingerprint=afbfd443185dc8c3591d9671e4a09c30; _qimei_i_2=64ef64859d53538ac894fe6559867ae5f0bfadf8150855d0b088795b2693206d6732369c6988b3de95b0; _qimei_i_1=2cd979839c0955d8c195fb365d8474b1a6eda4f741080a84b4db79582493206c616364913980b0dc8590a4d9; ptui_loginuin=3877417963; sessionid=BgAA9cE8UqimiyYwoa8p%2F3HCwS%2B5d1kdeWa5sgbwgNBYjiJPcKcgjLAXv9OOu%2BpkTHALWjt1GCaH2eUlj%2Bb0NrB8VTC3K0laf%2BnW01V99nHN; wxuin=988138074"

FINGER_PRINT_DEVICE_ID = "11257a117b56412b6ed9b9a8270fdbf0"
X_WECHAT_UIN = "845252188"
FINDER_ID = "v2_060000231003b20faec8c5e38818c3dcc802ee30b077c324fb175e911ac9c4045e7ee0105a42@finder"

PAGE_SIZE = 20  # 每页条数

# API 配置 - 获取剧目列表（与 fetch_wechat_video.py 相同的接口）
BASE_URL = "https://channels.weixin.qq.com"
PATH = "/micro/content/cgi-bin/mmfinderassistant-bin/component/get-finder-native-drama-list"
QUERY_PARAMS = "_pageUrl=https:%2F%2Fchannels.weixin.qq.com%2Fmicro%2Fcontent%2Fplaylet"
URL = f"{BASE_URL}{PATH}?{QUERY_PARAMS}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0",
    "Cookie": COOKIE,
    "Content-Type": "application/json",
    "Origin": "https://channels.weixin.qq.com",
    "Referer": "https://channels.weixin.qq.com/micro/content/playlet",
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


def fetch_page(page):
    """抓取某一页的剧目列表"""
    payload = {
        "pageSize": PAGE_SIZE,
        "currentPage": page,
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
    if not ts or ts == "0":
        return "未发布"
    try:
        dt = datetime.fromtimestamp(int(ts), tz=timezone(timedelta(hours=8)))
        return dt.strftime("%Y-%m-%d")
    except:
        return str(ts)


if __name__ == "__main__":
    print("开始抓取香蕉账号的剧目列表...")
    print(f"API URL: {URL}")
    print()

    all_items = []
    page = 1
    total = None

    while True:
        try:
            print(f"[Page {page}] 请求中...")
            data = fetch_page(page)

            errCode = data.get("errCode") or data.get("data", {}).get("baseResp", {}).get("errcode")
            if errCode != 0:
                print(f"请求失败: errCode={errCode}")
                print(f"Response: {data}")
                break

            item_list = data.get("data", {}).get("list", [])
            if not item_list:
                print(f"[Page {page}] 无数据，停止")
                break

            # 获取总数
            if total is None:
                total = data.get("data", {}).get("totalCount", 0)
                print(f"总剧目数: {total}，预计 {(total + PAGE_SIZE - 1) // PAGE_SIZE} 页")

            all_items.extend(item_list)
            print(f"[Page {page}] 获取 {len(item_list)} 条，累计 {len(all_items)}/{total}")

            # 检查是否还有更多
            if len(all_items) >= total or len(item_list) < PAGE_SIZE:
                break

            page += 1
            time.sleep(1.5)

        except Exception as e:
            print(f"[Page {page}] 异常: {e}")
            break

    print(f"\n=== 数据处理 ===")
    print(f"总共抓取 {len(all_items)} 部剧目")

    if not all_items:
        print("没有抓取到数据，退出")
        exit(1)

    # 转换为 DataFrame
    records = []
    for item in all_items:
        drama_info = item.get("dramaInfo", item)  # 兼容两种数据结构
        publish_ts = drama_info.get("publishTime", "0")
        publish_date = ts_to_date(publish_ts)

        records.append({
            "剧名": drama_info.get("dramaName", ""),
            "剧ID": drama_info.get("dramaUuid", ""),
            "集数": drama_info.get("mediaCount", 0),
            "上架时间戳": publish_ts,
            "上架日期": publish_date,
            "备案号": drama_info.get("registerNo", ""),
            "变现模式": drama_info.get("monetizationMode", 0),
            "免费集数": drama_info.get("freeEpisodeNum", 0),
        })

    df = pd.DataFrame(records)

    # 按上架日期排序
    df = df.sort_values("上架日期", ascending=False)

    # 保存为 CSV
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_csv = os.path.join(OUTPUT_DIR, "works_list.csv")
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")

    # 同时保存为 JSON
    output_json = os.path.join(OUTPUT_DIR, "works_list.json")
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    print(f"\n已保存到:")
    print(f"  CSV: {output_csv}")
    print(f"  JSON: {output_json}")

    print(f"\n=== 剧目列表 ===")
    print(df.to_string(index=False))

    # 统计
    print(f"\n=== 统计 ===")
    print(f"总剧目数: {len(df)}")
    print(f"已发布剧目: {len(df[df['上架日期'] != '未发布'])}")
    print(f"未发布剧目: {len(df[df['上架日期'] == '未发布'])}")

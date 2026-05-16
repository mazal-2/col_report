import requests
import json
import time
import os
from datetime import datetime, timezone, timedelta

COOKIE = "qq_domain_video_guid_verify=336807f2ccf1dafe; pgv_pvid=1901955720; _qimei_uuid42=1a104123a2810014fe060034d7e2e8482b6680bd82; _qimei_i_3=64dd64d4935d52d29595ab330ed173e0a6e6f1f5475c0a80b78b7a0e7792213a663065943c89e2d5a5f1; _qimei_h38=8f95c0bbfe060034d7e2e8480200000e21a104; RK=hrJ+o3a1eU; ptcz=c1c12b4ea41efd7d7ef48169521d597bc49e014b3dc270db6bb4e0de08760cbe; yybsdk-webId=677a31300000019bb11f1de500002444; _qimei_q36=; _qimei_q32=; _qimei_fingerprint=15a65b06488b8359acaa9543da80e715; a_pk__04=8f95c0bbfe060034d7e2e8480200000e21a104; a_sk__07__15d45fa36b498329=015465636363616760666d61; _qimei_i_2=21b32cebd209; _qimei_i_1=42bf518ac3535588c1c5ac660e8475e0f7eda0a5150e01d7bc8b20582493206c6163629739d8e3dcd295c3d7; sessionid=BgAATGn6hQ7m18Swq4vV%2BMaYJC6EzStdGJN21gDOoejMy6Me04PRtmyAu3HLo%2FoPjTkmTQUjbHtqKW3TQVtcnuoc124QZ8JWTxUdpcCnmmNP; wxuin=2031825887; promotewebsessionid="

BASE_URL = "https://channels.weixin.qq.com"
PATH = "/micro/content/cgi-bin/mmfinderassistant-bin/component/get-finder-native-drama-statistics-list"
QUERY_PARAMS = "_aid=2caf8354-94b1-41aa-891b-d954f21b6b7f&_rid=6a06df96-9a8d7267&_pageUrl=https:%2F%2Fchannels.weixin.qq.com%2Fmicro%2Fcontent%2Fplaylet%2Fstatistic"

URL = f"{BASE_URL}{PATH}?{QUERY_PARAMS}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0",
    "Cookie": COOKIE,
    "Content-Type": "application/json",
    "Origin": "https://channels.weixin.qq.com",
    "Referer": "https://channels.weixin.qq.com/micro/content/playlet/statistic",
    "X-WECHAT-UIN": "845252188",
    "finger-print-device-id": "40bc8d112d786b2f8f7cbdd1cd0c971d",
}

# 2026-04-01 北京时间 00:00
START_DT = datetime(2026, 4, 1, 0, 0, 0, tzinfo=timezone(timedelta(hours=8)))
START_TS = int(START_DT.timestamp())
DAYS = 30
PAGE_SIZE = 50  # 每页条数

print(f"起始时间: {START_DT.strftime('%Y-%m-%d')} 时间戳: {START_TS}")
print(f"目标: 抓取 2026-04-01 至 2026-04-30 共 {DAYS} 天数据\n")

def fetch_day(day_offset, page=1):
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
        "_log_finder_id": "v2_060000231003b20faec8c5e28b10c6d3cf03ea3db077fe3542ff61028816e00a2ec888bbfe7d@finder",
        "_log_finder_uin": "",
    }

    resp = requests.post(URL, headers=HEADERS, json=payload, timeout=30)
    return resp.json()

def ts_to_date(ts):
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
                print(f"  [Page {page}] 请求失败: {data}")
                break

            item_list = data.get("data", {}).get("list", [])
            if not item_list:
                break

            all_items.extend(item_list)
            total = data.get("data", {}).get("total", 0)
            print(f"  [Page {page}] 获取 {len(item_list)} 条, 累计 {len(all_items)}/{total}")

            if len(all_items) >= total or len(item_list) < PAGE_SIZE:
                break

            page += 1
            time.sleep(1.5)
        except Exception as e:
            print(f"  [Page {page}] 异常: {e}")
            break

    return all_items

if __name__ == "__main__":
    results = []
    for i in range(DAYS):
        try:
            date_str = ts_to_date(START_TS + i * 86400)
            print(f"[{date_str}] 开始抓取...")
            items = fetch_all_pages(i)
            print(f"[{date_str}] 完成, 共 {len(items)} 条数据")
            results.append({"date": date_str, "data": items})
            time.sleep(1.5)
        except Exception as e:
            print(f"[Day {i}] 异常: {e}")
            time.sleep(2)

    output_path = os.path.join(os.path.dirname(__file__), "fetched_data.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n已保存到: {output_path}")
    print(f"总共抓取 {len(results)} 天的数据")
import requests
import json
import time
import os
from datetime import datetime, timezone, timedelta

COOKIE = "qq_domain_video_guid_verify=336807f2ccf1dafe; pgv_pvid=1901955720; _qimei_uuid42=1a104123a2810014fe060034d7e2e8482b6680bd82; _qimei_i_3=64dd64d4935d52d29595ab330ed173e0a6e6f1f5475c0a80b78b7a0e7792213a663065943c89e2d5a5f1; _qimei_h38=8f95c0bbfe060034d7e2e8480200000e21a104; RK=hrJ+o3a1eU; ptcz=c1c12b4ea41efd7d7ef48169521d597bc49e014b3dc270db6bb4e0de08760cbe; yybsdk-webId=677a31300000019bb11f1de500002444; _qimei_q36=; _qimei_q32=; _qimei_fingerprint=15a65b06488b8359acaa9543da80e715; a_pk__04=8f95c0bbfe060034d7e2e8480200000e21a104; a_sk__07__15d45fa36b498329=015465636363616760666d61; _qimei_i_2=21b32cebd209; _qimei_i_1=42bf518ac3535588c1c5ac660e8475e0f7eda0a5150e01d7bc8b20582493206c6163629739d8e3dcd295c3d7; sessionid=BgAATGn6hQ7m18Swq4vV%2BMaYJC6EzStdGJN21gDOoejMy6Me04PRtmyAu3HLo%2FoPjTkmTQUjbHtqKW3TQVtcnuoc124QZ8JWTxUdpcCnmmNP; compass_token=b_0000019e_2b027ee5_37502728_168aaa68_3991a72a; compass_rand=CAESIBxd4NSkIMpml8J0Aut5YoHdfhJeyaK93EjNf3+0TJ41; compass_login_type=1; compass_magic=8a775d9edff3f968f58c4933f48553374f2cd3e738d6e3d80251f421146e9bb9; compass_single_status=1; faas_logId=f5ce598a-b324-4e0a-a877-830879765028; promotewebsessionid=BgAAcpjZe%2FE%2BpAZSTG3V8fOMgg1cMcbvbFo%2B3hBtnBglCw9ndUccD5X5LRZEt8zAVhYuROEG8lRXCaJmpP%2FEY1CiyhUbEuFg2lkYCT%2BhLstU; wxuin=988138074"

BASE_URL = "https://channels.weixin.qq.com"
PATH = "/micro/content/cgi-bin/mmfinderassistant-bin/component/get-finder-native-drama-list"
QUERY = "_pageUrl=https:%2F%2Fchannels.weixin.qq.com%2Fmicro%2Fcontent%2Fplaylet"

URL = f"{BASE_URL}{PATH}?{QUERY}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0",
    "Cookie": COOKIE,
    "Content-Type": "application/json",
    "Origin": "https://channels.weixin.qq.com",
    "Referer": "https://channels.weixin.qq.com/micro/content/playlet/",
    "X-WECHAT-UIN": "845252188",
    "finger-print-device-id": "40bc8d112d786b2f8f7cbdd1cd0c971d",
}

def fetch_page(page):
    payload = {
        "pageSize": 50,
        "currentPage": page,
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
    if not ts or ts == "0":
        return "未发布"
    try:
        dt = datetime.fromtimestamp(int(ts), tz=timezone(timedelta(hours=8)))
        return dt.strftime("%Y-%m-%d")
    except:
        return ts

results = []
page = 1

while True:
    try:
        data = fetch_page(page)
        errCode = data.get("errCode") or data.get("data", {}).get("baseResp", {}).get("errcode")
        if errCode != 0:
            print(f"请求失败: {data}")
            break

        item_list = data.get("data", {}).get("list", [])
        if not item_list:
            print(f"第 {page} 页无数据，停止")
            break

        total = data.get("data", {}).get("totalCount", 0)
        if page == 1:
            print(f"总作品数: {total}，预计 {(total + 49) // 50} 页")

        for item in item_list:
            publish_time = item.get("publishTime", "0")
            results.append({
                "dramaName": item.get("dramaName", ""),
                "dramaUuid": item.get("dramaUuid", ""),
                "mediaCount": item.get("mediaCount", 0),
                "registerNo": item.get("registerNo", ""),
                "monetizationMode": item.get("monetizationMode", 0),
                "dramaStatus": item.get("dramaStatus", 0),
                "freeEpisodeNum": item.get("freeEpisodeNum", 0),
                "publishTime": publish_time,
                "publishDate": ts_to_date(publish_time),
                "dramaAgencyName": item.get("dramaAgencyName", ""),
            })

        print(f"第 {page} 页: 获取 {len(item_list)} 条")
        page += 1
        time.sleep(1.5)

        if len(results) >= total:
            break

    except Exception as e:
        print(f"第 {page} 页异常: {e}")
        break

# 保存
output_path = os.path.join(os.path.dirname(__file__), "works_list.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n完成，共 {len(results)} 部作品")
print(f"已保存到: {output_path}")
print("\n前10条:")
for item in results[:10]:
    print(f"  {item['publishDate']} | {item['mediaCount']}集 | {item['dramaName']}")
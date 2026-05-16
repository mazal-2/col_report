import json

with open("fetched_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 找一个有非零广告收益的记录
for day in data:
    for item in day["data"]:
        iaa = item.get("iaaProfit", "0")
        if iaa and iaa != "0":
            print(f"日期: {day['date']}")
            print(f"剧名: {item['dramaInfo']['dramaName']}")
            print(f"广告收益(iaaProfit): {iaa}")
            print(f"原始数据字段: {list(item.keys())}")
            print(json.dumps(item, ensure_ascii=False, indent=2))
            break
    else:
        continue
    break

# 统计所有有非零收益的记录
print("\n\n=== 统计非零广告收益 ===")
count = 0
for day in data:
    for item in day["data"]:
        iaa = item.get("iaaProfit", "0")
        if iaa and iaa != "0":
            count += 1
            if count <= 5:
                print(f"{day['date']} | {item['dramaInfo']['dramaName']} | iaaProfit={iaa}")

print(f"\n非零广告收益记录数: {count}")
print(f"总记录数: {sum(len(day['data']) for day in data)}")
import json
import csv
import os

with open("works_list.json", "r", encoding="utf-8") as f:
    data = json.load(f)

output_path = os.path.join(os.path.dirname(__file__), "works_list.csv")
with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["dramaName", "publishDate"])
    writer.writeheader()
    for item in data:
        writer.writerow({
            "dramaName": item["dramaName"],
            "publishDate": item["publishDate"],
        })

print(f"已导出: {output_path}")
print(f"共 {len(data)} 条记录")
print("\n预览:")
for item in data[:5]:
    print(f"  {item['publishDate']} | {item['dramaName']}")
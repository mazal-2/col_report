import json

with open("works_list.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total: {len(data)} works\n")
print("First 5 raw records:")
for item in data[:5]:
    print(json.dumps(item, ensure_ascii=False, indent=2))

print("\n\nAll unique publishTime values:")
times = set(item["publishTime"] for item in data)
print(times)
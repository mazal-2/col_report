import json
import pandas as pd

with open("fetched_data.json", "r", encoding="utf-8") as f:
    raw = json.load(f)

rows = []
for day_entry in raw:
    date = day_entry["date"]
    for item in day_entry["data"]:
        drama = item.get("dramaInfo", {})
        rows.append({
            "date": date,
            "name": drama.get("dramaName", ""),
            "iaa_raw": float(item.get("iaaProfit", 0)),
            "iaa_yuan": float(item.get("iaaProfit", 0)) / 100,
        })

df = pd.DataFrame(rows)
non_zero = df[df["iaa_yuan"] > 0].head(10)
print("Non-zero iaaProfit records:")
print(non_zero.to_string(index=False))
print(f"\nMax: {df['iaa_yuan'].max():.2f} yuan")
print(f"Total: {df['iaa_yuan'].sum():.2f} yuan")
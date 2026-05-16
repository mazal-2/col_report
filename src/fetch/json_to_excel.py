import json
import pandas as pd
import os

output_path = os.path.join(os.path.dirname(__file__), "fetched_data.json")
with open(output_path, "r", encoding="utf-8") as f:
    raw = json.load(f)

rows = []
for day_entry in raw:
    date = day_entry["date"]
    for item in day_entry["data"]:
        drama = item.get("dramaInfo", {})
        rows.append({
            "日期": date,
            "剧名": drama.get("dramaName", ""),
            "剧ID": drama.get("dramaUuid", ""),
            "集数": drama.get("mediaCount", 0),
            "备案号": drama.get("registerNo", ""),
            "阅读量": item.get("readCount", "0"),
            "点赞数": item.get("likeCount", "0"),
            "收藏数": item.get("favCount", "0"),
            "广告收益": item.get("iaaProfit", "0"),
            "付费收益": item.get("iapProfit", "0"),
            "推广收益": item.get("promotionProfit", "0"),
            "附加收益": item.get("attachProfit", "0"),
            "发帖数": item.get("attachPostCount", 0),
        })

df = pd.DataFrame(rows)

# 数值列清洗，收益字段从"分"转为"元"（除以100）
profit_cols = ["广告收益", "付费收益", "推广收益", "附加收益"]
for col in profit_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0) / 100

numeric_cols = ["阅读量", "点赞数", "收藏数", "发帖数"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# 透视表：按日期和剧名统计核心指标
pivot_read = df.pivot_table(index="剧名", columns="日期", values="阅读量", aggfunc="sum")
pivot_like = df.pivot_table(index="剧名", columns="日期", values="点赞数", aggfunc="sum")
pivot_iaa = df.pivot_table(index="剧名", columns="日期", values="广告收益", aggfunc="sum")

excel_path = os.path.join(os.path.dirname(__file__), "april_daily_data.xlsx")

with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
    # 原始数据
    df.to_excel(writer, sheet_name="原始数据", index=False)

    # 阅读量透视
    pivot_read.to_excel(writer, sheet_name="阅读量(日频)")
    pivot_like.to_excel(writer, sheet_name="点赞数(日频)")
    pivot_iaa.to_excel(writer, sheet_name="广告收益(日频)")

    # 汇总
    summary = df.groupby("剧名").agg({
        "阅读量": "sum",
        "点赞数": "sum",
        "收藏数": "sum",
        "广告收益": "sum",
        "付费收益": "sum",
        "推广收益": "sum",
    }).reset_index()
    summary.to_excel(writer, sheet_name="剧名汇总", index=False)

print(f"已导出: {excel_path}")
print(f"共 {len(df)} 条记录, {df['剧名'].nunique()} 部剧")
print(f"\n数据预览:")
print(df[["日期", "剧名", "阅读量", "点赞数", "广告收益"]].head(10).to_string(index=False))
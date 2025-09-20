import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timezone
# 搜尋出來的json檔
with open("../sentiment_analysis/articles.json", "r", encoding="utf-8") as f:
    data = json.load(f)

records = []
for r in data["records"]:
    row = {"timestamp": pd.to_datetime(r["timestamp"], utc=True)}
    row.update(r["emotions"])
    records.append(row)

df = pd.DataFrame(records)

# 6 個月範圍
end_time   = datetime.now(timezone.utc)
start_time = end_time - pd.DateOffset(months=6)

#「每兩週」分桶
time_bins = pd.date_range(start=start_time, end=end_time, freq="2W", tz="UTC")

# 分桶
df["time_bin"] = pd.cut(df["timestamp"], bins=time_bins)

# 每月平均
grouped = (
    df.groupby("time_bin", observed=False)[
        ["joy","sadness","anger","fear","surprise","disgust"]
    ]
    .mean()
)

# 取每個區間的左邊界（即該月開始日期）
x = pd.IntervalIndex(grouped.index).left

colors = {
    "joy":      "#FFB300",   # 橘
    "sadness":  "#1F77B4",   # 藍
    "anger":    "#D62728",   # 紅
    "fear":     "#9467BD",   # 紫
    "surprise": "#2CA02C",   # 綠
    "disgust":  "#8C564B",   # 咖啡
}

linestyles = ["-", "--", "-.", ":", (0,(3,1,1,1)), (0,(5,5))]
markers    = ["o","s","^","D","v","*"]

plt.style.use("seaborn-v0_8-darkgrid")
plt.figure(figsize=(12,6))

for i, emo in enumerate(colors):
    plt.plot(
        x, grouped[emo],
        color=colors[emo],
        linestyle=linestyles[i],
        marker=markers[i],
        linewidth=2,
        alpha=0.85,
        label=emo
    )

plt.title("情緒折線圖 (6 個月，每 2 週平均)")
plt.xlabel("日期")
plt.ylabel("平均分數")
plt.xticks(rotation=45)
plt.legend(ncol=2, frameon=False)  # 兩欄避免擁擠
plt.tight_layout()
plt.show()

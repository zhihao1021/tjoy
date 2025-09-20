import json
import pandas as pd
from pycirclize import Circos

# 假設你已經計算好 avg_scores
with open("fake_articles_db.json", "r", encoding="utf-8") as f:
    db = json.load(f)
records = db["records"]
emotions = ["joy", "sadness", "anger", "fear", "surprise", "disgust"]
avg_scores = {e: sum(r["emotions"][e] for r in records)/len(records)
              for e in emotions}

df = pd.DataFrame([avg_scores], index=["Average"])

# ✅ 直接在這裡調整六個情緒標籤的字型大小與粗細
circos = Circos.radar_chart(
    df,
    vmax=1.0,
    marker_size=6,
    cmap={"Average": "coral"},
    grid_interval_ratio=0.2,
    label_kws_handler=lambda _: dict(size=15, weight="bold")  # 這行很重要
)

fig = circos.plotfig()
fig.savefig("emotion_radar.png", dpi=150)
fig.show()

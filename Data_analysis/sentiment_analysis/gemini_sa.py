import json
import re
import google.generativeai as genai
import os

# 初始化 Gemini
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-pro")

# 搜尋出來的json檔
with open("articles.json", "r", encoding="utf-8") as f:
    data = json.load(f)

prompt_template = """你是一個專業的多面向情緒分析系統。
請依照以下規範分析輸入的文章內容，並輸出 JSON。

【輸入】  
{{ {text} }}

【任務】  
1. 針對下列六個情緒面向分別評分，每個分數介於 0.0 到 1.0 之間。
- joy
- sadness
- anger
- fear
- surprise
- disgust
2. 六個分數不必總和為 1。
3. 只輸出純 JSON，不要加 ```json 標籤。
"""

for record in data["records"]:
    # 合併文章與留言
    full_text = record["content"] + "\n" + "\n".join(c["text"] for c in record["comments"])
    prompt = prompt_template.format(text=full_text)

    # 呼叫 Gemini
    response = model.generate_content(prompt)

    # 安全取出文字
    raw = ""
    if response.candidates and response.candidates[0].content.parts:
        raw = response.candidates[0].content.parts[0].text or ""
    raw = raw.strip()

    if not raw:
        print(f"⚠️ ID {record['id']} 沒有回傳內容，略過")
        continue

    # 去除 ```json ... ``` 包裝
    clean = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.DOTALL)

    # 直接寫回原始資料結構
    record["emotions"] = json.loads(clean)

# 覆寫原始檔
with open("fake_articles_db.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ 已將分析結果直接寫入 fake_articles_db.json")

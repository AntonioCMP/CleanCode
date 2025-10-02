
import requests
import pandas as pd

data = requests.get(f'https://newsdata.io/api/1/latest?apikey=pub_95c015f2a639418ba2a0e404a9bc344d&q=ecuador&country=ec&category=business')
data = data.json()

if data["status"] != "error":
    df = pd.DataFrame(data["results"])
    df.drop(columns=[
        "keywords","content","image_url","video_url","source_icon",
        "language","country","sentiment","sentiment_stats","ai_tag",
        "ai_region","ai_org"
    ], inplace=True)
else:
    print("No funcionó bien")

filtered = df[["article_id", "title", "link", "pubDate"]]
print(filtered.head())

with open('DataBFN.csv', 'a',newline="",encoding='utf-8') as f:
    filtered.to_csv(f,mode="a",index=False,header=False)

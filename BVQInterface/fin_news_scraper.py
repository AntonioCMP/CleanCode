
import requests
import pandas as pd
from dotenv import load_dotenv
import os
from googletrans import Translator
import time

load_dotenv("tokens.env")
API_KEY = os.getenv("API_KEY")
SECRETS = os.getenv("SECRETS")
ROUTE_API = os.getenv("ROUTE_API")

translator = Translator()

def news_scrap():
    data = requests.get(f'https://newsdata.io/api/1/latest?apikey={API_KEY}&q=ecuador&country=ec&category=business')
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
        return pd.DataFrame()

    def translate_text(text):
        try:
            time.sleep(1)
            return translator.translate(text, src='es', dest='en').text
        except Exception as e:
            print("Error:", e)
            return ""

    df["title"] = df["title"].apply(translate_text)
    filtered = df[["article_id", "title", "link", "pubDate"]]

    enviar_a_api(filtered)
    print(filtered.head())

    return filtered

def enviar_a_api(filtered):
    header = {
        "Authorization": SECRETS
    }

    for i in range(filtered.shape[0]):
        final = {
            "main": {
                "articleid": filtered["article_id"].iloc[i],
                "title": filtered["title"].iloc[i],
                "link": filtered["link"].iloc[i],
                "pubDate": filtered["pubDate"].iloc[i],
            }
        }
        response = requests.post(ROUTE_API, json=final, headers=header)
        print(response.status_code)

if __name__ == "__main__":
    noticias = news_scrap()
    enviar_a_api(noticias)
    print(noticias.head())

from flask import Flask, render_template
from data_functions import *
import time
from dotenv import load_dotenv
from googletrans import Translator

news_cache = {
    "data": None,
    "last_fetched": 0,
    "sentiment_analysis": None
}
CACHE_DURATION_SECONDS = 1800 

load_dotenv("tokens.env")
API_KEY ="" #os.getenv("API_KEY")
SECRETS = ""#os.getenv("SECRETS")
ROUTE_API ="" #os.getenv("ROUTE_API")

translator = Translator()

def get_latest_news_and_sentiment():
    current_time = time.time()
    if news_cache["data"] is None or news_cache["data"].empty or (current_time - news_cache["last_fetched"]) > CACHE_DURATION_SECONDS:
        print("Caché de noticias expirado o vacío. Obteniendo nuevos datos...")

        df_news = "" #news_scrap()
        if not df_news == "":
            images, numy = analizar_sentimiento_noticias(df_news)
            
            news_cache["data"] = df_news
            news_cache["sentiment_analysis"] = (images, numy)
            news_cache["last_fetched"] = current_time
        else:
            print("No se pudieron obtener noticias. Se usará el caché antiguo si existe.")
    else:
        print("Usando noticias y sentimiento del caché.")

    return news_cache["sentiment_analysis"]

#Initialize flask and declare some important info
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
dtf= genesis()
estado=[["fire-flame.gif","🔥 Alza","alcista"],["water.gif","✌️ Neutro","neutral"],["snowflake.gif", "❄️️ Baja","bajista"]]
#ROUTES 

#Main route that contains all the info that will be in the landing page of the web
@app.route('/')
def home():
        name_array= dtf[-int(daily_len(dtf)):]["EMISOR"].to_list()
        utilities= [differential(dtf,i) for i in name_array]
        prize= dtf[-int(daily_len(dtf)):]["PRECIO"].to_list()
        liquid= dtf[-int(daily_len(dtf)):]["VALOR EFECTIVO"].to_list()
        secrets= [ i for i in range(len(name_array))]
        sentiment_result = get_latest_news_and_sentiment()
        if sentiment_result:
            images, numy = sentiment_result
        else:
            images, numy = ["water.gif", "✌️ Neutro", "neutral","neutral"], 0
        market= 0
        for i in utilities:
              market= market +i
        if market > 0:
              market=estado[0]
        else:
                if market==0:
                        market=estado[1]
                else:
                        market=estado[2]
                        
        return render_template("index.html",name_array=name_array,utilities=utilities,liquid=liquid,prize=prize,secrets=secrets,market=market,images=images,numy=numy)

@app.route("/infogeneral")
def infogeneral():
      return render_template("graphs.html")

@app.route("/plot_in_time/<action>/<business>")
def plot_time(action,business):
    business= business
    filtered_data = dtf[dtf["EMISOR"] == business]
    graph_json= grapher(action,filtered_data)

    return render_template("plots.html",graph_json=graph_json,business=business)

@app.route("/prediction/<business>")
def predict(business):

    graph_json= isaias(dtf,business)

    return render_template("predict.html",graph_json=graph_json,business=business)

@app.route("/LSTM_prediction/<business>")
def lstm_pred(business):
    
    graph_json= miqueas(dtf,business)

    return render_template("plots.html",graph_json=graph_json,business=business)


if __name__ == "__main__":
    app.run(debug=True)

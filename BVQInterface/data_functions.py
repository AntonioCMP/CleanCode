
import pandas as pd
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import json
from prophet import Prophet
import plotly.graph_objects as go
import datetime as dt
from datetime import timedelta
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from tensorflow.keras.models import load_model
import plotly.io as pio
import pickle
from dotenv import load_dotenv
from nltk.corpus import stopwords
from nltk.stem.porter import *
from nltk.tokenize import word_tokenize
import re
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import os

#To avoid the annoying warning related to that environ
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

day_today= str(dt.datetime.today())[:10]
try:
    model = load_model("SA_FinancialNews.h5")
    with open("tokenizer.pickle", "rb") as handle:
        tokenizer = pickle.load(handle)
    print("Modelos de sentimiento cargados correctamente.")
except Exception as e:
    print(f"Error al cargar los modelos de sentimiento: {e}")
    model = None
    tokenizer= None


#Initialize the dataframe and clean all the columns and rows that no have information
def genesis():
     #Processing data
    df= pd.read_excel("D:\\DocumentosI\\NGE\\NGE3.0+1.0\\The grid\\acciones.xls")
    data= pd.read_excel("D:\\DocumentosI\\NGE\\NGE3.0+1.0\\The grid\\acciones2025.xls")
    dmax= pd.read_excel("D:\\DocumentosI\\NGE\\NGE3.0+1.0\\The grid\\acciones180425.xlsx",sheet_name="2025")


    #Cleaning the data
    df.dropna(thresh=2,inplace=True)
    data.dropna(thresh=2,inplace=True)
    dmax.dropna(thresh=2,inplace=True)


    #Changing the headers of the dataframe

    df.columns= df.loc[7]
    df.drop(index=[7],inplace=True)
    df.dropna(axis=1,inplace=True)

    data.columns= data.loc[7]
    data.drop(index=[7],inplace=True)
    data.dropna(axis=1,inplace=True)

    dmax.columns= dmax.loc[7]
    dmax.drop(index=[7],inplace=True)
    dmax.dropna(axis=1,inplace=True)

    #Dropping useless data
    df.drop_duplicates(inplace=True)
    data.drop_duplicates(inplace=True)
    dmax.drop_duplicates(inplace=True)

    #Pasting three years of data
    dtf= pd.concat([df,data,dmax])


    #Fix some rows with date problems
    dtf.iloc[-188:-37, dtf.columns.get_loc("FECHA")] = dtf.iloc[-188:-37]["FECHA"].str.slice(0, 10)

    #Put all the data into the same format and drop nan values that could interfere with the program
    dtf["FECHA"] = pd.to_datetime(dtf["FECHA"], errors="coerce",format="%d/%m/%Y")
    dtf.dropna(inplace=True)

    return dtf

#Creates the main plot depending of which action the user choose
def grapher(action,filtered_data):
    #Creation of the plot

    fig= go.Figure()

    fig.add_trace(go.Scatter(
        x=filtered_data["FECHA"].to_list(),
        y=filtered_data[action].to_list(),
            mode='lines',
             
        ))
    
    fig.update_layout(
        title=f"Gráfico {action} 2023-2024-2025",
        xaxis_title='FECHA',
        yaxis_title='PRECIO',
    )

    graph_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    return graph_json

#Use prophet to predict the values of the business chosen, also makes a plot with the prophet prediction and the original values
def isaias(dtf,business):
    chosen= dtf[dtf["EMISOR"]== business][["FECHA","PRECIO"]]
    chosen.columns = ['ds', 'y'] 

    model = Prophet()
    model.fit(chosen)

    future = model.make_future_dataframe(periods=30)  
    forecast = model.predict(future)

    ds = forecast['ds'].tolist()
    yhat = forecast['yhat'].tolist()
    yhat_upper = forecast['yhat_upper'].tolist()
    yhat_lower = forecast['yhat_lower'].tolist()

    # Crear gráfico manualmente
    fig = go.Figure()

    # Datos reales
    fig.add_trace(go.Scatter(x=chosen['ds'].tolist(), 
                             y=chosen['y'].tolist(),
                             mode='markers', name='Datos reales', marker=dict(color='black', size=4)))

    # Predicción
    fig.add_trace(go.Scatter(x=ds, y=yhat, mode='lines', name='Predicción', line=dict(color='blue')))

    fig.add_trace(go.Scatter(x=ds, y=yhat_upper, mode='lines', name='Límite superior', line=dict(dash='dot', color='red')))
    fig.add_trace(go.Scatter(x=ds, y=yhat_lower, mode='lines', name='Límite inferior', line=dict(dash='dot', color='red')))

    # Ajustar layout
    fig.update_layout(title=f'Predicción para {business}',
                      xaxis_title='Fecha',
                      yaxis_title='Precio',
                      showlegend=True,
                      width=1400, height=600)

    # Serializar
    graph_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    return graph_json

#Returns the amount of business that are in the daily dataframe
def daily_len(dtf):
    try:
        daily= dtf[dtf["FECHA"] == day_today].shape[0]
        if daily == 0:
            daily=5
    except:
        daily= 5
    return daily


#Returns the difference between prizes in the last days depending the amount of data that is available in that business
def differential(dtf,business):

    dtf["ENTLIN"] = pd.to_datetime(dtf["FECHA"]).dt.date

    wheblue = dtf["EMISOR"] == business
    today = dtf["ENTLIN"] == dt.date.today()
    try:
        first = dtf[wheblue & today].iloc[-1]["PRECIO"]
    except IndexError:
        print("No hay datos para hoy")
        first = None

    second = None
    max_days_back = 50 
    for i in range(1, max_days_back + 1):
        target_date = dt.date.today() - dt.timedelta(days=i)
        mask = wheblue & (dtf["ENTLIN"] == target_date)
        if not dtf[mask].empty:
            second = dtf[mask].iloc[-1]["PRECIO"]
            break

    if first is None or second is None:
        print("No se pudo calcular la diferencia.")
        return 0
    else:
        first = float(str(first).replace(',', ''))
        second = float(str(second).replace(',', ''))
        return round(first - second, 2)

#Make a window and predict all the values based on the last one (t=t+1)
def predecir_futuro(modelo, datos,scaler, pasos=30):
    predicciones = []
    secuencia = datos[-pasos:].reshape(1, pasos, 1)

    for _ in range(pasos):
        pred = modelo.predict(secuencia, verbose=0)[0][0]
        predicciones.append(pred)
        
        nueva_secuencia = np.append(secuencia[0][1:], [[pred]], axis=0)
        secuencia = nueva_secuencia.reshape(1, pasos, 1)
        
    predicciones_desescaladas = scaler.inverse_transform(np.array(predicciones).reshape(-1, 1))
    return predicciones_desescaladas

#Clean the dataframe and make the rpediction based on the model that is chosen by the user
def miqueas(dtf,chosen):
    scaler=MinMaxScaler()
    dtf["PRECIO"]= pd.to_numeric(dtf["PRECIO"],errors="coerce")
    risky= dtf[dtf["EMISOR"] == chosen]
    risky.index= risky["FECHA"]
    risky= risky[["PRECIO"]]
    scaled_data = scaler.fit_transform(risky)
    model = load_model(f"D:\\DocumentosI\\NGE\\NGE3.0+1.0\\The grid\\{chosen}_LSTM_model.h5")
    prediction= predecir_futuro(model, scaled_data, pasos=30,scaler=scaler)
    hoy = dtf["FECHA"].max() + timedelta(days=1)
    fechas_pred = [hoy + timedelta(days=i) for i in range(len(prediction))]
    prediction= [round(float(i),2) for i in prediction]
    preds= pd.DataFrame({
    'FECHA': fechas_pred,
    'PRECIO': prediction,
    'TIPO': 'Predicción'
    })
    
    reals= dtf[dtf["EMISOR"] == chosen][["FECHA","PRECIO"]]
    reals["TIPO"]= "Original"
    real_and_pred= pd.concat([reals,preds])
    real_and_pred["FECHA"] = real_and_pred["FECHA"].astype(str)
    real_and_pred['PRECIO'] = real_and_pred['PRECIO'].astype(float)
    real_and_pred.dropna(subset=["PRECIO"], inplace=True)

    fig = go.Figure()

    #To make the plot work we MUST convert the dataframe columns to a list, because the json file not accept objects as pandas dataframes or numpy arrays
    for tipo in real_and_pred['TIPO'].unique():
        df_filtrado = real_and_pred[real_and_pred['TIPO'] == tipo]

        fig.add_trace(go.Scatter(
            x=df_filtrado['FECHA'].tolist(),
            y=df_filtrado['PRECIO'].tolist(),
            mode='lines',
            name=tipo  
        ))

    #Title and labels
    fig.update_layout(
        title='Precio original vs predicción',
        xaxis_title='FECHA',
        yaxis_title='PRECIO',
    )
 
    graph_json = pio.to_json(fig)
 
    return graph_json

#Convert the words to root form
def basicalizer(text):
    stop_words = set(stopwords.words("english"))
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    words = word_tokenize(text)
    words = [w for w in words if w not in stop_words]
    words = [PorterStemmer().stem(w) for w in words]
    return ' '.join(words)

#Load the model and evaluate which sentiment is predominant today
def analizar_sentimiento_noticias(df_noticias):
    if model is None or tokenizer is None:
        print("Modelos no disponibles, saltando análisis de sentimiento.")
        return ["water.gif", "✌️ Neutro", "neutral","neutral"], 0
    df_noticias["clean_text"] = df_noticias["title"].apply(basicalizer)
    seqs = tokenizer.texts_to_sequences(df_noticias["clean_text"])
    padded_seqs = pad_sequences(seqs, maxlen=50, padding='post')
    preds = model.predict(padded_seqs)
    df_noticias["pred_class"] = preds.argmax(axis=1)
    label_map = {0: "neutral", 1: "positive", 2: "negative"}
    df_noticias["sentiment"] = df_noticias["pred_class"].map(label_map)

    #Count sentiments
    counts = df_noticias["sentiment"].value_counts()
    pos = counts.get("positive", 0)
    neu = counts.get("neutral", 0)
    neg = counts.get("negative", 0)

    if pos > neg and pos > neu:
        return ["fire-flame.gif", "🔥 Alza", "alcista","positivo"],pos
    elif neg > pos and neg > neu:
        return ["snowflake.gif", "❄️ Baja", "bajista","negativo"],neg
    else:
        return ["water.gif", "✌️ Neutro", "neutral","neutral"],neu

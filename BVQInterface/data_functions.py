
import pandas as pd
from prophet import Prophet
from plotly.graph_objects import Scatter,Figure
from datetime import datetime,timedelta
from sklearn.preprocessing import MinMaxScaler
from numpy import append,array
from plotly.io import to_json
from pickle import load
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
from re import sub
from os import environ

#To avoid the annoying warning related to that environ
environ["TF_ENABLE_ONEDNN_OPTS"]="0"
environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences



#Initialize the dataframe and clean all the columns and rows that no have information
def genesis():
    """"Function that reads the ultimate version of the data and"""
    """Clean it converting to datetype objects the columns of the dataframe"""

    dtf= pd.read_csv("..\\Data\\AccionesFinal.csv",delimiter=",")
    dtf["FECHA"] = pd.to_datetime(dtf["FECHA"], errors="coerce",format="%Y-%m-%d")
    dtf["PRECIO"]=dtf["PRECIO"].map(lambda x: x.replace(",", "") if  "," in x else x)
    dtf["PRECIO"] = pd.to_numeric(dtf["PRECIO"])

    return dtf

#Creates the main plot depending of which action the user choose
def grapher(action,filtered_data):
    """Create an interactive plot of plotly with the action given"""
    """(PRECIO,NUMERO ACCIONES,VALOR NOMINAL) and the business given"""

    fig= Figure()

    fig.add_trace(Scatter(
        x=filtered_data["FECHA"].to_list(),
        y=filtered_data[action].to_list(),
            mode='lines',
             
        ))
    
    fig.update_layout(
        title=f"Gráfico {action} 2023-2024-2025",
        xaxis_title='FECHA',
        yaxis_title='PRECIO',
    )

    graph_json = to_json(fig)
    return graph_json

#Use prophet to predict the values of the business chosen, also makes a plot with the prophet prediction and the original values
def isaias(dtf,business):

    """Divide the DataFrame with only one business and with date and price"""
    """Create a Prophet object and train it with the data"""
    """Finally it creates an interactive plot with plotly with the predictions and real prices"""
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
    fig = Figure()

    # Datos reales
    fig.add_trace(Scatter(x=chosen['ds'].tolist(), 
                             y=chosen['y'].tolist(),
                             mode='markers', name='Datos reales', marker=dict(color='black', size=4)))

    # Predicción
    fig.add_trace(Scatter(x=ds, y=yhat, mode='lines', name='Predicción', line=dict(color='blue')))

    fig.add_trace(Scatter(x=ds, y=yhat_upper, mode='lines', name='Límite superior', line=dict(dash='dot', color='red')))
    fig.add_trace(Scatter(x=ds, y=yhat_lower, mode='lines', name='Límite inferior', line=dict(dash='dot', color='red')))

    # Ajustar layout
    fig.update_layout(title=f'Predicción para {business}',
                      xaxis_title='Fecha',
                      yaxis_title='Precio',
                      showlegend=True,
                      width=1400, height=600)

    # Serializar
    graph_json = to_json(fig)
    return graph_json

#Returns the amount of business that are in the daily dataframe
def daily_len(dtf):
    """Check the total business in the dataframe of today"""
    day_today= str(datetime.today())[:10]

    try:
        daily= dtf[dtf["FECHA"] == day_today].shape[0]
        if daily == 0:
            daily=5
    except:
        daily= 5
    return daily


#Returns the difference between prizes in the last days depending the amount of data that is available in that business
def differential(dtf,business):
    """Collect the price of previous days and depending"""
    """the situation use the last price that is different"""
    """to the today's prices"""

    chosen_business = dtf["EMISOR"] == business
    today = dtf["FECHA"] == dtf["FECHA"].max()
    nowaday= dtf["FECHA"].max()

    try:
        first = dtf[chosen_business & today].iloc[-1]["PRECIO"]
    except IndexError:
        print("No hay datos para hoy")
        first = None
        second = None

    max_days_back = 50 
    for i in range(1, max_days_back + 1):
        target_date = nowaday - timedelta(days=i)
        mask = chosen_business & (dtf["FECHA"] == target_date)
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
    """A simple window creator for the predictions of the LSTM NN"""
    """Basically, create a list that contains groups of 30 prices"""
    """being this predictions of the model and predictions of the predictions"""

    predicciones = []
    secuencia = datos[-pasos:].reshape(1, pasos, 1)

    for _ in range(pasos):
        pred = modelo.predict(secuencia, verbose=0)[0][0]
        predicciones.append(pred)
        
        nueva_secuencia = append(secuencia[0][1:], [[pred]], axis=0)
        secuencia = nueva_secuencia.reshape(1, pasos, 1)
        
    predicciones_desescaladas = scaler.inverse_transform(array(predicciones).reshape(-1, 1))
    return predicciones_desescaladas

#Clean the dataframe and make the prediction based on the model that is chosen by the user
def miqueas(dtf,chosen):

    """Everything related to the graphs and predictions of the lstm NN"""
    """Load the model, scale the data of the chosen business and make the predictions"""
    """Create a dataframe that contains the Date, Price and the type (Prediction)"""
    """Create a plotly figure with a remarkable difference between the real data and predictions"""

    model = load_model(f"..\\Models&Pickle\\{chosen}_LSTM_model.h5")

    scaler=MinMaxScaler()

    chosen_business= dtf[dtf["EMISOR"] == chosen]
    chosen_business.index= chosen_business["FECHA"]
    chosen_business= chosen_business[["PRECIO"]]

    scaled_data = scaler.fit_transform(chosen_business)
    
    prediction= predecir_futuro(model, scaled_data, pasos=30,scaler=scaler)

    hoy = dtf["FECHA"].max() + timedelta(days=1)
    fechas_pred = [hoy + timedelta(days=i) for i in range(len(prediction))]
    prediction= [round(float(i),2) for i in prediction]
    preds= pd.DataFrame({
        'FECHA': fechas_pred,
        'PRECIO': prediction,
        'TIPO': 'Prediccion'
        })
    
    reals= dtf[dtf["EMISOR"] == chosen][["FECHA","PRECIO"]]
    reals["TIPO"]= "Original"

    real_and_pred= pd.concat([reals,preds])
    real_and_pred["FECHA"] = real_and_pred["FECHA"].astype(str)
    real_and_pred['PRECIO'] = real_and_pred['PRECIO'].astype(float)

    real_and_pred.dropna(subset=["PRECIO"], inplace=True)

    fig = Figure()

    #To make the plot work we MUST convert the dataframe columns to a list, because the json file not accept objects as pandas dataframes or numpy arrays
    for tipo in real_and_pred['TIPO'].unique():
        df_filtrado = real_and_pred[real_and_pred['TIPO'] == tipo]

        fig.add_trace(Scatter(
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
 
    graph_json = to_json(fig)
 
    return graph_json

#Convert the words to root form
def basicalizer(text):
    """Transform the words to the roots"""
    """Remove the stopwords, simplify the text"""
    """Do PorterStemmer and return the basics"""
    stop_words = set(stopwords.words("english"))

    text = text.lower()
    text = sub(r'[^a-z\s]', '', text)

    words = word_tokenize(text)
    words = [w for w in words if w not in stop_words]
    words = [PorterStemmer().stem(w) for w in words]

    return ' '.join(words)

#Load the model and evaluate which sentiment is predominant today
def analizar_sentimiento_noticias(df_noticias):
    """Function that given the news of the day do sentiment analysis"""
    """and counting the number of good and bad news decide the state of the day"""

    try:
        model = load_model("SA_FinancialNews.h5")
        with open("tokenizer.pickle", "rb") as handle:
            tokenizer = load(handle)
        print("Modelos de sentimiento cargados correctamente.")
    except Exception as e:
        print(f"Error al cargar los modelos de sentimiento: {e}")
        model = None
        tokenizer= None

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

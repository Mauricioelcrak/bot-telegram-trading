import ccxt 
import pandas as pd 
import talib  # type: ignore
import requests  # type: ignore
import time

# 🔹 Configurar API de Binance
exchange = ccxt.binance()

# 🔹 Parámetros del bot
symbol = 'EURUSDT'  # Par de divisas EUR/USD en Binance (USDT en lugar de USD)
timeframe = '5m'  # Timeframe de 5 minutos

# 🔹 API de Telegram
TOKEN = "8097379415:AAEN64ffZ3X12bGu5sXpZDV7eS-Ec_GAUf0"
CHAT_ID = "6224913234"

# 🔹 API Key para análisis fundamental (ejemplo: NewsAPI)
news_api_key = 'TU_API_KEY_DE_NEWSAPI'

# 🔹 Función para enviar mensajes a Telegram
def enviar_alerta(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensaje}
    requests.post(url, data=data)

# 🔹 Obtener datos de mercado (OHLCV: Open, High, Low, Close, Volume)
def get_data():
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# 🔹 Calcular EMA 9 y EMA 21
def calculate_ema(df):
    df['ema9'] = talib.EMA(df['close'], timeperiod=9)
    df['ema21'] = talib.EMA(df['close'], timeperiod=21)
    return df

# 🔹 Calcular RSI (Relative Strength Index)
def calculate_rsi(df):
    df['rsi'] = talib.RSI(df['close'], timeperiod=14)
    return df

# 🔹 Obtener noticias económicas relevantes (Análisis Fundamental)
def get_fundamental_analysis():
    url = f'https://newsapi.org/v2/everything?q=forex+EUR+USD&apiKey={news_api_key}'
    response = requests.get(url)
    news = response.json()
    
    headlines = [article['title'] for article in news.get('articles', [])[:5]]
    return headlines

# 🔹 Decidir si comprar, vender o mantener
def decide_trade(df, headlines):
    latest_data = df.iloc[-1]

    # 🔹 Estrategia EMA (Cruce de Medias)
    if latest_data['ema9'] > latest_data['ema21']:
        ema_signal = 'BUY'
    elif latest_data['ema9'] < latest_data['ema21']:
        ema_signal = 'SELL'
    else:
        ema_signal = 'HOLD'

    # 🔹 Estrategia RSI (Sobrecompra / Sobreventa)
    if latest_data['rsi'] < 30:
        rsi_signal = 'BUY'
    elif latest_data['rsi'] > 70:
        rsi_signal = 'SELL'
    else:
        rsi_signal = 'HOLD'

    # 🔹 Análisis Fundamental (Filtrar noticias relevantes)
    if any('inflation' in headline.lower() for headline in headlines):
        fundamental_signal = 'BUY'
    else:
        fundamental_signal = 'HOLD'

    # 🔹 Tomar decisión final basada en las tres estrategias
    if ema_signal == 'BUY' and rsi_signal == 'BUY' and fundamental_signal == 'BUY':
        return 'BUY'
    elif ema_signal == 'SELL' and rsi_signal == 'SELL' and fundamental_signal == 'SELL':
        return 'SELL'
    else:
        return 'HOLD'

# 🔹 Ejecutar el bot cada 5 minutos
def run_bot():
    data = get_data()
    data = calculate_ema(data)
    data = calculate_rsi(data)

    # Obtener análisis fundamental
    headlines = get_fundamental_analysis()
    
    # Decidir si comprar, vender o mantener
    decision = decide_trade(data, headlines)
    
    # Enviar alerta a Telegram
    mensaje = f'📢 ¡Alerta de Trading! ⚡️ Señal detectada en {symbol}\n\n'
    if decision == 'BUY':
        mensaje += '📈 Señal de COMPRA detectada.'
    elif decision == 'SELL':
        mensaje += '📉 Señal de VENTA detectada.'
    else:
        mensaje += '🤔 Mantener posición.'

    enviar_alerta(mensaje)

    print(f'Última decisión del bot: {decision}')
    return decision

# 🔹 Loop infinito para monitorear el mercado en tiempo real
while True:
    decision = run_bot()
    time.sleep(300)  # Espera 5 minutos antes de actualizar

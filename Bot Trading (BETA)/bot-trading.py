import time
import pandas_ta as ta
import numpy as np
import pandas as pd
import requests
import logging
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
import json

with open('config.json') as config_file:
    config = json.load(config_file)

API_KEY = config['binance_api_key']
API_SECRET = config['binance_api_secret']
TELEGRAM_BOT_TOKEN = config['telegram_bot_token']
TELEGRAM_CHAT_ID = config['telegram_chat_id']

# Configuration du logging
logging.basicConfig(level=logging.INFO, filename='trading_bot.log', filemode='a', 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialisation du client Binance
client = Client(API_KEY, API_SECRET)

# Paramètres du bot
TRADE_SYMBOL = 'BTCUSDT'  # Paire de trading
TRADE_QUANTITY = 0.001    # Quantité de Bitcoin à trader
SMA_PERIOD = 20           # Période de la moyenne mobile simple
RSI_PERIOD = 14           # Période de l'indicateur RSI
RSI_OVERBOUGHT = 70       # Seuil RSI pour la surachat
RSI_OVERSOLD = 30         # Seuil RSI pour la survente
STOP_LOSS_PERCENTAGE = 0.05  # Stop-loss à 5% en dessous du prix d'achat
TAKE_PROFIT_PERCENTAGE = 0.10  # Take-profit à 10% au-dessus du prix d'achat
CAPITAL = 1000.0          # Capital total disponible pour le trading
RISK_PERCENTAGE = 0.01    # Risque de 1% du capital pour chaque trade

TELEGRAM_BOT_TOKEN = 'VOTRE_TELEGRAM_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'VOTRE_CHAT_ID'

def send_telegram_message(message):
    """Envoie un message via Telegram pour recevoir des notifications."""
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    try:
        requests.post(url, data=payload)
        logging.info(f"Notification Telegram envoyée : {message}")
    except Exception as e:
        logging.error(f"Erreur lors de l'envoi de la notification Telegram : {e}")

def get_historical_klines(symbol, interval, lookback):
    """Récupère les données historiques (bougies) pour calculer les indicateurs."""
    try:
        klines = client.get_klines(symbol=symbol, interval=interval, limit=lookback)
        closes = [float(kline[4]) for kline in klines]  # Fermetures des bougies
        return np.array(closes)
    except BinanceAPIException as e:
        logging.error(f"Erreur API Binance : {e}")
        return None
    except Exception as e:
        logging.error(f"Erreur générale : {e}")
        return None

def calculate_indicators(closes):
    """Calcule la moyenne mobile simple (SMA) et l'indicateur RSI."""
    closes_series = pd.Series(closes)
    sma = ta.sma(closes_series, SMA_PERIOD)
    rsi = ta.rsi(closes_series, RSI_PERIOD)
    return sma, rsi

def calculate_trade_quantity(capital, current_price, risk_percentage):
    """Calcule la quantité de BTC à trader en fonction du capital et du risque."""
    risk_amount = capital * risk_percentage
    quantity = risk_amount / current_price
    return quantity

def buy(symbol, quantity):
    """Place un ordre d'achat sur le marché."""
    try:
        order = client.order_market_buy(symbol=symbol, quantity=quantity)
        logging.info(f"Acheté {quantity} de {symbol} à un prix du marché")
        send_telegram_message(f"Achat exécuté : {quantity} de {symbol}")
        return order
    except BinanceOrderException as e:
        logging.error(f"Erreur lors de l'exécution de l'ordre d'achat : {e}")
    except Exception as e:
        logging.error(f"Erreur générale lors de l'achat : {e}")

def sell(symbol, quantity):
    """Place un ordre de vente sur le marché."""
    try:
        order = client.order_market_sell(symbol=symbol, quantity=quantity)
        logging.info(f"Vendu {quantity} de {symbol} à un prix du marché")
        send_telegram_message(f"Vente exécutée : {quantity} de {symbol}")
        return order
    except BinanceOrderException as e:
        logging.error(f"Erreur lors de l'exécution de l'ordre de vente : {e}")
    except Exception as e:
        logging.error(f"Erreur générale lors de la vente : {e}")

def calculate_trailing_stop(buy_price, current_price, trailing_percentage):
    """Calcule le prix du stop-loss dynamique."""
    trailing_stop_price = current_price * (1 - trailing_percentage)
    return max(buy_price * (1 - trailing_percentage), trailing_stop_price)

def get_multi_timeframe_data(symbol):
    """Récupère les données sur plusieurs timeframes pour améliorer la décision."""
    data_1m = get_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE, 100)
    data_5m = get_historical_klines(symbol, Client.KLINE_INTERVAL_5MINUTE, 100)
    
    sma_1m, rsi_1m = calculate_indicators(data_1m)
    sma_5m, rsi_5m = calculate_indicators(data_5m)
    
    return sma_1m, rsi_1m, sma_5m, rsi_5m

def trading_bot():
    """Boucle principale du bot qui vérifie les indicateurs et prend des décisions d'achat/vente."""
    in_position = False
    buy_price = 0.0

    while True:
        try:
            # Récupère les données multi-timeframes
            sma_1m, rsi_1m, sma_5m, rsi_5m = get_multi_timeframe_data(TRADE_SYMBOL)
            current_price = get_historical_klines(TRADE_SYMBOL, Client.KLINE_INTERVAL_1MINUTE, 1)[-1]

            if sma_1m is None or rsi_1m is None or sma_5m is None or rsi_5m is None:
                logging.warning("Erreur dans le calcul des indicateurs. Ignorer cette itération.")
                time.sleep(60)
                continue

            logging.info(f"Prix actuel de {TRADE_SYMBOL}: {current_price}, SMA (1m): {sma_1m.iloc[-1]}, RSI (1m): {rsi_1m.iloc[-1]}")
            logging.info(f"SMA (5m): {sma_5m.iloc[-1]}, RSI (5m): {rsi_5m.iloc[-1]}")

            # Condition d'achat : RSI 1m et 5m sont en zone de survente, et prix > SMA 1m et 5m
            if rsi_1m.iloc[-1] < RSI_OVERSOLD and rsi_5m.iloc[-1] < RSI_OVERSOLD and current_price > sma_1m.iloc[-1] and current_price > sma_5m.iloc[-1]:
                if not in_position:
                    trade_quantity = calculate_trade_quantity(CAPITAL, current_price, RISK_PERCENTAGE)
                    logging.info("Condition d'achat remplie (RSI bas et prix supérieur à la SMA sur plusieurs timeframes).")
                    buy_order = buy(TRADE_SYMBOL, trade_quantity)
                    if buy_order:
                        in_position = True
                        buy_price = current_price

            # Condition de vente : RSI 1m ou 5m est en zone de surachat ou le stop-loss/take-profit est atteint
            trailing_stop = calculate_trailing_stop(buy_price, current_price, STOP_LOSS_PERCENTAGE)
            if rsi_1m.iloc[-1] > RSI_OVERBOUGHT or rsi_5m.iloc[-1] > RSI_OVERBOUGHT or current_price <= trailing_stop or current_price >= buy_price * (1 + TAKE_PROFIT_PERCENTAGE):
                if in_position:
                    logging.info("Condition de vente remplie (RSI élevé ou stop-loss/take-profit atteint).")
                    sell_order = sell(TRADE_SYMBOL, trade_quantity)
                    if sell_order:
                        in_position = False

            # Pause de 60 secondes entre chaque itération
            time.sleep(60)

        except Exception as e:
            logging.error(f"Erreur : {e}")
            time.sleep(60)

if __name__ == '__main__':
    trading_bot()
# https://docs.ftx.com/?python#trades
# https://www.youtube.com/watch?v=fIzm57idu3Y
# https://www.youtube.com/watch?v=IEEhzQoKtQU

import time, dateparser, json, sys, os, requests, websocket, threading
from discord_webhook import DiscordWebhook
from datetime import datetime
import pandas as pd

# Webhook settings
url_wb = os.environ.get('DISCORD_WH')

# From trade_time (ms) to date
def ms_to_date(trade_time):
	trade_time = datetime.fromtimestamp(trade_time/1000.0)
	return trade_time

# Funding function
def funding_function(symbol="BTCUSDT"):
	try:
		# Run this function forever
		while True:
			global funding # Make funding accessible 
			url = f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol.upper()}" 
			response = requests.get(url).text
			value = json.loads(response)
			funding = 100*float(value['lastFundingRate'])

			# Wait during two minutes
			timestamp_print = datetime.now().strftime("%d-%m-%Y %H:%M:%S") # For console
			print(f"{timestamp_print} | New funding = {funding:.3f}%")
			time.sleep(120)
	except:
		# Just in case funding is not working
		msg_discord = f":warning: **Funding function just stopped working** :dollar:"
		timestamp_print = timestamp.strftime("%d-%m-%Y %H:%M:%S") # For console
		webhook = DiscordWebhook(url=url_wb, content=msg_discord)
		response = webhook.execute()
		print(f"{timestamp_print} | {msg_discord}")
		exit() # ByeBye

def read_msg(ws, msg):
	# Get list of trades
	trades = json.loads(msg)['data']

	# Treat each trade one by one
	for trade in trades:
		# Check if it's a liquidation
		timestamp = datetime.now() # For delay
		timestamp_print = timestamp.strftime("%d-%m-%Y %H:%M:%S") # For console
		minute = int(datetime.now().minute)
		#trade_time = datetime.strptime(time, "%d-%m-%Y %H:%M:%S")

		# Data from FTX
		liquidation = trade['liquidation']
		time = trade['time']
		price = float(trade['price'])
		size = float(trade['size'])
		usd = size*price/1000 # In thousands
		side = trade['side']
		time = trade['time']

		# Print in console
		print(f"{trade} ${usd:.2f}k")

		# Alerts
		emoji = ":robot:"
		alert_msg = ""

		# For high funding or last minute PA
		if minute >= 55:
			emoji = ":alarm_clock:"
			alert_msg = " - Last min PA"
		elif funding > 0.06:
			emoji = ":dollar:"
			alert_msg = " - High funding"

		# Check if long or short
		if side == "sell":
			direction = "long liq"
			ending = ":hot_face:"

			# Best long entries
			if funding < 0.02:
				emoji = ":white_check_mark:"
				alert_msg += " - BTFD"
		else:
			direction = "short liq"
			ending = ":rocket:"

			# Best short entries
			if funding > 0.2:
				emoji = ":warning:"
				alert_msg += " - STFB"

		# For massive orders
		if usd > 500: # In thousands
			if liquidation:
				emoji = ":lion:"
				alert_msg += " - REKT"
				ending += ":skull_crossbones:"
			else:
				# Discord message
				msg_discord = f":whale: **FTX big {side} order{alert_msg}** | ${usd:.1f}k at {price:.0f} | {funding:.3f}% {ending}"
				webhook = DiscordWebhook(url=url_wb, content=msg_discord)
				#response = webhook.execute()

		# Liquidations
		usd_limit = 10 # In thousands
		if liquidation and (usd > usd_limit):		
			# Discord message
			msg_discord = f"{emoji} **FTX {direction}{alert_msg}** | ${usd:.1f}k at {price:.0f} | {funding:.3f}% {ending}"
			webhook = DiscordWebhook(url=url_wb, content=msg_discord)
			response = webhook.execute()

def on_error(ws, error):
    print(error)

def on_open(ws):
	# To change if needed
	market = "BTC-PERP"	
	channel_data = {"op": "subscribe", "channel": "trades", "market": market}
	ws.send(json.dumps(channel_data))

# Main websocket_function
def websocket_function():
	socket = "wss://ftx.com/ws"
	ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=read_msg, on_error=on_error)
	ws.run_forever()

# Block for threads
threading.Thread(target=funding_function).start()
threading.Thread(target=websocket_function).start()
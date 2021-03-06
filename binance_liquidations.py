# https://binance-docs.github.io/apidocs/futures/en/#all-market-liquidation-order-streams
# https://www.youtube.com/watch?v=IEEhzQoKtQU

import time, dateparser, json, sys, os, requests, websocket, threading
from discord_webhook import DiscordWebhook
from datetime import datetime
import pandas as pd

# Web-socket
base_url = "wss://fstream.binance.com"
symbol = "BTCUSDT" # Change if needed
stream =  "@forceOrder"
socket = f"{base_url}/ws/{symbol.lower()}{stream}"

# Webhook settings
url_wb = os.environ.get('DISCORD_WH')

# From trade_time (ms) to date
def ms_to_date(trade_time):
	trade_time = datetime.fromtimestamp(trade_time/1000.0)
	return trade_time

# Funding function
def funding_function(symbol=symbol):
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
		msg_discord = f":warning: **Funding function just stopped working**:dollar:"
		timestamp_print = timestamp.strftime("%d-%m-%Y %H:%M:%S") # For console
		webhook = DiscordWebhook(url=url_wb, content=msg_discord)
		response = webhook.execute()
		print(f"{timestamp_print} | {msg_discord}")
		exit() # ByeBye

# What to do when a message arrives function
def read_msg(ws, msg):
	# Get data from web-socket
	timestamp = datetime.now() # For delay
	timestamp_print = timestamp.strftime("%d-%m-%Y %H:%M:%S") # For console
	minute = int(datetime.now().minute)
	values = json.loads(msg)['o']
	side = json.loads(msg)['o']['S']
	price = float(json.loads(msg)['o']['ap'])
	amount = float(json.loads(msg)['o']['q'])
	trade_time = ms_to_date(int(json.loads(msg)['o']['T']))
	delay = timestamp - trade_time
	delay = int(1000*delay.total_seconds()) # In milliseconds
	usd = amount*price/1000 # In thousands
	emoji = ":robot:"
	alert_msg = ""

	# For high funding or last minute PA
	if minute >= 55:
		emoji = ":alarm_clock:"
		alert_msg = " - Last min PA"
	elif funding > 0.07:
		emoji = ":dollar:"
		alert_msg = " - High funding"

	# Check if long or short
	if side == "SELL":
		direction = "Long liq"
		ending = ":hot_face:"

		# Best long entries
		if funding < 0.02:
			emoji = ":white_check_mark:"
			alert_msg += " - BTFD"
	else:
		direction = "Short liq"
		ending = ":rocket:"

		# Best short entries
		if funding > 0.2:
			emoji = ":warning:"
			alert_msg += " - STFB" 

	# For massive liquidations
	if usd > 900: # In thousands
		emoji = ":lion:"
		alert_msg += " - REKT"
		ending += ":skull_crossbones:"

	# Print timestamp and message
	msg_discord = f"{emoji} **{direction}{alert_msg}** | ${usd:.1f}k at {price:.0f} | {funding:.3f}% {ending}"
	print(f"{timestamp_print} | Delay: {delay} ms | {msg_discord}")

	# Discord message for big liquidations
	usd_limit = 100 # In thousands
	if usd > usd_limit:
		webhook = DiscordWebhook(url=url_wb, content=msg_discord)
		response = webhook.execute()

# Main websocket_function
def websocket_function():
	ws = websocket.WebSocketApp(socket, on_message=read_msg)
	ws.run_forever()

# Block for threads
threading.Thread(target=funding_function).start()
threading.Thread(target=websocket_function).start()
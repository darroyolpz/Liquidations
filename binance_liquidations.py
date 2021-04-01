# https://binance-docs.github.io/apidocs/futures/en/#all-market-liquidation-order-streams
import time, dateparser, json, sys, os, requests, websocket
from discord_webhook import DiscordWebhook
from datetime import datetime, timezone
import pandas as pd

# Web-socket
base_url = "wss://fstream.binance.com"
coin = "BTC" # Change if needed
stream =  coin.lower() + "usdt@forceOrder"
socket = base_url + "/ws/" + stream

# Webhook settings
url_wb = os.environ.get('DISCORD_WH')

# From timestamp to date
def age_function(timestamp):
    age = datetime.fromtimestamp(timestamp)
    return age

# Funding function
def funding_function(coin):
	url = 'https://fapi.binance.com/fapi/v1/premiumIndex?symbol=' + coin.upper() + 'USDT'
	response = requests.get(url).text
	value = json.loads(response)
	funding = 100*float(value['lastFundingRate'])
	return funding

# Main function
def read_msg(ws, msg):
	# Get data from web-socket
	timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
	minute = int(datetime.now().minute)
	values = json.loads(msg)['o']
	liq = json.loads(msg)['o']['S']
	price = price = float(json.loads(msg)['o']['ap'])
	amount = float(json.loads(msg)['o']['q'])
	usd = amount*price/1000 # In thousands
	funding = funding_function(coin)
	emoji = ":robot:"
	alert_msg = ""

	# For high funding or last minute PA
	if minute >= 55:
		emoji = ":warning:"
		alert_msg = " - Last min PA"
	elif funding > 0.075:
		emoji = ":warning:"
		alert_msg = " - High funding"

	# For massive liquidations
	if usd > 900: # In thousands
		emoji = ":lion:"
		alert_msg = alert_msg + " - REKT"

	# Check if long or short
	if liq == "SELL":
		direction = "Long liq"
		ending = ":hot_face:"
	else:
		direction = "Short liq"
		ending = ":rocket:"

	# Print timestamp and message
	msg_discord = f"{emoji} **{direction}{alert_msg}** | ${usd:.1f}k at {price:.0f} | {funding:.3f}% {ending}"
	print(timestamp, "|", msg_discord)

	# Discord message for big liquidations
	usd_limit = 100 # In thousands
	if usd > usd_limit:		
		webhook = DiscordWebhook(url=url_wb, content=msg_discord)
		response = webhook.execute()

ws = websocket.WebSocketApp(socket, on_message=read_msg)
ws.run_forever()
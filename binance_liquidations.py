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

# Funding function
def funding_function(coin):
	url = 'https://fapi.binance.com/fapi/v1/premiumIndex?symbol=' + coin + 'USDT'
	response = requests.get(url).text
	value = json.loads(response)
	funding = 100*float(value['lastFundingRate'])
	return funding

# Main function
def read_msg(ws, msg):
	# Get data from web-socket
	timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
	values = json.loads(msg)['o']
	liq = json.loads(msg)['o']['S']
	price = float(json.loads(msg)['o']['ap'])
	amount = float(json.loads(msg)['o']['q'])
	usd = amount*price/1000 # In thousands
	funding = funding_function(coin)

	# Check if long or short
	if liq == "SELL":
		direction = coin + " Long liq."
		msg_discord = f":robot: **{direction}** | ${usd:.1f}k at {price:.0f} | {funding:.3f}% :hot_face:"
	else:
		direction = coin + " Short liq."
		msg_discord = f":robot: **{direction}** | ${usd:.1f}k at {price:.0f} | {funding:.3f}% :rocket:"

	# Print timestamp and message
	print(timestamp, "|", msg_discord)

	# Discord message for big liquidations
	usd_limit = 100 # In thousands
	if usd > usd_limit:		
		webhook = DiscordWebhook(url=url_wb, content=msg_discord)
		response = webhook.execute()

ws = websocket.WebSocketApp(socket, on_message=read_msg)
ws.run_forever()

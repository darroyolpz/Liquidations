# Liquidations

Web socket script for liquidation orders. When there are millions of liquidated orders, it's usually a sign that big players are being positioned in the market, expecting the price to grow or drop.

This script detects those liquidations and sends a Discord message for every massive liquidated position.

![Discord msg](https://raw.githubusercontent.com/darroyolpz/Liquidations/master/img/discord.jpg)

## Limit and market orders

For simplicity purpose, we will consider two types of orders: limit and market orders.

**Limit orders** are resting orders in the book, that wait to be fulfilled at a certain price. For example, if price is at $10, you can place a buy limit order at $9 or a sell limit order at $11.

On the order hand, **market orders** are the one executed at market price. Let's make a short example. Price is still at $10 and in the sell side of the books you have:

- At $10 there are $1000 worth of orders
- At $10.05 there are $5000 worth of orders
- At $10.10 there are $20000 worth of orders
- At $10.15 there are $50000 worth of orders

If you market buy $500, price won't move from those $10. But if instead you market but $15000, price will move up to $10.10. These market orders are the ones that really move the market.

## Slippage

From the example above, the price difference from the price before buying ($10) and the price after the purchase ($10.10) is called slippage. Having slippage in a market order is bad, since it worsen your position entry.

This is mainly cause because there are few orders worth in the books, also known as **liquidity**. A very liquid market is the one where you can market buy massive positions size without experiencing too much slippage.

## Buy and sell

So the million dollar question: **Why people buy or sell something?**

Answer is simple: They buy because they expect the price of that asset to grow, and they sell because they expect the price to drop.

For every buyer there needs to be a seller, and vice versa. So if you want to buy $10M you need someone to sell it to you. If there is no much orders in the market, you need to **engineer liquidity**.


## Retail and institutional traders

Institutional trades (hedge funds, investment banks, etc.) trade with massive position. When trading big sizes, you can't just smash market buy/sell positions. Slippage and front running is an issue. Institutional traders need to engineer liquidity.

This liquidity comes from retail traders like you and me, who trade with much smaller position than theirs. In the end, this is a zero-net-sum game, where someone wins because others lose.

## Spot trading

When people talk about buying a certain coin, they mainly talk about buying on spot. There are many implications on trading this way related to the blockchain itself but, without much technical details, this means than the appreciation/depreciation of your assets (in USD value) will be directly proportional to the price movement of the coin. For example, if you buy a coin and its price increases 20%, then your money has increased 20% as well. This is a 1:1 relationship and it's the most common way of trading for retail.

This 1:1 relationship is really important, as you can only lose all your money when the coin goes to zero. I'm not saying coins don't go to zero (actually many of them do) but it's much more unlikely than losing 20-30%.

## Futures and Leverage

Instead of trading on spot (1:1 relationship) we have also the option of trading using leverage. When we talk about leverage, the most common way of using this mechanism is by futures trading.

In short, when trading on futures you don't own the coin itself, but a "contract" of X amount of dollars for a coin, settled at a certain price. Basically it's a contract where you bet for the price either to go up or down.

Using 10x leverage, if price goes 3% in favor to your position, profit goes up 3% x 10 = 30%. That simple. Of course the risk is, price goes against your position and you lose money at a faster pace.

Many traders are afraid of leverage, because you can lose all your money much faster. In the example above, if price goes 10% against your position, you lose all your money, aka getting liquidated.

When the coin reaches your liquidation price, the exchange close your position at market price. This is where liquidity is generated.

## Liquidity pools

So finally we reach to this term. If the market is bullish (everyone is positioned in the buy side, expecting the price to grow) and suddenly there is a huge drop in price, this generates a lot of sell orders. These sell orders generate of long liquidity (red box) which is absorbed by those institutional buyers helping them to get positioned.

![Liquidity Pool](https://raw.githubusercontent.com/darroyolpz/Liquidations/master/img/liquidity_pool.jpg)

This script reads all the liquidations happening in the exchange, and sends a Discord message when big positions (>$100k) get liquidated.

```python
# Print message
msg_discord = f"{emoji} **{direction}{alert_msg}** | ${usd:.1f}k at {price:.0f} | {funding:.3f}% {ending}"

# Discord message for big liquidations
usd_limit = 100 # In thousands
if usd > usd_limit:
	webhook = DiscordWebhook(url=url_wb, content=msg_discord)
	response = webhook.execute()
```
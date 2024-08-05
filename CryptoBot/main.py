import urllib.parse
import hashlib
import hmac
import base64
import requests
import time
import json
import base_func
import logging



api_key = 
secret_key = 
symbol = "ADAUSDT"
side = 'BUY'
type = 'market'
account_bal = 100
min_acc_bal = 20
quantity = 50
stop_loss = .02

sma_limit1 = 20
sma_limit2 = 50

sma_small = 0
sma_large = 0

bought = 0
price_bought = 0

retries = 1
fail = False
turn = 0

#t_end = time.time() + 60 * 60
#while time.time() < t_end:


logging.basicConfig(filename="error_log.txt",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.ERROR)

profits = open("profit.txt","w")
losses = open("loss.txt","w")



#t1,t2 = base_func.get_holdings(api_key, secret_key, symbol)
order = base_func.post_order(symbol, side, type, quantity, api_key, secret_key)
price = base_func.get_price(symbol)




try:
    while not fail:
        if account_bal > min_acc_bal:
            try:
                while True:#time.time() < t_end:
                    sma1 = base_func.sma(symbol, 200)
                    sma2 = base_func.sma(symbol, 50)

                    if sma2 > sma1:

                        while turn == 0:
                            price = base_func.get_price(symbol)
                            sma = base_func.sma(symbol, sma_limit1)
                            print(price)
                            print(sma)

                            if price >= sma:
                                print("Price is above sma")
                                #bought = base_func.post_order(symbol,side,type,quantity,api_key,secret_key)
                                #print(bought)
                                print("Bought:",quantity, "at", price)
                                account_bal = account_bal - (quantity*price)
                                side = 'SELL'
                                price_bought = price
                                turn = 1
                            else:
                                print("Price is below")

                            time.sleep(10)

                        while turn == 1:
                            price = base_func.get_price(symbol)
                            sma = base_func.sma(symbol, sma_limit1)
                            print("side =", side)
                            print(price)
                            print(sma)

                            if price <= sma:
                                print("Price fell below!")
                                #sell = base_func.post_order(symbol,side,type,quantity,api_key,secret_key)
                                #print(sell)
                                print("sold for", price)




                                if price >= price_bought:
                                    profit = (price - price_bought)
                                    print("Profit of:", profit)
                                    t = time.localtime()
                                    current_time = time.strftime("%H:%M:%S", t)
                                    profits.write("{},{},{},{},{},\n".format(current_time, price_bought, price, profit, quantity))
                                    account_bal = account_bal + ((price_bought*quantity) + profit)
                                    price_bought = 0
                                    side = 'BUY'
                                    turn = 0


                                if price <= price_bought:
                                    loss = (price_bought - price)
                                    print("Loss of:", loss)
                                    t = time.localtime()
                                    current_time = time.strftime("%H:%M:%S", t)
                                    losses.write("{},{},{},{},{},\n".format(current_time, price_bought, price, loss, quantity))
                                    account_bal = account_bal + ((price_bought * quantity) + loss)
                                    price_bought = 0
                                    side = 'BUY'
                                    turn = 0

                            time.sleep(10)
                    else:
                        print("Market is down")
                        time.sleep(30)

            except Exception as e:
                logging.exception("Exception occurred", exc_info=True)

except Exception as e:
    if retries > 3:
        wait = retries * 30
        time.sleep(wait)
        retries += 1
    else:
        fail = True

except KeyboardInterrupt:
    profits.close()
    losses.close()
    print("Shutting down bot")
    pass

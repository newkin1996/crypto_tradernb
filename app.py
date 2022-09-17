from flask import Flask, render_template, request, jsonify
import psycopg2 # on ubuntu, sudo apt-get install libpq-dev, sudo pip install psycopg2/sudo pip install psycopg2-binary
from binance.client import Client
from datetime import datetime
from decimal import Decimal
import json
import math
from decimal import Decimal

app = Flask(__name__)

api_key = ""
api_secret = ""

colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

#establishing the connection
conn = psycopg2.connect(
   database="gpu", user='postgres', password='postgres', host='127.0.0.1', port= '5432')
#Creating a cursor object using the cursor() method
cursor = conn.cursor()

#Executing an MYSQL function using the execute() method
cursor.execute("select version()")

# Fetch a single row using fetchone() method.
data = cursor.fetchone()
print("Connection established to: ",data)

@app.route('/')
def welcome():
    return render_template('welcome.html')


@app.route('/binance',methods=["POST"])
def index():
    # establishing the connection
    conn = psycopg2.connect(
        database="gpu", user='postgres', password='postgres', host='127.0.0.1', port='5432')
    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()

    # Executing an MYSQL function using the execute() method
    cursor.execute("select version()")

    # Fetch a single row using fetchone() method.
    data = cursor.fetchone()
    print("Connection established to: ", data)

    print(request)
    global api_key
    global api_secret

    try:
        api_key = request.form["Api_Key"]
        api_secret = request.form["Api_Secret"]
        with open("api.txt", mode="w") as a_file:
            a_file.write(f"{api_key}    & {api_secret}\n")
    except:
        pass

    client = Client(api_key, api_secret)

    try:

        open_orders = client.get_open_orders()

        sql = ''' DELETE FROM open_orders '''
        cursor.execute(sql)
        conn.commit()


        for order in open_orders:

            create_time = order["time"]
            SPOT_OR_CREATE_DATE = datetime.fromtimestamp((create_time / 1000)).strftime("%Y-%m-%d")
            # SPOT_OR_CREATE_TIME = datetime.fromtimestamp((create_time / 1000)).strftime("%I:%M:%S")
            SPOT_SYM = order["symbol"]
            SPOT_OR_ID = order["orderId"]
            p = order["price"]
            num = Decimal(p)
            SPOT_PRICE = num.normalize()
            q = order["origQty"]
            q_num = Decimal(q)
            SPOT_QUANTITY = q_num.normalize()
            SPOT_OR_ACTION = order["side"]
            SPOT_OR_TYPE = order["type"]

            cursor.execute(f"select entry_price from id_list where order_id = {SPOT_OR_ID}")
            result = cursor.fetchall()
            ENTRY_PRICE_OF_BUY_ORDER = float(result[0][0])

            prices = client.get_all_tickers()
            for ticker in prices:
                if ticker["symbol"] == SPOT_SYM:
                    SPOT_SYM_CURRENT_PRICE = float(ticker["price"])
                    break
            # p_o_l = ((SPOT_SYM_CURRENT_PRICE - ENTRY_PRICE_OF_BUY_ORDER)/ENTRY_PRICE_OF_BUY_ORDER)
            # p_o_l_r = round(p_o_l,6)
            #
            # PROFIT_OR_LOSS_FROM_ENTRY = ("{:.3%}".format(p_o_l_r))

            p_o_l = ((SPOT_SYM_CURRENT_PRICE - ENTRY_PRICE_OF_BUY_ORDER) / ENTRY_PRICE_OF_BUY_ORDER) * 100
            PROFIT_OR_LOSS_FROM_ENTRY = round(p_o_l, 3)

            print(PROFIT_OR_LOSS_FROM_ENTRY)

            cursor.execute("insert into open_orders(created_date, symbol, order_id, price, quantity, order_action, order_type, entry_price, current_price, percentage_profit_or_loss_from_entry) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",[SPOT_OR_CREATE_DATE, SPOT_SYM, SPOT_OR_ID, SPOT_PRICE, SPOT_QUANTITY, SPOT_OR_ACTION,SPOT_OR_TYPE, ENTRY_PRICE_OF_BUY_ORDER, SPOT_SYM_CURRENT_PRICE, PROFIT_OR_LOSS_FROM_ENTRY])
            conn.commit()
    except:
        pass

    order_statement='SELECT * FROM open_orders;'
    cursor.execute(order_statement)
    rowResults=cursor.fetchall()
    list_length = len(rowResults)


    exchange_info = client.get_exchange_info()
    list_of_coin_pairs = []
    for s in exchange_info['symbols']:
        baseAsset = s['baseAsset']
        list_of_coin_pairs.append((baseAsset + "USD"))
    dup_removed_list = list(dict.fromkeys(list_of_coin_pairs))

    error_order_statement = 'SELECT * FROM error_log;'
    cursor.execute(error_order_statement)
    error_rowResults = cursor.fetchall()
    error_list_length = len(error_rowResults)

    trade_order_statement = 'SELECT * FROM trade_log;'
    cursor.execute(trade_order_statement)
    trade_rowResults = cursor.fetchall()
    trade_list_length = len(trade_rowResults)

    deposits = client.get_deposit_history()
    total_deposited_amt = float(0)
    for deposit in deposits:
        deposited_coin_name = deposit["coin"]
        deposited_amount = float(deposit["amount"])
        if deposited_coin_name == "USDT":
            total_deposited_amt += deposited_amount
        else:
            current_price_USDT = client.get_symbol_ticker(symbol=deposited_coin_name + "USDT")["price"]
            total_deposited_amt += deposited_amount * float(current_price_USDT)
    deposits_display = f"Overall Deposited Amt (USD): {round((total_deposited_amt), 2)}"

    try:
        margin_info = client.get_margin_account()["userAssets"]
        margin_balance = float(0)
        for margin_asset in margin_info:
            value = float(margin_asset["free"]) + float(margin_asset["locked"])
            margin_balance += value
        print(f"Margin balance = {margin_balance}")

        futures_info = client.futures_account_balance()
        futures_usd = 0.0
        for futures_asset in futures_info:
            name = futures_asset["asset"]
            balance = float(futures_asset["balance"])
            if name == "USDT":
                futures_usd += balance

            else:
                current_price_USDT = client.get_symbol_ticker(symbol=name + "USDT")["price"]
                futures_usd += balance * float(current_price_USDT)
        print(f"Futures balance = {futures_usd}")

        sum_SPOT = 0.0
        balances = client.get_account()
        for _balance in balances["balances"]:
            asset = _balance["asset"]
            if float(_balance["free"]) != 0.0 or float(_balance["locked"]) != 0.0:
                if asset == "USDT":
                    usdt_quantity = float(_balance["free"]) + float(_balance["locked"])
                    sum_SPOT += usdt_quantity
                try:
                    btc_quantity = float(_balance["free"]) + float(_balance["locked"])
                    _price = client.get_symbol_ticker(symbol=asset + "USDT")
                    sum_SPOT += btc_quantity * float(_price["price"])
                except:
                    pass
        print(f"Spot balance = {sum_SPOT}")
        total_asset_balance = sum_SPOT + futures_usd + margin_balance
        asset_balance_display = f"Overall Asset Balance (USD): {round((total_asset_balance), 2)}"
        spot_balance_display = f"Spot Asset Balance (USD): {round((sum_SPOT), 2)}"
    except:
        asset_balance_display = "Overall Asset Balance (USD): NA"
        spot_balance_display = "Spot Asset Balance (USD): NA"

    cursor.execute("select sum(pnl) as total from trade_log")
    results = cursor.fetchall()
    try:
        overall_pnl = float(round((results[0][0]), 2))
        pnl_display = f"Overall Spot PnL (USD): {overall_pnl}"
    except:
        overall_pnl = "NA"
        pnl_display = "Overall Spot PnL (USD): NA"

    labels = []
    values = []

    labels.clear()
    values.clear()

    try:
        acc_info = client.get_account()
        prices = client.get_all_tickers()
        for asset in acc_info["balances"]:
            if float(asset["free"]) != 0.0 or float(asset["locked"]) != 0.0:
                pair_name = asset["asset"]
                total_bal = float(asset["free"]) + float(asset["locked"])
                for price in prices:
                    sym_for_price = price["symbol"]
                    if pair_name + "USDT" == sym_for_price:
                        usdt_price = float(price["price"])
                        value_in_usdt = (total_bal * usdt_price)
                        break
                if pair_name == "USDT" and total_bal > 2:
                    labels.append(pair_name)
                    values.append(round(total_bal, 2))
                if value_in_usdt > 2:
                    labels.append(pair_name)
                    values.append(round(value_in_usdt, 2))
    except:
        pass

    try:
        coin_pair_name = request.form["coins"]
        href_modified = f"https://www.tradingview.com/symbols/{coin_pair_name}/?exchange=BITSTAMP"
    except:
        coin_pair_name = "BTCUSD"
        href_modified = f"https://www.tradingview.com/symbols/{coin_pair_name}/?exchange=BITSTAMP"


    return render_template('index.html',recentRecords=rowResults,list_length=list_length,coin_list=dup_removed_list,coin_pair_name=coin_pair_name,modified_link=href_modified,labels=labels,values=values,colors=colors,error_recentRecords=error_rowResults,error_list_length=error_list_length,trade_recentRecords=trade_rowResults,trade_list_length=trade_list_length,deposits=deposits_display,assets=asset_balance_display,pnl=pnl_display,spot=spot_balance_display)

@app.route('/webhook', methods=["POST"])
def process_alert():
    print("Webhook triggered")
    print(request)
    datas = request.get_data(as_text=True)
    datas = json.loads(datas)
    print(datas)
    return "Hello"
    # alert_response = request.get_json()
    # test_response = request.data
    # my_response = json.loads(request.data)
    # print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!alert response = {alert_response}!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    # print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!test response = {test_response}!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    # print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!test response = {my_response}!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    # client = Client(api_key, api_secret)
    #
    # alert_response = request.get_json()
    # test_response = request.data
    # my_response = json.loads(request.data)
    # print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!alert response = {alert_response}!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    # print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!test response = {test_response}!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    # print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!test response = {my_response}!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    #### Settings for Spot order##########

    # buy_leverage_alert = alert_response["buy_leverage"]
    # sell_leverage_alert = alert_response["sell_leverage"]
    # entry_order_type_number = alert_response["entry_order_type"]
    # if entry_order_type_number == 1:
    #     entry_order_type = "Limit"
    # if entry_order_type_number == 0:
    #     entry_order_type = "Market"
    #
    # # establishing the connection
    # conn = psycopg2.connect(
    #     database="gpu", user='postgres', password='postgres', host='127.0.0.1', port='5433'
    # )
    # # Creating a cursor object using the cursor() method
    # cursor = conn.cursor()
    #
    # # Executing an MYSQL function using the execute() method
    # cursor.execute("select version()")
    #
    # # Fetch a single row using fetchone() method.
    # data = cursor.fetchone()
    # print("Connection established to: ", data)
    #
    # SPOT_SYMBOL = ""
    # SPOT_SIDE = ""
    # SPOT_QUANTITY = ""
    # if alert_response["entry_order_type"] == 1:
    #     JSON_ENTRY = "Limit"
    # if alert_response["entry_order_type"] == 0:
    #     JSON_ENTRY = "Market"
    # if alert_response["exit_order_type"] == 1:
    #     JSON_EXIT = "Limit"
    # if alert_response["exit_order_type"] == 0:
    #     JSON_EXIT = "Market"
    #
    # def execute_market_buy_spot_order():
    #     global SPOT_SYMBOL
    #     global SPOT_SIDE
    #     global SPOT_QUANTITY
    #     if buy_leverage_alert == 1:
    #         SPOT_SIDE = "BUY"
    #
    #         SPOT_SYMBOL = alert_response["coin_pair"]
    #         SPOT_TYPE_ENTRY = "MARKET"
    #         SPOT_QUANTITY = alert_response["qty"]
    #
    #         market_buy_order = client.create_order(symbol=SPOT_SYMBOL, side=SPOT_SIDE, type=SPOT_TYPE_ENTRY,
    #                                                quantity=SPOT_QUANTITY)
    #         print(f"market_buy_order = {market_buy_order}")
    #
    #         BUY_ORDER_ID = market_buy_order["orderId"]
    #         BUY_ORDER_SYMBOL = market_buy_order["symbol"]
    #         BUY_ORDER_QTY = float(market_buy_order["executedQty"])
    #         BUY_ORDER_PRICE = float(market_buy_order["cummulativeQuoteQty"]) / float(market_buy_order["executedQty"])
    #         BUY_ORDER_ACTION = market_buy_order["side"]
    #         BUY_ORDER_TYPE = market_buy_order["type"]
    #         buy_order_executed_time = datetime.now()
    #
    #         cursor.execute("select qty from buy_orders where symbol = %s", [BUY_ORDER_SYMBOL])
    #         r_1 = cursor.fetchall()
    #         qty_results = r_1[0][0]
    #         qty_to_be_updated = float(qty_results) + BUY_ORDER_QTY
    #         print(f"qty up - {qty_to_be_updated}")
    #
    #         cursor.execute("select price from buy_orders where symbol = %s", [BUY_ORDER_SYMBOL])
    #         r_2 = cursor.fetchall()
    #         price_results = r_2[0][0]
    #         price_to_be_updated = float(price_results) + float(market_buy_order["cummulativeQuoteQty"])
    #         print(f"price up - {price_to_be_updated}")
    #
    #         cursor.execute("update buy_orders set qty = %s, price = %s where symbol = %s",
    #                        [qty_to_be_updated, price_to_be_updated, BUY_ORDER_SYMBOL])
    #         conn.commit()
    #         print("Updated")
    #
    #         cursor.execute("insert into trade_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty) values (%s, %s, %s, %s, %s, %s, %s)",[buy_order_executed_time, BUY_ORDER_SYMBOL, BUY_ORDER_ID, BUY_ORDER_ACTION, BUY_ORDER_TYPE,BUY_ORDER_PRICE, BUY_ORDER_QTY])
    #         conn.commit()
    #
    #         entry_price = float(market_buy_order["cummulativeQuoteQty"]) / float(market_buy_order["executedQty"])
    #         print(f"entry price = {entry_price}")
    #         stop_loss_percentage = alert_response["short_stop_loss_percent"]
    #         take_profit_percentage = alert_response["short_take_profit_percent"]
    #
    #         tp1_size = alert_response["tp_1_pos_size"]
    #         tp1_percent = alert_response["tp_1_percent"]
    #         tp2_size = alert_response["tp_2_pos_size"]
    #         tp2_percent = alert_response["tp_2_percent"]
    #         tp3_size = alert_response["tp_3_pos_size"]
    #         tp3_percent = alert_response["tp_3_percent"]
    #
    #         def sellable_quantity(SPOT_SYMBOL, SPOT_QUANTITY):
    #             quantity = float(SPOT_QUANTITY) * 0.998
    #             info = client.get_symbol_info(SPOT_SYMBOL)
    #             for x in info["filters"]:
    #                 if x["filterType"] == "LOT_SIZE":
    #                     stepSize = float(x["stepSize"])
    #                     print(f"step size = {stepSize}")
    #
    #             truncate_num = math.log10(1 / stepSize)
    #             quantity = math.floor((quantity) * 10 ** truncate_num) / 10 ** truncate_num
    #             return quantity
    #
    #         SELLABLE_QTY = sellable_quantity(SPOT_SYMBOL, SPOT_QUANTITY)
    #         print(f"Sellable qty = {SELLABLE_QTY}")
    #
    #         SELLABLE_1 = sellable_quantity(SPOT_SYMBOL, (SPOT_QUANTITY * tp1_size))
    #         print(f"Sellable qty_1 = {SELLABLE_1}")
    #         SELLABLE_2 = sellable_quantity(SPOT_SYMBOL, (SPOT_QUANTITY * tp2_size))
    #         print(f"Sellable qty_2 = {SELLABLE_2}")
    #         SELLABLE_3 = sellable_quantity(SPOT_SYMBOL, (SPOT_QUANTITY * tp3_size))
    #         print(f"Sellable qty_3 = {SELLABLE_3}")
    #
    #         def s_sellable_stop_loss(SPOT_SYMBOL, SHORT_STOP_LOSS_BP):
    #             data_from_api = client.get_exchange_info()
    #             symbol_info = next(filter(lambda x: x['symbol'] == SPOT_SYMBOL, data_from_api['symbols']))
    #             price_filters = next(filter(lambda x: x['filterType'] == 'PRICE_FILTER', symbol_info['filters']))
    #             tick_size = price_filters["tickSize"]
    #             num = Decimal(tick_size)
    #             price_precision = int(len(str(num.normalize())) - 2)
    #             price = round(SHORT_STOP_LOSS_BP, price_precision)
    #             return price
    #
    #         SHORT_STOP_LOSS = entry_price * stop_loss_percentage
    #         print(f"SHORT STOP LOSS = {SHORT_STOP_LOSS}")
    #
    #         SHORT_TAKE_PROFIT = entry_price * take_profit_percentage
    #         print((f"SHORT TAKE PROFIT = {SHORT_TAKE_PROFIT}"))
    #         SHORT_TAKE_PROFIT_1 = entry_price * tp1_percent
    #         print((f"SHORT TAKE PROFIT_1 = {SHORT_TAKE_PROFIT_1}"))
    #         SHORT_TAKE_PROFIT_2 = entry_price * tp2_percent
    #         print((f"SHORT TAKE PROFIT_2 = {SHORT_TAKE_PROFIT_2}"))
    #         SHORT_TAKE_PROFIT_3 = entry_price * tp3_percent
    #         print((f"SHORT TAKE PROFIT_3 = {SHORT_TAKE_PROFIT_3}"))
    #
    #         def s_sellable_take_profit(SPOT_SYMBOL, TAKE_PROFIT_PRICE_BP):
    #             data_from_api = client.get_exchange_info()
    #             symbol_info = next(filter(lambda x: x['symbol'] == SPOT_SYMBOL, data_from_api['symbols']))
    #             price_filters = next(filter(lambda x: x['filterType'] == 'PRICE_FILTER', symbol_info['filters']))
    #             tick_size = price_filters["tickSize"]
    #             num = Decimal(tick_size)
    #             price_precision = int(len(str(num.normalize())) - 2)
    #             price = round(TAKE_PROFIT_PRICE_BP, price_precision)
    #             return price
    #
    #         STOP_LOSS_PRICE_BP = entry_price - SHORT_STOP_LOSS
    #         STOP_LOSS_PRICE_FINAL = s_sellable_stop_loss(SPOT_SYMBOL, STOP_LOSS_PRICE_BP)
    #         print(f"Stop loss price final = {STOP_LOSS_PRICE_FINAL}")
    #         TAKE_PROFIT_PRICE_BP = entry_price + SHORT_TAKE_PROFIT
    #         TAKE_PROFIT_PRICE_FINAL = s_sellable_take_profit(SPOT_SYMBOL, TAKE_PROFIT_PRICE_BP)
    #         print(f"Take profit price final = {TAKE_PROFIT_PRICE_FINAL}")
    #         TAKE_PROFIT_PRICE_BP_1 = entry_price + SHORT_TAKE_PROFIT_1
    #         TAKE_PROFIT_PRICE_BP_2 = entry_price + SHORT_TAKE_PROFIT_2
    #         TAKE_PROFIT_PRICE_BP_3 = entry_price + SHORT_TAKE_PROFIT_3
    #         TAKE_PROFIT_PRICE_FINAL_1 = s_sellable_take_profit(SPOT_SYMBOL, TAKE_PROFIT_PRICE_BP_1)
    #         TAKE_PROFIT_PRICE_FINAL_2 = s_sellable_take_profit(SPOT_SYMBOL, TAKE_PROFIT_PRICE_BP_2)
    #         TAKE_PROFIT_PRICE_FINAL_3 = s_sellable_take_profit(SPOT_SYMBOL, TAKE_PROFIT_PRICE_BP_3)
    #         print(f"Take profit price final_1 = {TAKE_PROFIT_PRICE_FINAL_1}")
    #         print(f"Take profit price final_2 = {TAKE_PROFIT_PRICE_FINAL_2}")
    #         print(f"Take profit price final_3 = {TAKE_PROFIT_PRICE_FINAL_3}")
    #
    #         exit_order_type_number = alert_response["exit_order_type"]
    #         if exit_order_type_number == 1:
    #             exit_order_type = "Limit"
    #         else:
    #             exit_order_type = "Market"
    #
    #         def execute_market_oco_order():
    #             market_oco_order = client.order_oco_sell(symbol=SPOT_SYMBOL, quantity=SELLABLE_QTY,
    #                                                      price=TAKE_PROFIT_PRICE_FINAL, stopPrice=STOP_LOSS_PRICE_FINAL)
    #             print(f"market oco order = {market_oco_order}")
    #             for item in market_oco_order["orderReports"]:
    #                 market_oco_order_ID = item["orderId"]
    #                 print(market_oco_order_ID)
    #                 cursor.execute(
    #                     f"""INSERT INTO id_list (order_id, entry_price) VALUES ({market_oco_order_ID},{entry_price})""")
    #                 conn.commit()
    #                 print("Records inserted")
    #
    #         def execute_market_oco_order_1():
    #             market_oco_order_1 = client.order_oco_sell(symbol=SPOT_SYMBOL, quantity=SELLABLE_1,
    #                                                        price=TAKE_PROFIT_PRICE_FINAL_1,
    #                                                        stopPrice=STOP_LOSS_PRICE_FINAL)
    #             for item in market_oco_order_1["orderReports"]:
    #                 market_oco_order_1_ID = item["orderId"]
    #                 print(market_oco_order_1_ID)
    #                 cursor.execute(
    #                     f"""INSERT INTO id_list (order_id, entry_price) VALUES ({market_oco_order_1_ID},{entry_price})""")
    #                 conn.commit()
    #                 print("Records inserted")
    #
    #         def execute_market_oco_order_2():
    #             market_oco_order_2 = client.order_oco_sell(symbol=SPOT_SYMBOL, quantity=SELLABLE_2,
    #                                                        price=TAKE_PROFIT_PRICE_FINAL_2,
    #                                                        stopPrice=STOP_LOSS_PRICE_FINAL)
    #             for item in market_oco_order_2["orderReports"]:
    #                 market_oco_order_2_ID = item["orderId"]
    #                 print(market_oco_order_2_ID)
    #                 cursor.execute(
    #                     f"""INSERT INTO id_list (order_id, entry_price) VALUES ({market_oco_order_2_ID},{entry_price})""")
    #                 conn.commit()
    #                 print("Records inserted")
    #
    #         def execute_market_oco_order_3():
    #             market_oco_order_3 = client.order_oco_sell(symbol=SPOT_SYMBOL, quantity=SELLABLE_3,
    #                                                        price=TAKE_PROFIT_PRICE_FINAL_3,
    #                                                        stopPrice=STOP_LOSS_PRICE_FINAL)
    #             for item in market_oco_order_3["orderReports"]:
    #                 market_oco_order_3_ID = item["orderId"]
    #                 print(market_oco_order_3_ID)
    #                 cursor.execute(
    #                     f"""INSERT INTO id_list (order_id, entry_price) VALUES ({market_oco_order_3_ID},{entry_price})""")
    #                 conn.commit()
    #                 print("Records inserted")
    #
    #         ####################################################################################################################################################################################################
    #         def execute_market_stop_loss_order():
    #             market_stop_loss_order = client.create_order(symbol=SPOT_SYMBOL, side="SELL", type="STOP_LOSS",
    #                                                          quantity=SELLABLE_QTY, stopPrice=STOP_LOSS_PRICE_FINAL)
    #             market_stop_loss_order_ID = market_stop_loss_order["orderId"]
    #             print(market_stop_loss_order_ID)
    #             cursor.execute(
    #                 f"""INSERT INTO id_list (order_id, entry_price) VALUES ({market_stop_loss_order_ID},{entry_price})""")
    #             conn.commit()
    #             print("Records inserted")
    #
    #         def execute_market_take_profit_order():
    #             market_take_profit_order = client.create_order(symbol=SPOT_SYMBOL, side="SELL", type="TAKE_PROFIT",
    #                                                            quantity=SELLABLE_QTY, stopPrice=TAKE_PROFIT_PRICE_FINAL)
    #             market_take_profit_order_ID = market_take_profit_order["orderId"]
    #             print(market_take_profit_order_ID)
    #             cursor.execute(
    #                 f"""INSERT INTO id_list (order_id, entry_price) VALUES ({market_take_profit_order_ID},{entry_price})""")
    #             conn.commit()
    #             print("Records inserted")
    #
    #         def execute_market_tp_order_1():
    #             market_take_profit_order_1 = client.create_order(symbol=SPOT_SYMBOL, side="SELL", type="TAKE_PROFIT",
    #                                                              quantity=SELLABLE_1,
    #                                                              stopPrice=TAKE_PROFIT_PRICE_FINAL_1)
    #             market_take_profit_order_1_ID = market_take_profit_order_1["orderId"]
    #             print(market_take_profit_order_1_ID)
    #             cursor.execute(
    #                 f"""INSERT INTO id_list (order_id, entry_price) VALUES ({market_take_profit_order_1_ID},{entry_price})""")
    #             conn.commit()
    #             print("Records inserted")
    #
    #         def execute_market_tp_order_2():
    #             market_take_profit_order_2 = client.create_order(symbol=SPOT_SYMBOL, side="SELL", type="TAKE_PROFIT",
    #                                                              quantity=SELLABLE_2,
    #                                                              stopPrice=TAKE_PROFIT_PRICE_FINAL_2)
    #             market_take_profit_order_2_ID = market_take_profit_order_2["orderId"]
    #             print(market_take_profit_order_2_ID)
    #             cursor.execute(
    #                 f"""INSERT INTO id_list (order_id, entry_price) VALUES ({market_take_profit_order_2_ID},{entry_price})""")
    #             conn.commit()
    #             print("Records inserted")
    #
    #         def execute_market_tp_order_3():
    #             market_take_profit_order_3 = client.create_order(symbol=SPOT_SYMBOL, side="SELL", type="TAKE_PROFIT",
    #                                                              quantity=SELLABLE_3,
    #                                                              stopPrice=TAKE_PROFIT_PRICE_FINAL_3)
    #             market_take_profit_order_3_ID = market_take_profit_order_3["orderId"]
    #             print(market_take_profit_order_3_ID)
    #             cursor.execute(
    #                 f"""INSERT INTO id_list (order_id, entry_price) VALUES ({market_take_profit_order_3_ID},{entry_price})""")
    #             conn.commit()
    #             print("Records inserted")
    #
    #         ###########################################################################################################################################################################################
    #
    #         def execute_limit_oco_order():
    #             limit_oco_order = client.order_oco_sell(symbol=SPOT_SYMBOL, quantity=SELLABLE_QTY,
    #                                                     price=TAKE_PROFIT_PRICE_FINAL, stopPrice=STOP_LOSS_PRICE_FINAL,
    #                                                     stopLimitPrice=STOP_LOSS_PRICE_FINAL,
    #                                                     stopLimitTimeInForce="GTC")
    #             print(f"limit oco order = {limit_oco_order}")
    #             for item in limit_oco_order["orderReports"]:
    #                 limit_oco_order_ID = item["orderId"]
    #                 print(limit_oco_order_ID)
    #                 cursor.execute(
    #                     f"""INSERT INTO id_list (order_id, entry_price) VALUES ({limit_oco_order_ID},{entry_price})""")
    #                 conn.commit()
    #                 print("Records inserted")
    #
    #         def execute_limit_oco_order_1():
    #             limit_oco_order_1 = client.order_oco_sell(symbol=SPOT_SYMBOL, quantity=SELLABLE_1,
    #                                                       price=TAKE_PROFIT_PRICE_FINAL_1,
    #                                                       stopPrice=STOP_LOSS_PRICE_FINAL,
    #                                                       stopLimitPrice=STOP_LOSS_PRICE_FINAL,
    #                                                       stopLimitTimeInForce="GTC")
    #             print(f"limit oco order_1 = {limit_oco_order_1}")
    #             for item in limit_oco_order_1["orderReports"]:
    #                 limit_oco_order_1_ID = item["orderId"]
    #                 print(limit_oco_order_1_ID)
    #                 cursor.execute(
    #                     f"""INSERT INTO id_list (order_id, entry_price) VALUES ({limit_oco_order_1},{entry_price})""")
    #                 conn.commit()
    #                 print("Records inserted")
    #
    #         def execute_limit_oco_order_2():
    #             limit_oco_order_2 = client.order_oco_sell(symbol=SPOT_SYMBOL, quantity=SELLABLE_2,
    #                                                       price=TAKE_PROFIT_PRICE_FINAL_2,
    #                                                       stopPrice=STOP_LOSS_PRICE_FINAL,
    #                                                       stopLimitPrice=STOP_LOSS_PRICE_FINAL,
    #                                                       stopLimitTimeInForce="GTC")
    #             print(f"limit oco order_2 = {limit_oco_order_2}")
    #             for item in limit_oco_order_2["orderReports"]:
    #                 limit_oco_order_2_ID = item["orderId"]
    #                 print(limit_oco_order_2_ID)
    #                 cursor.execute(
    #                     f"""INSERT INTO id_list (order_id, entry_price) VALUES ({limit_oco_order_2},{entry_price})""")
    #                 conn.commit()
    #                 print("Records inserted")
    #
    #         def execute_limit_oco_order_3():
    #             limit_oco_order_3 = client.order_oco_sell(symbol=SPOT_SYMBOL, quantity=SELLABLE_3,
    #                                                       price=TAKE_PROFIT_PRICE_FINAL_3,
    #                                                       stopPrice=STOP_LOSS_PRICE_FINAL,
    #                                                       stopLimitPrice=STOP_LOSS_PRICE_FINAL,
    #                                                       stopLimitTimeInForce="GTC")
    #             print(f"limit oco order_3 = {limit_oco_order_3}")
    #             for item in limit_oco_order_3["orderReports"]:
    #                 limit_oco_order_3_ID = item["orderId"]
    #                 print(limit_oco_order_3_ID)
    #                 cursor.execute(
    #                     f"""INSERT INTO id_list (order_id, entry_price) VALUES ({limit_oco_order_3_ID},{entry_price})""")
    #                 conn.commit()
    #                 print("Records inserted")
    #
    #         def execute_limit_stop_loss_order():
    #             limit_stop_loss_order = client.create_order(symbol=SPOT_SYMBOL, side="SELL", type="STOP_LOSS_LIMIT",
    #                                                         quantity=SELLABLE_QTY, price=STOP_LOSS_PRICE_FINAL,
    #                                                         stopPrice=STOP_LOSS_PRICE_FINAL, timeInForce="GTC")
    #             print(f"limit stop loss order = {limit_stop_loss_order}")
    #             limit_stop_loss_order_ID = limit_stop_loss_order["orderId"]
    #             print(limit_stop_loss_order_ID)
    #             cursor.execute(
    #                 f"""INSERT INTO id_list (order_id, entry_price) VALUES ({limit_stop_loss_order_ID},{entry_price})""")
    #             conn.commit()
    #             print("Records inserted")
    #
    #         def execute_limit_take_profit_order():
    #             limit_take_proft_order = client.create_order(symbol=SPOT_SYMBOL, side="SELL", type="TAKE_PROFIT_LIMIT",
    #                                                          quantity=SELLABLE_QTY, price=TAKE_PROFIT_PRICE_FINAL,
    #                                                          stopPrice=TAKE_PROFIT_PRICE_FINAL, timeInForce="GTC")
    #             print(f"limit take profit order = {limit_take_proft_order}")
    #             limit_take_proft_order_ID = limit_take_proft_order["orderId"]
    #             print(limit_take_proft_order_ID)
    #             cursor.execute(
    #                 f"""INSERT INTO id_list (order_id, entry_price) VALUES ({limit_take_proft_order_ID},{entry_price})""")
    #             conn.commit()
    #             print("Records inserted")
    #
    #         def execute_limit_tp_order_1():
    #             limit_take_proft_order_1 = client.create_order(symbol=SPOT_SYMBOL, side="SELL",
    #                                                            type="TAKE_PROFIT_LIMIT", quantity=SELLABLE_1,
    #                                                            price=TAKE_PROFIT_PRICE_FINAL_1,
    #                                                            stopPrice=TAKE_PROFIT_PRICE_FINAL_1, timeInForce="GTC")
    #             print(f"limit take profit order_1 = {limit_take_proft_order_1}")
    #             limit_take_proft_order_1_ID = limit_take_proft_order_1["orderId"]
    #             print(limit_take_proft_order_1_ID)
    #             cursor.execute(
    #                 f"""INSERT INTO id_list (order_id, entry_price) VALUES ({limit_take_proft_order_1_ID},{entry_price})""")
    #             conn.commit()
    #             print("Records inserted")
    #
    #         def execute_limit_tp_order_2():
    #             limit_take_proft_order_2 = client.create_order(symbol=SPOT_SYMBOL, side="SELL",
    #                                                            type="TAKE_PROFIT_LIMIT", quantity=SELLABLE_2,
    #                                                            price=TAKE_PROFIT_PRICE_FINAL_2,
    #                                                            stopPrice=TAKE_PROFIT_PRICE_FINAL_2, timeInForce="GTC")
    #             print(f"limit take profit order_2 = {limit_take_proft_order_2}")
    #             limit_take_proft_order_2_ID = limit_take_proft_order_2["orderId"]
    #             print(limit_take_proft_order_2_ID)
    #             cursor.execute(
    #                 f"""INSERT INTO id_list (order_id, entry_price) VALUES ({limit_take_proft_order_2_ID},{entry_price})""")
    #             conn.commit()
    #             print("Records inserted")
    #
    #         def execute_limit_tp_order_3():
    #             limit_take_proft_order_3 = client.create_order(symbol=SPOT_SYMBOL, side="SELL",
    #                                                            type="TAKE_PROFIT_LIMIT", quantity=SELLABLE_3,
    #                                                            price=TAKE_PROFIT_PRICE_FINAL_3,
    #                                                            stopPrice=TAKE_PROFIT_PRICE_FINAL_3, timeInForce="GTC")
    #             print(f"limit take profit order_3 = {limit_take_proft_order_3}")
    #             limit_take_proft_order_3_ID = limit_take_proft_order_3["orderId"]
    #             print(limit_take_proft_order_3_ID)
    #             cursor.execute(
    #                 f"""INSERT INTO id_list (order_id, entry_price) VALUES ({limit_take_proft_order_3_ID},{entry_price})""")
    #             conn.commit()
    #             print("Records inserted")
    #
    #         if SHORT_STOP_LOSS > 0 and SHORT_TAKE_PROFIT > 0 and exit_order_type == "Market":
    #             if tp1_percent == "" or tp1_percent == 0:
    #                 execute_market_oco_order()
    #             elif tp1_percent > 0:
    #                 execute_market_oco_order_1()
    #                 if tp2_percent > 0:
    #                     execute_market_oco_order_2()
    #                 if tp3_percent > 0:
    #                     execute_market_oco_order_3()
    #
    #         if SHORT_STOP_LOSS > 0 and SHORT_TAKE_PROFIT > 0 and exit_order_type == "Limit":
    #             if tp1_percent == "" or tp1_percent == 0:
    #                 execute_limit_oco_order()
    #             elif tp1_percent > 0:
    #                 execute_limit_oco_order_1()
    #                 if tp2_percent > 0:
    #                     execute_limit_oco_order_2()
    #                 if tp3_percent > 0:
    #                     execute_limit_oco_order_3()
    #
    #         if SHORT_STOP_LOSS > 0 and (
    #                 SHORT_TAKE_PROFIT == "" or SHORT_TAKE_PROFIT == 0) and exit_order_type == "Market":
    #             execute_market_stop_loss_order()
    #
    #         if SHORT_TAKE_PROFIT > 0 and (
    #                 SHORT_STOP_LOSS == "" or SHORT_STOP_LOSS == 0) and exit_order_type == "Market":
    #             if tp1_percent == "" or tp1_percent == 0:
    #                 execute_market_take_profit_order()
    #             elif tp1_percent > 0:
    #                 execute_market_tp_order_1()
    #                 if tp2_percent > 0:
    #                     execute_market_tp_order_2()
    #                 if tp3_percent > 0:
    #                     execute_market_tp_order_3()
    #
    #         if SHORT_STOP_LOSS > 0 and (
    #                 SHORT_TAKE_PROFIT == "" or SHORT_TAKE_PROFIT == 0) and exit_order_type == "Limit":
    #             execute_limit_stop_loss_order()
    #
    #         if SHORT_TAKE_PROFIT > 0 and (SHORT_STOP_LOSS == "" or SHORT_STOP_LOSS == 0) and exit_order_type == "Limit":
    #             if tp1_percent == "" or tp1_percent == 0:
    #                 execute_limit_take_profit_order()
    #             elif tp1_percent > 0:
    #                 execute_limit_tp_order_1()
    #                 if tp2_percent > 0:
    #                     execute_limit_tp_order_2()
    #                 if tp3_percent > 0:
    #                     execute_limit_tp_order_3()
    #
    # def execute_market_sell_spot_order():
    #     global SPOT_SYMBOL
    #     global SPOT_SIDE
    #     global SPOT_QUANTITY
    #     if sell_leverage_alert == 1:
    #         SPOT_SIDE = "SELL"
    #
    #         SPOT_SYMBOL = alert_response["coin_pair"]
    #         SPOT_TYPE_ENTRY = "MARKET"
    #         SPOT_QUANTITY = alert_response["qty"]
    #
    #         sell_order = client.create_order(symbol=SPOT_SYMBOL, side=SPOT_SIDE, type=SPOT_TYPE_ENTRY,
    #                                          quantity=SPOT_QUANTITY)
    #         print(f"sell order = {sell_order}")
    #         SELL_ORDER_SYMBOL = sell_order["symbol"]
    #         SELL_ORDER_ID = sell_order["orderId"]
    #         SELL_ORDER_QTY = float(sell_order["executedQty"])
    #         SELL_ORDER_PRICE = float(sell_order["cummulativeQuoteQty"]) / float(sell_order["executedQty"])
    #         SELL_ORDER_ACTION = sell_order["side"]
    #         SELL_ORDER_TYPE = sell_order["type"]
    #         sell_order_executed_time = datetime.now()
    #
    #         cursor.execute("select qty from buy_orders where symbol = %s", [SELL_ORDER_SYMBOL])
    #         r_1 = cursor.fetchall()
    #         qty_results = r_1[0][0]
    #
    #         cursor.execute("select price from buy_orders where symbol = %s", [SELL_ORDER_SYMBOL])
    #         r_2 = cursor.fetchall()
    #         price_results = r_2[0][0]
    #
    #         EXISTING_AVG_PRICE = float(price_results) / float(qty_results)
    #         SELL_PNL = round((SELL_ORDER_PRICE - EXISTING_AVG_PRICE), 2)
    #         sell_per = (SELL_PNL / EXISTING_AVG_PRICE) * 100
    #         SELL_PNL_PERCENTAGE = str((round(sell_per, 2))) + "%"
    #
    #         qty_to_be_updated = float(qty_results) - SELL_ORDER_QTY
    #         print(f"qty up - {qty_to_be_updated}")
    #
    #         price_to_be_updated = float(price_results) - float(sell_order["cummulativeQuoteQty"])
    #         print(f"price up - {price_to_be_updated}")
    #
    #         cursor.execute("update buy_orders set qty = %s, price = %s where symbol = %s",
    #                        [qty_to_be_updated, price_to_be_updated, SELL_ORDER_SYMBOL])
    #         conn.commit()
    #         print("Updated")
    #
    #         cursor.execute("insert into trade_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty, pnl, percentage) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)",[sell_order_executed_time, SELL_ORDER_SYMBOL, SELL_ORDER_ID, SELL_ORDER_ACTION,SELL_ORDER_TYPE, SELL_ORDER_PRICE, SELL_ORDER_QTY, SELL_PNL, SELL_PNL_PERCENTAGE])
    #         conn.commit()
    #
    # if buy_leverage_alert == 1 and entry_order_type == "Market":
    #     try:
    #         execute_market_buy_spot_order()
    #     except Exception as e:
    #         error_occured = f"{e}"
    #         error_occured_time = datetime.now()
    #
    #         cursor.execute("insert into error_log(symbol, order_action, entry_order_type, exit_order_type, quantity, occured_time, error_description) values (%s, %s, %s, %s, %s, %s, %s)",[SPOT_SYMBOL, SPOT_SIDE, JSON_ENTRY, JSON_EXIT, SPOT_QUANTITY, error_occured_time,error_occured])
    #         conn.commit()
    #
    # if sell_leverage_alert == 1 and entry_order_type == "Market":
    #     try:
    #         execute_market_sell_spot_order()
    #     except Exception as e:
    #         error_occured = f"{e}"
    #         print(error_occured)
    #         error_occured_time = datetime.now()
    #
    #         cursor.execute("insert into error_log(occured_time, symbol, order_action, entry_order_type, exit_order_type, quantity, error_description) values (%s, %s, %s, %s, %s, %s, %s)",[error_occured_time, SPOT_SYMBOL, SPOT_SIDE, JSON_ENTRY, JSON_EXIT, SPOT_QUANTITY,error_occured])
    #         conn.commit()

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=80)

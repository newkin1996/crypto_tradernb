from binance.client import Client
import requests
from binance.enums import *
import math
from decimal import Decimal
import psycopg2 # on ubuntu, sudo apt-get install libpq-dev, sudo pip install psycopg2/sudo pip install psycopg2-binary
from psycopg2 import sql
from datetime import datetime
import time
import threading

api_key = "oH9O1uFYYkbm81rj2FPCbBEzaqUCWDs1vudZ4OoD94UYrTJsNQc1pUG9yR6baFjX"
api_secret = "7tGyRDG97EjH6Zk0re04Ln9mjodknCifA9YbCOTEVCTBCXgkAuv9ZksNmXaXFiON"

client = Client(api_key, api_secret)

#establishing the connection
conn = psycopg2.connect(database="gpu", user='postgres', password='postgres', host='127.0.0.1', port= '5433')
#Creating a cursor object using the cursor() method
cursor = conn.cursor()

#Executing an MYSQL function using the execute() method
cursor.execute("select version()")

# Fetch a single row using fetchone() method.
data = cursor.fetchone()
print("Connection established to: ",data)


alert_response = {"exchange":"Binance",
 "base_coin":"USDT",
 "coin_pair": "XVSUSDT",
 "entry_type":"Market",
 "exit_type":"Limit",
 "long_leverage": 2,
 "short_leverage": 2,
 "margin_mode":"Isolated",
 "qty_type": "Fixed",
 "qty": 21,
 "trade_type": "Spot",
 "long_stop_loss_percent":0,
 "long_take_profit_percent":0,
 "short_stop_loss_percent":0,
 "short_take_profit_percent":0,
 "enable_multi_tp":"No",
 "tp_1_pos_size":0,
 "tp1_percent":0,
 "tp_2_pos_size":0,
 "tp2_percent":0,
 "tp_3_pos_size":0,
 "tp3_percent":0,
 "stop_bot_below_balance":1,
 "order_time_out":120,
 "position_type": "Exit_short"}

try:
    try:
        req_exchange = alert_response["exchange"]
    except Exception as e:
        print(e)
        error_occured_time = datetime.now()
        error_occured = "Invalid/Empty exchange type"
        cursor.execute("insert into error_log(occured_time, error_description) values (%s, %s)",[error_occured_time, error_occured])
        conn.commit()

    try:
        req_base_coin = alert_response["base_coin"]
    except Exception as e:
        print(e)
        error_occured_time = datetime.now()
        error_occured = "Invalid/Empty base coin"
        cursor.execute("insert into error_log(occured_time, error_description) values (%s, %s)",
                       [error_occured_time, error_occured])
        conn.commit()

    try:
        req_coin_pair = alert_response["coin_pair"]
    except Exception as e:
        print(e)
        error_occured_time = datetime.now()
        error_occured = "Invalid/Empty coin pair"
        cursor.execute("insert into error_log(occured_time, error_description) values (%s, %s)",
                       [error_occured_time, error_occured])
        conn.commit()

    req_entry_type = alert_response["entry_type"].upper()
    req_exit_type = alert_response["exit_type"].upper()
    req_margin_mode = alert_response["margin_mode"]
    req_long_leverage = float(alert_response["long_leverage"])
    req_short_leverage = float(alert_response["short_leverage"])

    try:
        req_qty_type = alert_response["qty_type"]
    except Exception as e:
        print(e)
        error_occured_time = datetime.now()
        error_occured = "Invalid/Empty qty type"
        cursor.execute("insert into error_log(occured_time, error_description) values (%s, %s)",
                       [error_occured_time, error_occured])
        conn.commit()

    try:
        req_qty = float(alert_response["qty"])
    except Exception as e:
        print(e)
        error_occured_time = datetime.now()
        error_occured = "Invalid/Empty qty"
        cursor.execute("insert into error_log(occured_time, error_description) values (%s, %s)",
                       [error_occured_time, error_occured])
        conn.commit()

    try:
        req_trade_type = alert_response["trade_type"]
    except Exception as e:
        print(e)
        error_occured_time = datetime.now()
        error_occured = "Invalid/Empty trade type"
        cursor.execute("insert into error_log(occured_time, error_description) values (%s, %s)",
                       [error_occured_time, error_occured])
        conn.commit()

    req_long_leverage = alert_response["long_leverage"]
    req_short_leverage = alert_response["short_leverage"]

    req_long_stop_loss_percent = (float(alert_response["long_stop_loss_percent"]))/100
    req_long_take_profit_percent = (float(alert_response["long_take_profit_percent"]))/100
    req_short_stop_loss_percent = (float(alert_response["short_stop_loss_percent"]))/100
    req_short_take_profit_percent = (float(alert_response["short_take_profit_percent"]))/100
    print(f"req short tp = {req_short_take_profit_percent}")
    req_multi_tp = alert_response["enable_multi_tp"]

    req_tp1_qty_size = (float(alert_response["tp_1_pos_size"]))/100
    req_tp2_qty_size = (float(alert_response["tp_2_pos_size"]))/100
    req_tp3_qty_size = (float(alert_response["tp_3_pos_size"]))/100

    req_tp1_percent = (float(alert_response["tp1_percent"]))/100
    req_tp2_percent = (float(alert_response["tp2_percent"]))/100
    req_tp3_percent = (float(alert_response["tp3_percent"]))/100

    req_stop_bot_balance = float(alert_response["stop_bot_below_balance"])
    req_order_time_out = float(alert_response["order_time_out"])

    try:
        req_position_type = alert_response["position_type"]
    except Exception as e:
        print(e)
        error_occured_time = datetime.now()
        error_occured = "Invalid/Empty position type"
        cursor.execute("insert into error_log(occured_time, error_description) values (%s, %s)",
                       [error_occured_time, error_occured])
        conn.commit()
except Exception as e:
    print(e)
    error_occured_time = datetime.now()
    error_occured = "Error in parsing json alert"
    cursor.execute("insert into error_log(occured_time, error_description) values (%s, %s)",
                   [error_occured_time, error_occured])
    conn.commit()

try:
    if req_trade_type == "Spot":

        SPOT_SYMBOL = req_coin_pair
        SPOT_ENTRY = req_entry_type
        SPOT_EXIT = req_exit_type

        # Check usdt balance in spot wallet
        def check_base_coin_balance():
            balances = client.get_account()
            for _balance in balances["balances"]:
                asset = _balance["asset"]
                if float(_balance["free"]) != 0.0 or float(_balance["locked"]) != 0.0:
                    if asset == req_base_coin:
                        base_coin_bal = float(_balance["free"]) + float(_balance["locked"])
                        break
                else:
                    base_coin_bal = 0
            return base_coin_bal


        def calculate_buy_qty_with_precision(SPOT_SYMBOL, qty_in_base_coin):
            prices = client.get_all_tickers()
            for ticker in prices:
                if ticker["symbol"] == SPOT_SYMBOL:
                    current_market_price = float(ticker["price"])
                    break
            tradeable_qty = qty_in_base_coin / current_market_price
            info = client.get_symbol_info(SPOT_SYMBOL)
            for x in info["filters"]:
                if x["filterType"] == "LOT_SIZE":
                    stepSize = float(x["stepSize"])
                    print(f"step size = {stepSize}")

            truncate_num = math.log10(1 / stepSize)
            BUY_QUANTITY = math.floor((tradeable_qty) * 10 ** truncate_num) / 10 ** truncate_num
            return BUY_QUANTITY

        def calculate_sell_qty_with_precision(SPOT_SYMBOL, buy_qty):
            info = client.get_symbol_info(SPOT_SYMBOL)
            for x in info["filters"]:
                if x["filterType"] == "LOT_SIZE":
                    stepSize = float(x["stepSize"])
                    print(f"step size = {stepSize}")

            truncate_num = math.log10(1 / stepSize)
            SELL_QUANTITY = math.floor((buy_qty) * 10 ** truncate_num) / 10 ** truncate_num
            return SELL_QUANTITY

        def trunc_calculate_sell_qty_with_precision(SPOT_SYMBOL, buy_qty):
            sellable_qty_after_fees = float(buy_qty) * 0.998
            info = client.get_symbol_info(SPOT_SYMBOL)
            for x in info["filters"]:
                if x["filterType"] == "LOT_SIZE":
                    stepSize = float(x["stepSize"])
                    print(f"step size = {stepSize}")

            truncate_num = math.log10(1 / stepSize)
            SELL_QUANTITY = math.floor((sellable_qty_after_fees) * 10 ** truncate_num) / 10 ** truncate_num
            return SELL_QUANTITY


        def cal_price_with_precision(SPOT_SYMBOL, input_price):
            data_from_api = client.get_exchange_info()
            symbol_info = next(filter(lambda x: x['symbol'] == SPOT_SYMBOL, data_from_api['symbols']))
            price_filters = next(filter(lambda x: x['filterType'] == 'PRICE_FILTER', symbol_info['filters']))
            tick_size = price_filters["tickSize"]
            num = Decimal(tick_size)
            price_precision = int(len(str(num.normalize())) - 2)
            price = round(input_price, price_precision)
            return price

        def get_current_open_orders(SPOT_SYMBOL):
            oo_id_list = []
            current_open_orders = client.get_open_orders()

            for oo in current_open_orders:
                if oo["symbol"] == SPOT_SYMBOL:
                    oo_id_list.append(oo["orderId"])

            return oo_id_list

        if req_qty_type == "Percentage":
            current_bal = check_base_coin_balance()
            qty_in_base_coin = current_bal * req_qty
        elif req_qty_type == "Fixed":
            qty_in_base_coin = req_qty

        def execute_limit_oco_order(SPOT_SIDE,req_position_type,BUY_ORDER_ID, SPOT_SYMBOL, SPOT_SELL_QUANTITY, TAKE_PROFIT_PRICE_FINAL,STOP_LOSS_PRICE_FINAL, SPOT_ENTRY,req_multi_tp,req_qty_size,req_order_time_out):
            SPOT_EXIT = "LIMIT"
            print(SPOT_SIDE)

            # STOP_LOSS_PRICE_FINAL_S = cal_price_with_precision(SPOT_SYMBOL=SPOT_SYMBOL,input_price=(STOP_LOSS_PRICE_FINAL * 0.9999))
            STOP_LOSS_PRICE_FINAL_B = cal_price_with_precision(SPOT_SYMBOL=SPOT_SYMBOL,
                                                               input_price=(STOP_LOSS_PRICE_FINAL * 1.0009))

            try:
                if SPOT_SIDE == "SELL":
                    limit_oco_order = client.order_oco_sell(symbol=SPOT_SYMBOL, quantity=SPOT_SELL_QUANTITY,
                                                            price=TAKE_PROFIT_PRICE_FINAL, stopPrice=STOP_LOSS_PRICE_FINAL,
                                                            stopLimitPrice=STOP_LOSS_PRICE_FINAL, stopLimitTimeInForce="GTC")

                    for o in limit_oco_order["orders"]:
                        o_id_for_table = o["orderId"]
                        cursor.execute("select entry_price from long_entry where symbol = %s", [SPOT_SYMBOL])
                        r_3 = cursor.fetchall()
                        price_results = r_3[0][0]
                        p_for_table = float(price_results)

                        cursor.execute("insert into s_id_list(order_id, entry_price) values (%s, %s)",
                                       [o_id_for_table, p_for_table])
                        conn.commit()

                    print(f"limit oco order = {limit_oco_order}")
                if SPOT_SIDE == "BUY":
                    limit_oco_order = client.order_oco_buy(symbol=SPOT_SYMBOL, quantity=SPOT_SELL_QUANTITY,
                                                            price=TAKE_PROFIT_PRICE_FINAL, stopPrice=STOP_LOSS_PRICE_FINAL_B,
                                                            stopLimitPrice=STOP_LOSS_PRICE_FINAL, stopLimitTimeInForce="GTC")
                    print(f"limit oco order = {limit_oco_order}")

                    for o in limit_oco_order["orders"]:
                        o_id_for_table = o["orderId"]
                        cursor.execute("select entry_price from short_entry where symbol = %s", [SPOT_SYMBOL])
                        r_3 = cursor.fetchall()
                        price_results = r_3[0][0]
                        p_for_table = float(price_results)

                        cursor.execute("insert into s_id_list(order_id, entry_price) values (%s, %s)",
                                       [o_id_for_table, p_for_table])
                        conn.commit()

            except Exception as e:

                error_occured = f"{e}"
                print(error_occured)

                error_occured_time = datetime.now()

                cursor.execute(
                    "insert into error_log(symbol, order_action, entry_order_type, exit_order_type, quantity, occured_time, error_description) values (%s, %s, %s, %s, %s, %s, %s)",
                    [SPOT_SYMBOL, SPOT_SIDE, SPOT_ENTRY, SPOT_EXIT, SPOT_SELL_QUANTITY, error_occured_time, error_occured])
                conn.commit()

                error = "APIError(code=-2010): Account has insufficient balance for requested action."
                if str(e) == error and req_position_type == "Exit_long":
                    no_qty = True
                    oo_list = get_current_open_orders(SPOT_SYMBOL)

                    while no_qty == True:
                        for item in oo_list:
                            client.cancel_order(symbol=SPOT_SYMBOL, orderId=item)
                            try:
                                if SPOT_SIDE == "SELL":
                                    limit_oco_order = client.order_oco_sell(symbol=SPOT_SYMBOL, quantity=SPOT_SELL_QUANTITY,
                                                                            price=TAKE_PROFIT_PRICE_FINAL,
                                                                            stopPrice=STOP_LOSS_PRICE_FINAL,
                                                                            stopLimitPrice=STOP_LOSS_PRICE_FINAL,
                                                                            stopLimitTimeInForce="GTC")
                                    print(f"limit oco order = {limit_oco_order}")

                                    for o in limit_oco_order["orders"]:
                                        o_id_for_table = o["orderId"]
                                        cursor.execute("select entry_price from long_entry where symbol = %s",
                                                       [SPOT_SYMBOL])
                                        r_3 = cursor.fetchall()
                                        price_results = r_3[0][0]
                                        p_for_table = float(price_results)

                                        cursor.execute("insert into s_id_list(order_id, entry_price) values (%s, %s)",
                                                       [o_id_for_table, p_for_table])
                                        conn.commit()

                                if SPOT_SIDE == "BUY":
                                    limit_oco_order = client.order_oco_buy(symbol=SPOT_SYMBOL, quantity=SPOT_SELL_QUANTITY,
                                                                           price=TAKE_PROFIT_PRICE_FINAL,
                                                                           stopPrice=STOP_LOSS_PRICE_FINAL_B,
                                                                           stopLimitPrice=STOP_LOSS_PRICE_FINAL,
                                                                           stopLimitTimeInForce="GTC")
                                    print(f"limit oco order = {limit_oco_order}")

                                    for o in limit_oco_order["orders"]:
                                        o_id_for_table = o["orderId"]
                                        cursor.execute("select entry_price from short_entry where symbol = %s",
                                                       [SPOT_SYMBOL])
                                        r_3 = cursor.fetchall()
                                        price_results = r_3[0][0]
                                        p_for_table = float(price_results)

                                        cursor.execute("insert into s_id_list(order_id, entry_price) values (%s, %s)",
                                                       [o_id_for_table, p_for_table])
                                        conn.commit()

                                no_qty = False
                                break
                            except Exception as e:
                                print(e)
                                pass


            oco_order_ids = []

            for item in limit_oco_order["orderReports"]:
                limit_oco_order_ID = item["orderId"]
                oco_order_ids.append(limit_oco_order_ID)
                print(limit_oco_order_ID)

            print(oco_order_ids)

            def add_to_trade_oco():
                while True:
                    time.sleep(4)
                    try:
                        for order_id in oco_order_ids:
                            active_order = client.get_order(symbol=SPOT_SYMBOL, orderId=order_id)
                            active_order_status = active_order["status"]
                            if active_order_status == "FILLED":
                                print("Filled")
                                break
                        if active_order_status == "FILLED":
                            break
                    except Exception as e:
                        print(e)
                        pass
                if active_order_status == "FILLED":
                    oco_limit_sell_order = active_order
                    print(f"oco limit sell order = {oco_limit_sell_order}")
                else:
                    for order_id in oco_order_ids:
                        check_for_partial = client.get_order(symbol=SPOT_SYMBOL, orderId=order_id)
                        if check_for_partial["status"] == "PARTIALLY_FILLED":
                            oco_limit_sell_order = check_for_partial
                        check_for_cancel = client.get_order(symbol=SPOT_SYMBOL, orderId=order_id)
                        if check_for_cancel["status"] == "CANCELED" or check_for_cancel["status"] != "PARTIALLY_FILLED" or check_for_cancel["status"] != "FILLED":
                            print("Already cancelled")
                        else:
                            cancel_oco_order = client.cancel_order(symbol=SPOT_SYMBOL, orderId=order_id)
                        error_occured = "Order time limit reached! Pending open oco sell orders have been cancelled"
                        print(error_occured)
                        error_occured_time = datetime.now()
                        cursor.execute("insert into error_log(symbol, order_action, entry_order_type, exit_order_type, quantity, occured_time, error_description) values (%s, %s, %s, %s, %s, %s, %s)",[SPOT_SYMBOL, SPOT_SIDE, SPOT_ENTRY, SPOT_EXIT, SPOT_SELL_QUANTITY, error_occured_time, error_occured])
                        conn.commit()

                try:
                    OCO_SELL_ORDER_ID = oco_limit_sell_order["orderId"]
                    OCO_SELL_ORDER_SYMBOL = oco_limit_sell_order["symbol"]
                    OCO_SELL_ORDER_QTY = float(oco_limit_sell_order["executedQty"])
                    sell_cum_qty = float(oco_limit_sell_order["cummulativeQuoteQty"])
                    TOTAL_SELL_SPEND = (sell_cum_qty / 100) * 99.9
                    TOTAL_BUY_SPEND = float(oco_limit_sell_order["cummulativeQuoteQty"])
                    OCO_SELL_ORDER_PRICE = round((float(oco_limit_sell_order["cummulativeQuoteQty"]) / float(oco_limit_sell_order["executedQty"])),3)
                    OCO_SELL_ORDER_ACTION = oco_limit_sell_order["side"]
                    OCO_SELL_ORDER_TYPE = oco_limit_sell_order["type"]
                    sell_order_executed_time = datetime.now()

                    if req_position_type == "Enter_long":
                        cursor.execute("select total_spend from id_list where order_id = %s", [BUY_ORDER_ID])
                        r_2 = cursor.fetchall()
                        price_results = r_2[0][0]
                        total_buy_spend = float(price_results)
                        print(f"Total buy spend from DB= {total_buy_spend}")

                        if req_multi_tp == "No":
                            OCO_SELL_PNL = round((TOTAL_SELL_SPEND - total_buy_spend),2)
                            oco_sell_per = (OCO_SELL_PNL / total_buy_spend) * 100
                            OCO_SELL_PNL_PERCENTAGE = str((round(oco_sell_per, 2))) + "%"
                        if req_multi_tp == "Yes":
                            buy_spend_per = float(total_buy_spend)*float(req_qty_size)
                            OCO_SELL_PNL = round((TOTAL_SELL_SPEND - buy_spend_per), 2)
                            oco_sell_per = (OCO_SELL_PNL / buy_spend_per) * 100
                            OCO_SELL_PNL_PERCENTAGE = str((round(oco_sell_per, 2))) + "%"

                        cursor.execute(sql.SQL("insert into trade_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty, pnl, percentage) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"),[sell_order_executed_time, OCO_SELL_ORDER_SYMBOL, OCO_SELL_ORDER_ID, OCO_SELL_ORDER_ACTION,OCO_SELL_ORDER_TYPE, OCO_SELL_ORDER_PRICE, OCO_SELL_ORDER_QTY, OCO_SELL_PNL,OCO_SELL_PNL_PERCENTAGE])
                        conn.commit()

                    if req_position_type == "Exit_long":
                        cursor.execute("select qty from long_entry where symbol = %s", [SPOT_SYMBOL])
                        r_3 = cursor.fetchall()
                        price_results = r_3[0][0]
                        previous_long_entry_qty = float(price_results)
                        print(f"previous_long_entry_qty = {previous_long_entry_qty}")

                        cursor.execute("select total_spend from long_entry where symbol = %s", [SPOT_SYMBOL])
                        r_3 = cursor.fetchall()
                        price_results = r_3[0][0]
                        previous_long_entry_spend = float(price_results)
                        print(f"previous_long_entry_spend = {previous_long_entry_spend}")

                        proportional_buy_spend = (previous_long_entry_spend / previous_long_entry_qty) * OCO_SELL_ORDER_QTY
                        OCO_SELL_PNL = round((TOTAL_SELL_SPEND - proportional_buy_spend), 2)
                        oco_sell_per = (OCO_SELL_PNL / proportional_buy_spend) * 100
                        OCO_SELL_PNL_PERCENTAGE = str((round(oco_sell_per, 2))) + "%"

                        cursor.execute(sql.SQL("insert into trade_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty, pnl, percentage) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"),[sell_order_executed_time, OCO_SELL_ORDER_SYMBOL, OCO_SELL_ORDER_ID, OCO_SELL_ORDER_ACTION,OCO_SELL_ORDER_TYPE, OCO_SELL_ORDER_PRICE, OCO_SELL_ORDER_QTY, OCO_SELL_PNL,OCO_SELL_PNL_PERCENTAGE])
                        conn.commit()

                    if req_position_type == "Enter_short":

                        cursor.execute("select exists (select 1 from short_entry)")
                        r_1 = cursor.fetchall()
                        live_r = r_1[0][0]

                        if live_r == False:
                            cursor.execute(sql.SQL("insert into short_entry(order_id, entry_price, total_spend, symbol, qty) values (%s, %s, %s, %s, %s)"),
                                           [OCO_SELL_ORDER_ID, OCO_SELL_ORDER_PRICE, TOTAL_SELL_SPEND, OCO_SELL_ORDER_SYMBOL, OCO_SELL_ORDER_QTY])
                            conn.commit()
                        if live_r == True:
                            cursor.execute(
                                "update short_entry set order_id = %s, entry_price = %s, total_spend = %s, symbol = %s, qty = %s",
                                [OCO_SELL_ORDER_ID, OCO_SELL_ORDER_PRICE, TOTAL_SELL_SPEND, OCO_SELL_ORDER_SYMBOL, OCO_SELL_ORDER_QTY])
                            conn.commit()
                            print("Records inserted")

                        cursor.execute(sql.SQL("insert into trade_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty) values (%s, %s, %s, %s, %s, %s, %s)"),[sell_order_executed_time, OCO_SELL_ORDER_SYMBOL, OCO_SELL_ORDER_ID, OCO_SELL_ORDER_ACTION,OCO_SELL_ORDER_TYPE, OCO_SELL_ORDER_PRICE, OCO_SELL_ORDER_QTY])
                        conn.commit()

                    if req_position_type == "Exit_short":

                        cursor.execute("select total_spend from short_entry where symbol = %s", [SPOT_SYMBOL])
                        r_3 = cursor.fetchall()
                        price_results = r_3[0][0]
                        previous_short_entry_income = float(price_results)
                        print(f"previous_short_entry_price = {previous_short_entry_income}")

                        cursor.execute("select qty from short_entry where symbol = %s", [SPOT_SYMBOL])
                        r_3 = cursor.fetchall()
                        price_results = r_3[0][0]
                        previous_short_entry_qty = float(price_results)
                        print(f"previous_short_entry_price = {previous_short_entry_qty}")

                        actual_sell_income = (previous_short_entry_income / 100) * 99.9
                        proportional_sell_income = (actual_sell_income / previous_short_entry_qty) * OCO_SELL_ORDER_QTY
                        OCO_SELL_PNL = round((proportional_sell_income - TOTAL_BUY_SPEND), 2)
                        oco_sell_per = (OCO_SELL_PNL / proportional_sell_income) * 100
                        OCO_SELL_PNL_PERCENTAGE = str((round(oco_sell_per, 2))) + "%"

                        cursor.execute(sql.SQL(
                            "insert into trade_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty, pnl, percentage) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"),
                                       [sell_order_executed_time, OCO_SELL_ORDER_SYMBOL, OCO_SELL_ORDER_ID, OCO_SELL_ORDER_ACTION,
                                        OCO_SELL_ORDER_TYPE, OCO_SELL_ORDER_PRICE, OCO_SELL_ORDER_QTY, OCO_SELL_PNL,
                                        OCO_SELL_PNL_PERCENTAGE])
                        conn.commit()


                except Exception as e:
                    print(e)

            t22 = threading.Thread(target=add_to_trade_oco)
            t22.start()

        def execute_limit_stop_loss_order(SPOT_SIDE,req_position_type,BUY_ORDER_ID, SPOT_SYMBOL, SPOT_SELL_QUANTITY, STOP_LOSS_PRICE_FINAL, SPOT_ENTRY,req_order_time_out):
            print(SPOT_SIDE)
            SPOT_EXIT = "LIMIT"

            STOP_LOSS_PRICE_FINAL_A = cal_price_with_precision(SPOT_SYMBOL=SPOT_SYMBOL,input_price=(STOP_LOSS_PRICE_FINAL * 0.9999))

            try:
                limit_stop_loss_order = client.create_order(symbol=SPOT_SYMBOL, side=SPOT_SIDE, type="STOP_LOSS_LIMIT",
                                                            quantity=SPOT_SELL_QUANTITY, price=STOP_LOSS_PRICE_FINAL,
                                                            stopPrice=STOP_LOSS_PRICE_FINAL_A, timeInForce="GTC")
                print(f"limit stop loss order = {limit_stop_loss_order}")

                if SPOT_SIDE == "BUY":
                    o_id_for_table = limit_stop_loss_order["orderId"]
                    cursor.execute("select entry_price from short_entry where symbol = %s", [SPOT_SYMBOL])
                    r_3 = cursor.fetchall()
                    price_results = r_3[0][0]
                    p_for_table = float(price_results)

                    cursor.execute("insert into s_id_list(order_id, entry_price) values (%s, %s)",
                                   [o_id_for_table, p_for_table])
                    conn.commit()
                if SPOT_SIDE == "SELL":
                    o_id_for_table = limit_stop_loss_order["orderId"]
                    cursor.execute("select entry_price from long_entry where symbol = %s", [SPOT_SYMBOL])
                    r_3 = cursor.fetchall()
                    price_results = r_3[0][0]
                    p_for_table = float(price_results)

                    cursor.execute("insert into s_id_list(order_id, entry_price) values (%s, %s)",
                                   [o_id_for_table, p_for_table])
                    conn.commit()

            except Exception as e:
                error_occured = f"{e}"
                print(error_occured)
                error_occured_time = datetime.now()

                cursor.execute(
                    "insert into error_log(symbol, order_action, entry_order_type, exit_order_type, quantity, occured_time, error_description) values (%s, %s, %s, %s, %s, %s, %s)",
                    [SPOT_SYMBOL, SPOT_SIDE, SPOT_ENTRY, SPOT_EXIT, SPOT_SELL_QUANTITY, error_occured_time, error_occured])
                conn.commit()

                error = "APIError(code=-2010): Account has insufficient balance for requested action."
                if str(e) == error and req_position_type == "Exit_long":
                    no_qty = True
                    oo_list = get_current_open_orders(SPOT_SYMBOL)

                    while no_qty == True:
                        for item in oo_list:
                            client.cancel_order(symbol=SPOT_SYMBOL, orderId=item)
                            try:
                                limit_stop_loss_order = client.create_order(symbol=SPOT_SYMBOL, side=SPOT_SIDE,
                                                                            type="STOP_LOSS_LIMIT",
                                                                            quantity=SPOT_SELL_QUANTITY,
                                                                            price=STOP_LOSS_PRICE_FINAL,
                                                                            stopPrice=STOP_LOSS_PRICE_FINAL_A,
                                                                            timeInForce="GTC")
                                print(f"limit stop loss order = {limit_stop_loss_order}")

                                if SPOT_SIDE == "BUY":
                                    o_id_for_table = limit_stop_loss_order["orderId"]
                                    cursor.execute("select entry_price from short_entry where symbol = %s", [SPOT_SYMBOL])
                                    r_3 = cursor.fetchall()
                                    price_results = r_3[0][0]
                                    p_for_table = float(price_results)

                                    cursor.execute("insert into s_id_list(order_id, entry_price) values (%s, %s)",
                                                   [o_id_for_table, p_for_table])
                                    conn.commit()
                                if SPOT_SIDE == "SELL":
                                    o_id_for_table = limit_stop_loss_order["orderId"]
                                    cursor.execute("select entry_price from long_entry where symbol = %s", [SPOT_SYMBOL])
                                    r_3 = cursor.fetchall()
                                    price_results = r_3[0][0]
                                    p_for_table = float(price_results)

                                    cursor.execute("insert into s_id_list(order_id, entry_price) values (%s, %s)",
                                                   [o_id_for_table, p_for_table])
                                    conn.commit()

                                no_qty = False
                                break
                            except Exception as e:
                                print(e)
                                pass

            limit_stop_loss_order_ID = limit_stop_loss_order["orderId"]
            print(limit_stop_loss_order_ID)

            def add_to_trade_sl():

                while True:
                    time.sleep(4)
                    try:
                        active_order = client.get_order(symbol=SPOT_SYMBOL, orderId=limit_stop_loss_order_ID)
                        active_order_status = active_order["status"]
                        if active_order_status == "FILLED":
                            break
                    except Exception as e:
                        print(e)
                        pass
                if active_order_status == "FILLED":
                    enter_long_sell_stop_loss_order = active_order
                    print(f"enter long sell stop loss order={enter_long_sell_stop_loss_order}")
                else:
                    check_for_partial = client.get_order(symbol=SPOT_SYMBOL, orderId=limit_stop_loss_order_ID)
                    if check_for_partial["status"] == "PARTIALLY_FILLED":
                        enter_long_sell_stop_loss_order = check_for_partial
                    check_for_cancel = client.get_order(symbol=SPOT_SYMBOL, orderId=limit_stop_loss_order_ID)
                    if check_for_cancel["status"] == "CANCELED" or check_for_cancel["status"] != "PARTIALLY_FILLED" or check_for_cancel["status"] != "FILLED":
                        print("Already cancelled")
                    else:
                        cancel_stop_loss_order = client.cancel_order(symbol=SPOT_SYMBOL, orderId=limit_stop_loss_order_ID)
                    error_occured = "Order time limit reached! Pending open oco sell orders have been cancelled"
                    print(error_occured)
                    error_occured_time = datetime.now()
                    cursor.execute(
                        "insert into error_log(symbol, order_action, entry_order_type, exit_order_type, quantity, occured_time, error_description) values (%s, %s, %s, %s, %s, %s, %s)",
                        [SPOT_SYMBOL, SPOT_SIDE, SPOT_ENTRY, SPOT_EXIT, SPOT_SELL_QUANTITY, error_occured_time, error_occured])
                    conn.commit()
                try:
                    STOP_LOSS_SELL_ORDER_ID = enter_long_sell_stop_loss_order["orderId"]
                    STOP_LOSS_SELL_ORDER_SYMBOL = enter_long_sell_stop_loss_order["symbol"]
                    STOP_LOSS_SELL_ORDER_QTY = float(enter_long_sell_stop_loss_order["executedQty"])
                    sell_cum_qty = float(enter_long_sell_stop_loss_order["cummulativeQuoteQty"])
                    TOTAL_SELL_SPEND = (sell_cum_qty / 100) * 99.9
                    TOTAL_BUY_SPEND = float(enter_long_sell_stop_loss_order["cummulativeQuoteQty"])
                    STOP_LOSS_SELL_ORDER_PRICE = round((float(enter_long_sell_stop_loss_order["cummulativeQuoteQty"]) / float(enter_long_sell_stop_loss_order["executedQty"])),3)
                    STOP_LOSS_SELL_ORDER_ACTION = enter_long_sell_stop_loss_order["side"]
                    STOP_LOSS_SELL_ORDER_TYPE = enter_long_sell_stop_loss_order["type"]
                    sell_order_executed_time = datetime.now()

                    if req_position_type == "Enter_long":
                        cursor.execute("select total_spend from id_list where order_id = %s", [BUY_ORDER_ID])
                        r_2 = cursor.fetchall()
                        price_results = r_2[0][0]
                        total_buy_spend = float(price_results)

                        STOP_LOSS_SELL_PNL = round((TOTAL_SELL_SPEND - total_buy_spend), 2)
                        stop_loss_sell_per = (STOP_LOSS_SELL_PNL / total_buy_spend) * 100
                        STOP_LOSS_SELL_PNL_PERCENTAGE = str((round(stop_loss_sell_per, 2))) + "%"

                        cursor.execute(sql.SQL(
                            "insert into trade_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty, pnl, percentage) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"),
                                       [sell_order_executed_time, STOP_LOSS_SELL_ORDER_SYMBOL, STOP_LOSS_SELL_ORDER_ID,
                                        STOP_LOSS_SELL_ORDER_ACTION, STOP_LOSS_SELL_ORDER_TYPE, STOP_LOSS_SELL_ORDER_PRICE,
                                        STOP_LOSS_SELL_ORDER_QTY, STOP_LOSS_SELL_PNL, STOP_LOSS_SELL_PNL_PERCENTAGE])
                        conn.commit()

                    if req_position_type == "Exit_long":
                        cursor.execute("select qty from long_entry where symbol = %s", [SPOT_SYMBOL])
                        r_3 = cursor.fetchall()
                        price_results = r_3[0][0]
                        previous_long_entry_qty = float(price_results)
                        print(f"previous_long_entry_qty = {previous_long_entry_qty}")

                        cursor.execute("select total_spend from long_entry where symbol = %s", [SPOT_SYMBOL])
                        r_3 = cursor.fetchall()
                        price_results = r_3[0][0]
                        previous_long_entry_spend = float(price_results)
                        print(f"previous_long_entry_spend = {previous_long_entry_spend}")

                        proportional_buy_spend = (previous_long_entry_spend / previous_long_entry_qty) * STOP_LOSS_SELL_ORDER_QTY
                        STOP_LOSS_SELL_PNL = round((TOTAL_SELL_SPEND - proportional_buy_spend), 2)
                        sl_sell_per = (STOP_LOSS_SELL_PNL / proportional_buy_spend) * 100
                        STOP_LOSS_SELL_PNL_PERCENTAGE = str((round(sl_sell_per, 2))) + "%"

                        cursor.execute(sql.SQL("insert into trade_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty, pnl, percentage) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"),[sell_order_executed_time, STOP_LOSS_SELL_ORDER_SYMBOL, STOP_LOSS_SELL_ORDER_ID,STOP_LOSS_SELL_ORDER_ACTION, STOP_LOSS_SELL_ORDER_TYPE, STOP_LOSS_SELL_ORDER_PRICE,STOP_LOSS_SELL_ORDER_QTY, STOP_LOSS_SELL_PNL, STOP_LOSS_SELL_PNL_PERCENTAGE])
                        conn.commit()

                    if req_position_type == "Enter_short":

                        cursor.execute("select exists (select 1 from short_entry)")
                        r_1 = cursor.fetchall()
                        live_r = r_1[0][0]

                        if live_r == False:
                            cursor.execute(sql.SQL(
                                "insert into short_entry(order_id, entry_price, total_spend, symbol, qty) values (%s, %s, %s, %s, %s)"),
                                           [STOP_LOSS_SELL_ORDER_ID, STOP_LOSS_SELL_ORDER_PRICE, TOTAL_SELL_SPEND, STOP_LOSS_SELL_ORDER_SYMBOL,STOP_LOSS_SELL_ORDER_QTY])
                            conn.commit()
                        if live_r == True:
                            cursor.execute(
                                "update short_entry set order_id = %s, entry_price = %s, total_spend = %s, symbol = %s, qty = %s",
                                [STOP_LOSS_SELL_ORDER_ID, STOP_LOSS_SELL_ORDER_PRICE, TOTAL_SELL_SPEND, STOP_LOSS_SELL_ORDER_SYMBOL,STOP_LOSS_SELL_ORDER_QTY])
                            conn.commit()
                            print("Records inserted")

                        cursor.execute(sql.SQL(
                            "insert into trade_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty) values (%s, %s, %s, %s, %s, %s, %s)"),
                                       [sell_order_executed_time, STOP_LOSS_SELL_ORDER_SYMBOL, STOP_LOSS_SELL_ORDER_ID,
                                        STOP_LOSS_SELL_ORDER_ACTION, STOP_LOSS_SELL_ORDER_TYPE, STOP_LOSS_SELL_ORDER_PRICE,
                                        STOP_LOSS_SELL_ORDER_QTY])
                        conn.commit()

                    if req_position_type == "Exit_short":
                        cursor.execute("select total_spend from short_entry where symbol = %s", [SPOT_SYMBOL])
                        r_3 = cursor.fetchall()
                        price_results = r_3[0][0]
                        previous_short_entry_income = float(price_results)
                        print(f"previous_short_entry_price = {previous_short_entry_income}")

                        cursor.execute("select qty from short_entry where symbol = %s", [SPOT_SYMBOL])
                        r_3 = cursor.fetchall()
                        price_results = r_3[0][0]
                        previous_short_entry_qty = float(price_results)
                        print(f"previous_short_entry_price = {previous_short_entry_qty}")

                        actual_sell_income = (previous_short_entry_income / 100) * 99.9
                        proportional_sell_income = (actual_sell_income / previous_short_entry_qty) * STOP_LOSS_SELL_ORDER_QTY
                        STOP_LOSS_SELL_PNL = round((proportional_sell_income - TOTAL_BUY_SPEND), 2)
                        sl_sell_per = (STOP_LOSS_SELL_PNL / proportional_sell_income) * 100
                        STOP_LOSS_SELL_PNL_PERCENTAGE = str((round(sl_sell_per, 2))) + "%"

                        cursor.execute(sql.SQL(
                            "insert into trade_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty, pnl, percentage) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"),
                            [sell_order_executed_time, STOP_LOSS_SELL_ORDER_SYMBOL, STOP_LOSS_SELL_ORDER_ID,
                             STOP_LOSS_SELL_ORDER_ACTION, STOP_LOSS_SELL_ORDER_TYPE, STOP_LOSS_SELL_ORDER_PRICE,
                             STOP_LOSS_SELL_ORDER_QTY, STOP_LOSS_SELL_PNL, STOP_LOSS_SELL_PNL_PERCENTAGE])
                        conn.commit()

                except Exception as e:
                    print(e)

            t20 = threading.Thread(target=add_to_trade_sl)
            t20.start()

        def execute_limit_take_profit_order(SPOT_SIDE,req_position_type,BUY_ORDER_ID, SPOT_SYMBOL, SPOT_SELL_QUANTITY, TAKE_PROFIT_PRICE_FINAL, SPOT_ENTRY,req_multi_tp,req_qty_size,req_order_time_out):
            print(SPOT_SIDE)
            SPOT_EXIT = "LIMIT"

            try:
                limit_take_proft_order = client.create_order(symbol=SPOT_SYMBOL, side=SPOT_SIDE, type="TAKE_PROFIT_LIMIT",
                                                             quantity=SPOT_SELL_QUANTITY, price=TAKE_PROFIT_PRICE_FINAL,
                                                             stopPrice=TAKE_PROFIT_PRICE_FINAL, timeInForce="GTC")
                print(f"limit take profit order = {limit_take_proft_order}")

                if SPOT_SIDE == "BUY":
                    o_id_for_table = limit_take_proft_order["orderId"]
                    cursor.execute("select entry_price from short_entry where symbol = %s", [SPOT_SYMBOL])
                    r_3 = cursor.fetchall()
                    price_results = r_3[0][0]
                    p_for_table = float(price_results)

                    cursor.execute("insert into s_id_list(order_id, entry_price) values (%s, %s)",
                                   [o_id_for_table, p_for_table])
                    conn.commit()
                if SPOT_SIDE == "SELL":
                    o_id_for_table = limit_take_proft_order["orderId"]
                    cursor.execute("select entry_price from long_entry where symbol = %s", [SPOT_SYMBOL])
                    r_3 = cursor.fetchall()
                    price_results = r_3[0][0]
                    p_for_table = float(price_results)

                    cursor.execute("insert into s_id_list(order_id, entry_price) values (%s, %s)",
                                   [o_id_for_table, p_for_table])
                    conn.commit()


            except Exception as e:
                error_occured = f"{e}"
                print(error_occured)
                error_occured_time = datetime.now()

                cursor.execute(
                    "insert into error_log(symbol, order_action, entry_order_type, exit_order_type, quantity, occured_time, error_description) values (%s, %s, %s, %s, %s, %s, %s)",
                    [SPOT_SYMBOL, SPOT_SIDE, SPOT_ENTRY, SPOT_EXIT, SPOT_SELL_QUANTITY, error_occured_time, error_occured])
                conn.commit()

                error = "APIError(code=-2010): Account has insufficient balance for requested action."
                if str(e) == error and req_position_type == "Exit_long":
                    no_qty = True
                    oo_list = get_current_open_orders(SPOT_SYMBOL)

                    while no_qty == True:
                        for item in oo_list:
                            client.cancel_order(symbol=SPOT_SYMBOL, orderId=item)
                            try:
                                limit_take_proft_order = client.create_order(symbol=SPOT_SYMBOL, side=SPOT_SIDE,
                                                                             type="TAKE_PROFIT_LIMIT",
                                                                             quantity=SPOT_SELL_QUANTITY,
                                                                             price=TAKE_PROFIT_PRICE_FINAL,
                                                                             stopPrice=TAKE_PROFIT_PRICE_FINAL,
                                                                             timeInForce="GTC")
                                print(f"limit take profit order = {limit_take_proft_order}")

                                if SPOT_SIDE == "BUY":
                                    o_id_for_table = limit_take_proft_order["orderId"]
                                    cursor.execute("select entry_price from short_entry where symbol = %s", [SPOT_SYMBOL])
                                    r_3 = cursor.fetchall()
                                    price_results = r_3[0][0]
                                    p_for_table = float(price_results)

                                    cursor.execute("insert into s_id_list(order_id, entry_price) values (%s, %s)",
                                                   [o_id_for_table, p_for_table])
                                    conn.commit()
                                if SPOT_SIDE == "SELL":
                                    o_id_for_table = limit_take_proft_order["orderId"]
                                    cursor.execute("select entry_price from long_entry where symbol = %s", [SPOT_SYMBOL])
                                    r_3 = cursor.fetchall()
                                    price_results = r_3[0][0]
                                    p_for_table = float(price_results)

                                    cursor.execute("insert into s_id_list(order_id, entry_price) values (%s, %s)",
                                                   [o_id_for_table, p_for_table])
                                    conn.commit()

                                no_qty = False
                                break
                            except Exception as e:
                                print(e)
                                pass

            limit_take_proft_order_ID = limit_take_proft_order["orderId"]
            print(limit_take_proft_order_ID)

            def add_to_trade_tp():
                while True:
                    time.sleep(4)
                    try:
                        time.sleep(1)
                        active_order = client.get_order(symbol=SPOT_SYMBOL, orderId=limit_take_proft_order_ID)
                        active_order_status = active_order["status"]
                        if active_order_status == "FILLED":
                            break
                    except Exception as e:
                        print(e)
                        pass
                if active_order_status == "FILLED":
                    enter_long_take_profit_order = active_order
                    print(f"enter long take profit order = {enter_long_take_profit_order}")
                else:
                    check_for_partial = client.get_order(symbol=SPOT_SYMBOL, orderId=limit_take_proft_order_ID)
                    if check_for_partial["status"] == "PARTIALLY_FILLED":
                        enter_long_take_profit_order = check_for_partial
                    check_for_cancel = client.get_order(symbol=SPOT_SYMBOL, orderId=limit_take_proft_order_ID)
                    if check_for_cancel["status"] == "CANCELED" or check_for_cancel["status"] != "PARTIALLY_FILLED" or check_for_cancel["status"] != "FILLED":
                        print("Already cancelled")
                    else:
                        cancel_stop_loss_order = client.cancel_order(symbol=SPOT_SYMBOL, orderId=limit_take_proft_order_ID)
                    error_occured = "Order time limit reached! Pending open oco sell orders have been cancelled"
                    print(error_occured)
                    error_occured_time = datetime.now()
                    cursor.execute(
                        "insert into error_log(symbol, order_action, entry_order_type, exit_order_type, quantity, occured_time, error_description) values (%s, %s, %s, %s, %s, %s, %s)",
                        [SPOT_SYMBOL, SPOT_SIDE, SPOT_ENTRY, SPOT_EXIT, SPOT_SELL_QUANTITY, error_occured_time, error_occured])
                    conn.commit()

                try:
                    TAKE_PROFIT_SELL_ORDER_ID = enter_long_take_profit_order["orderId"]
                    TAKE_PROFIT_SELL_ORDER_SYMBOL = enter_long_take_profit_order["symbol"]
                    TAKE_PROFIT_SELL_ORDER_QTY = float(enter_long_take_profit_order["executedQty"])
                    sell_cum_qty = float(enter_long_take_profit_order["cummulativeQuoteQty"])
                    TOTAL_SELL_SPEND = (sell_cum_qty / 100) * 99.9
                    TOTAL_BUY_SPEND = float(enter_long_take_profit_order["cummulativeQuoteQty"])
                    TAKE_PROFIT_SELL_ORDER_PRICE = round((float(enter_long_take_profit_order["cummulativeQuoteQty"]) / float(enter_long_take_profit_order["executedQty"])),3)
                    TAKE_PROFIT_SELL_ORDER_ACTION = enter_long_take_profit_order["side"]
                    TAKE_PROFIT_SELL_ORDER_TYPE = enter_long_take_profit_order["type"]
                    sell_order_executed_time = datetime.now()

                    if req_position_type == "Enter_long":
                        cursor.execute("select total_spend from id_list where order_id = %s", [BUY_ORDER_ID])
                        r_2 = cursor.fetchall()
                        price_results = r_2[0][0]
                        total_buy_spend = float(price_results)

                        if req_multi_tp == "No":
                            TAKE_PROFIT_SELL_PNL = round((TOTAL_SELL_SPEND - total_buy_spend), 2)
                            take_profit_sell_per = (TAKE_PROFIT_SELL_PNL / total_buy_spend) * 100
                            TAKE_PROFIT_SELL_PNL_PERCENTAGE = str((round(take_profit_sell_per, 2))) + "%"
                        if req_multi_tp == "Yes":
                            buy_spend_per = float(total_buy_spend) * float(req_qty_size)
                            TAKE_PROFIT_SELL_PNL = round((TOTAL_SELL_SPEND - buy_spend_per), 2)
                            take_profit_sell_per = (TAKE_PROFIT_SELL_PNL / buy_spend_per) * 100
                            TAKE_PROFIT_SELL_PNL_PERCENTAGE = str((round(take_profit_sell_per, 2))) + "%"

                        cursor.execute(sql.SQL(
                            "insert into trade_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty, pnl, percentage) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"),
                                       [sell_order_executed_time, TAKE_PROFIT_SELL_ORDER_SYMBOL, TAKE_PROFIT_SELL_ORDER_ID,
                                        TAKE_PROFIT_SELL_ORDER_ACTION, TAKE_PROFIT_SELL_ORDER_TYPE, TAKE_PROFIT_SELL_ORDER_PRICE,
                                        TAKE_PROFIT_SELL_ORDER_QTY, TAKE_PROFIT_SELL_PNL, TAKE_PROFIT_SELL_PNL_PERCENTAGE])
                        conn.commit()

                    if req_position_type == "Exit_long":
                        cursor.execute("select qty from long_entry where symbol = %s", [SPOT_SYMBOL])
                        r_3 = cursor.fetchall()
                        price_results = r_3[0][0]
                        previous_long_entry_qty = float(price_results)
                        print(f"previous_long_entry_qty = {previous_long_entry_qty}")

                        cursor.execute("select total_spend from long_entry where symbol = %s", [SPOT_SYMBOL])
                        r_3 = cursor.fetchall()
                        price_results = r_3[0][0]
                        previous_long_entry_spend = float(price_results)
                        print(f"previous_long_entry_spend = {previous_long_entry_spend}")

                        proportional_buy_spend = (previous_long_entry_spend / previous_long_entry_qty) * TAKE_PROFIT_SELL_ORDER_QTY
                        TAKE_PROFIT_SELL_PNL = round((TOTAL_SELL_SPEND - proportional_buy_spend), 2)
                        tp_sell_per = (TAKE_PROFIT_SELL_PNL / proportional_buy_spend) * 100
                        TAKE_PROFIT_SELL_PNL_PERCENTAGE = str((round(tp_sell_per, 2))) + "%"


                        cursor.execute(sql.SQL("insert into trade_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty, pnl, percentage) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"),[sell_order_executed_time, TAKE_PROFIT_SELL_ORDER_SYMBOL, TAKE_PROFIT_SELL_ORDER_ID,TAKE_PROFIT_SELL_ORDER_ACTION, TAKE_PROFIT_SELL_ORDER_TYPE, TAKE_PROFIT_SELL_ORDER_PRICE,TAKE_PROFIT_SELL_ORDER_QTY, TAKE_PROFIT_SELL_PNL, TAKE_PROFIT_SELL_PNL_PERCENTAGE])
                        conn.commit()

                    if req_position_type == "Enter_short":

                        cursor.execute("select exists (select 1 from short_entry)")
                        r_1 = cursor.fetchall()
                        live_r = r_1[0][0]

                        if live_r == False:
                            cursor.execute(sql.SQL(
                                "insert into short_entry(order_id, entry_price, total_spend, symbol, qty) values (%s, %s, %s, %s, %s)"),
                                [TAKE_PROFIT_SELL_ORDER_ID, TAKE_PROFIT_SELL_ORDER_PRICE, TOTAL_SELL_SPEND, TAKE_PROFIT_SELL_ORDER_SYMBOL,TAKE_PROFIT_SELL_ORDER_QTY])
                            conn.commit()
                        if live_r == True:
                            cursor.execute(
                                "update short_entry set order_id = %s, entry_price = %s, total_spend = %s, symbol = %s, qty = %s",
                                [TAKE_PROFIT_SELL_ORDER_ID, TAKE_PROFIT_SELL_ORDER_PRICE, TOTAL_SELL_SPEND, TAKE_PROFIT_SELL_ORDER_SYMBOL,TAKE_PROFIT_SELL_ORDER_QTY])
                            conn.commit()
                            print("Records inserted")

                        cursor.execute(sql.SQL(
                            "insert into trade_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty) values (%s, %s, %s, %s, %s, %s, %s)"),
                                       [sell_order_executed_time, TAKE_PROFIT_SELL_ORDER_SYMBOL, TAKE_PROFIT_SELL_ORDER_ID,
                                        TAKE_PROFIT_SELL_ORDER_ACTION, TAKE_PROFIT_SELL_ORDER_TYPE, TAKE_PROFIT_SELL_ORDER_PRICE,
                                        TAKE_PROFIT_SELL_ORDER_QTY])
                        conn.commit()

                    if req_position_type == "Exit_short":
                        cursor.execute("select total_spend from short_entry where symbol = %s", [SPOT_SYMBOL])
                        r_3 = cursor.fetchall()
                        price_results = r_3[0][0]
                        previous_short_entry_income = float(price_results)
                        print(f"previous_short_entry_price = {previous_short_entry_income}")

                        cursor.execute("select qty from short_entry where symbol = %s", [SPOT_SYMBOL])
                        r_3 = cursor.fetchall()
                        price_results = r_3[0][0]
                        previous_short_entry_qty = float(price_results)
                        print(f"previous_short_entry_price = {previous_short_entry_qty}")

                        actual_sell_income = (previous_short_entry_income / 100) * 99.9
                        proportional_sell_income = (actual_sell_income / previous_short_entry_qty) * TAKE_PROFIT_SELL_ORDER_QTY
                        TAKE_PROFIT_SELL_PNL = round((proportional_sell_income - TOTAL_BUY_SPEND), 2)
                        tp_sell_per = (TAKE_PROFIT_SELL_PNL / proportional_sell_income) * 100
                        TAKE_PROFIT_SELL_PNL_PERCENTAGE = str((round(tp_sell_per, 2))) + "%"

                        cursor.execute(sql.SQL(
                            "insert into trade_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty, pnl, percentage) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"),
                                       [sell_order_executed_time, TAKE_PROFIT_SELL_ORDER_SYMBOL, TAKE_PROFIT_SELL_ORDER_ID,
                                        TAKE_PROFIT_SELL_ORDER_ACTION, TAKE_PROFIT_SELL_ORDER_TYPE, TAKE_PROFIT_SELL_ORDER_PRICE,
                                        TAKE_PROFIT_SELL_ORDER_QTY, TAKE_PROFIT_SELL_PNL, TAKE_PROFIT_SELL_PNL_PERCENTAGE])
                        conn.commit()

                except Exception as e:
                    print(e)

            t21 = threading.Thread(target=add_to_trade_tp)
            t21.start()

        def proceed_enter_long(SPOT_BUY_QUANTITY,SPOT_SYMBOL,SPOT_ENTRY,req_long_stop_loss_percent,req_long_take_profit_percent,req_multi_tp,req_tp1_percent,req_tp2_percent,req_tp3_percent,req_tp1_qty_size,req_tp2_qty_size,req_tp3_qty_size,req_order_time_out):
            SPOT_EXIT = "NA"
            if SPOT_ENTRY == "MARKET":
                try:
                    enter_long_buy_order = client.create_order(symbol=SPOT_SYMBOL, side="BUY", type=SPOT_ENTRY,quantity=SPOT_BUY_QUANTITY)
                    time.sleep(5)
                    print(f"enter_long_buy_order = {enter_long_buy_order}")
                except Exception as e:
                    error_occured = f"{e}"
                    print(error_occured)
                    error_occured_time = datetime.now()

                    cursor.execute("insert into error_log(symbol, order_action, entry_order_type, exit_order_type, quantity, occured_time, error_description) values (%s, %s, %s, %s, %s, %s, %s)",[SPOT_SYMBOL, "BUY", SPOT_ENTRY, SPOT_EXIT, SPOT_BUY_QUANTITY, error_occured_time,error_occured])
                    conn.commit()

            elif SPOT_ENTRY == "LIMIT":
                prices = client.get_all_tickers()
                for ticker in prices:
                    if ticker["symbol"] == SPOT_SYMBOL:
                        last_price = float(ticker["price"])
                        break

                try:
                    limit_buy_order = client.order_limit_buy(symbol=SPOT_SYMBOL,quantity=SPOT_BUY_QUANTITY,price=last_price)
                    print(f"limit_buy_order = {limit_buy_order}")
                    limit_order_id = limit_buy_order["orderId"]
                except Exception as e:
                    error_occured = f"{e}"
                    print(error_occured)
                    error_occured_time = datetime.now()

                    cursor.execute("insert into error_log(symbol, order_action, entry_order_type, exit_order_type, quantity, occured_time, error_description) values (%s, %s, %s, %s, %s, %s, %s)",[SPOT_SYMBOL, "BUY", SPOT_ENTRY, SPOT_EXIT, SPOT_BUY_QUANTITY, error_occured_time,error_occured])
                    conn.commit()

                # Loop and check if entry order is filled
                entry_order_timeout_start = time.time()

                while time.time() < (entry_order_timeout_start + req_order_time_out):
                    try:
                        active_order = client.get_order(symbol=SPOT_SYMBOL, orderId=limit_order_id)
                        active_order_status = active_order["status"]
                        if active_order_status == "FILLED":
                            break
                    except Exception as e:
                        print(e)
                        pass
                if active_order_status == "FILLED":
                    enter_long_buy_order = active_order
                    print(f"enter long liit buy order = {enter_long_buy_order}")
                else:
                    check_for_partial = client.get_order(symbol=SPOT_SYMBOL, orderId=limit_order_id)
                    if check_for_partial["status"] == "PARTIALLY_FILLED":
                        enter_long_buy_order = check_for_partial
                    check_for_cancel = client.get_order(symbol=SPOT_SYMBOL, orderId=limit_order_id)
                    if check_for_cancel["status"] == "CANCELED" or check_for_cancel["status"] != "PARTIALLY_FILLED" or check_for_cancel["status"] != "FILLED":
                        print("Already cancelled")
                    else:
                        cancel_limit_order = client.cancel_order(symbol=SPOT_SYMBOL, orderId=limit_order_id)
                    error_occured = "Order time limit reached! Pending open limit orders has been cancelled"
                    print(error_occured)
                    error_occured_time = datetime.now()
                    cursor.execute("insert into error_log(symbol, order_action, entry_order_type, exit_order_type, quantity, occured_time, error_description) values (%s, %s, %s, %s, %s, %s, %s)",[SPOT_SYMBOL, "BUY", SPOT_ENTRY, SPOT_EXIT, SPOT_BUY_QUANTITY, error_occured_time, error_occured])
                    conn.commit()

            try:

                BUY_ORDER_ID = enter_long_buy_order["orderId"]
                BUY_ORDER_SYMBOL = enter_long_buy_order["symbol"]
                ask_qty = float(enter_long_buy_order["executedQty"])
                commision_in_coin = 0
                try:
                    for fill in enter_long_buy_order["fills"]:
                        comm = float(fill["commission"])
                        commision_in_coin += comm
                except:
                    commision_in_coin = ask_qty * 0.001
                BUY_ORDER_QTY = ask_qty - commision_in_coin
                TOTAL_BUY_SPEND = float(enter_long_buy_order["cummulativeQuoteQty"])
                print(f"Total buy spend = {TOTAL_BUY_SPEND}")
                BUY_ORDER_PRICE = round((float(enter_long_buy_order["cummulativeQuoteQty"]) / float(enter_long_buy_order["executedQty"])),3)
                BUY_ORDER_ACTION = enter_long_buy_order["side"]
                BUY_ORDER_TYPE = enter_long_buy_order["type"]
                buy_order_executed_time = datetime.now()

                cursor.execute(f"""INSERT INTO id_list (order_id, entry_price, total_spend) VALUES ({BUY_ORDER_ID},{BUY_ORDER_PRICE},{TOTAL_BUY_SPEND})""")
                conn.commit()
                print("Records inserted")

                cursor.execute("select exists (select 1 from long_entry)")
                r_1 = cursor.fetchall()
                live_r = r_1[0][0]

                if live_r == False:
                    cursor.execute(sql.SQL(
                        "insert into long_entry(order_id, entry_price, total_spend, symbol, qty) values (%s, %s, %s, %s, %s)"),
                                   [BUY_ORDER_ID, BUY_ORDER_PRICE, TOTAL_BUY_SPEND, BUY_ORDER_SYMBOL, BUY_ORDER_QTY])
                    conn.commit()
                if live_r == True:
                    cursor.execute(
                        "update long_entry set order_id = %s, entry_price = %s, total_spend = %s, symbol = %s, qty = %s",
                        [BUY_ORDER_ID, BUY_ORDER_PRICE, TOTAL_BUY_SPEND, BUY_ORDER_SYMBOL, BUY_ORDER_QTY])
                    conn.commit()
                    print("Records inserted")

                cursor.execute(sql.SQL("insert into trade_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty) values (%s, %s, %s, %s, %s, %s, %s)"),[buy_order_executed_time, BUY_ORDER_SYMBOL, BUY_ORDER_ID, BUY_ORDER_ACTION, BUY_ORDER_TYPE,BUY_ORDER_PRICE, BUY_ORDER_QTY])
                conn.commit()

                entry_price = BUY_ORDER_PRICE
                print(f"entry price = {entry_price}")

                if req_long_stop_loss_percent > 0 or req_long_take_profit_percent > 0 or req_multi_tp == "Yes":
                    SPOT_SIDE = "SELL"

                    long_stop_loss_bp = entry_price - (entry_price * req_long_stop_loss_percent)

                    long_take_profit_bp = entry_price + (entry_price * req_long_take_profit_percent)

                    STOP_LOSS_PRICE_FINAL = cal_price_with_precision(SPOT_SYMBOL=SPOT_SYMBOL, input_price=long_stop_loss_bp)
                    print(f"Stop loss price final = {STOP_LOSS_PRICE_FINAL}")


                    TAKE_PROFIT_PRICE_FINAL = cal_price_with_precision(SPOT_SYMBOL=SPOT_SYMBOL, input_price=long_take_profit_bp)
                    print(f"Take profit price final = {TAKE_PROFIT_PRICE_FINAL}")

                    SPOT_SELL_QUANTITY = calculate_sell_qty_with_precision(SPOT_SYMBOL=SPOT_SYMBOL, buy_qty=BUY_ORDER_QTY)
                    print(SPOT_SELL_QUANTITY)

                    if req_multi_tp == "No":
                        if req_long_stop_loss_percent > 0 and req_long_take_profit_percent > 0:
                            execute_limit_oco_order(SPOT_SIDE=SPOT_SIDE,req_position_type="Enter_long",BUY_ORDER_ID=BUY_ORDER_ID,SPOT_SYMBOL=SPOT_SYMBOL,SPOT_SELL_QUANTITY=SPOT_SELL_QUANTITY,TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL,STOP_LOSS_PRICE_FINAL=STOP_LOSS_PRICE_FINAL,SPOT_ENTRY=SPOT_ENTRY,req_multi_tp=req_multi_tp,req_qty_size=0,req_order_time_out=req_order_time_out)
                        elif req_long_stop_loss_percent > 0 and (req_long_take_profit_percent == "" or req_long_take_profit_percent == 0):
                            execute_limit_stop_loss_order(SPOT_SIDE=SPOT_SIDE,req_position_type="Enter_long",BUY_ORDER_ID=BUY_ORDER_ID,SPOT_SYMBOL=SPOT_SYMBOL,SPOT_SELL_QUANTITY=SPOT_SELL_QUANTITY,STOP_LOSS_PRICE_FINAL=STOP_LOSS_PRICE_FINAL,SPOT_ENTRY=SPOT_ENTRY,req_order_time_out=req_order_time_out)
                        elif req_long_take_profit_percent > 0 and (req_long_stop_loss_percent == "" or req_long_stop_loss_percent == 0):
                            execute_limit_take_profit_order(SPOT_SIDE=SPOT_SIDE,req_position_type="Enter_long",BUY_ORDER_ID=BUY_ORDER_ID,SPOT_SYMBOL=SPOT_SYMBOL,SPOT_SELL_QUANTITY=SPOT_SELL_QUANTITY,TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL,SPOT_ENTRY=SPOT_ENTRY,req_multi_tp=req_multi_tp,req_qty_size=0,req_order_time_out=req_order_time_out)

                    print(f"BUY ORDER QTY = {BUY_ORDER_QTY}")
                    print(f"SIZE={req_tp1_qty_size}")
                    if req_multi_tp == "Yes":
                        SELLABLE_1 = calculate_sell_qty_with_precision(SPOT_SYMBOL, (BUY_ORDER_QTY * req_tp1_qty_size))
                        print(f"Sellable qty_1 = {SELLABLE_1}")
                        SELLABLE_2 = calculate_sell_qty_with_precision(SPOT_SYMBOL, (BUY_ORDER_QTY * req_tp2_qty_size))
                        print(f"Sellable qty_2 = {SELLABLE_2}")
                        SELLABLE_3 = calculate_sell_qty_with_precision(SPOT_SYMBOL, (BUY_ORDER_QTY * req_tp3_qty_size))
                        print(f"Sellable qty_3 = {SELLABLE_3}")

                        long_take_profit_bp_1 = entry_price + (entry_price * req_tp1_percent)
                        long_take_profit_bp_2 = entry_price + (entry_price * req_tp2_percent)
                        long_take_profit_bp_3 = entry_price + (entry_price * req_tp3_percent)
                        TAKE_PROFIT_PRICE_FINAL_1 = cal_price_with_precision(SPOT_SYMBOL=SPOT_SYMBOL,input_price=long_take_profit_bp_1)
                        TAKE_PROFIT_PRICE_FINAL_2 = cal_price_with_precision(SPOT_SYMBOL=SPOT_SYMBOL,input_price=long_take_profit_bp_2)
                        TAKE_PROFIT_PRICE_FINAL_3 = cal_price_with_precision(SPOT_SYMBOL=SPOT_SYMBOL,input_price=long_take_profit_bp_3)
                        print(f"Take profit price final_1 = {TAKE_PROFIT_PRICE_FINAL_1}")
                        print(f"Take profit price final_2 = {TAKE_PROFIT_PRICE_FINAL_2}")
                        print(f"Take profit price final_3 = {TAKE_PROFIT_PRICE_FINAL_3}")

                        if req_long_stop_loss_percent > 0 and (req_tp1_percent > 0 or req_tp2_percent > 0 or req_tp3_percent > 0):
                            if req_tp1_percent > 0:
                                t1 = threading.Thread(target=lambda: execute_limit_oco_order(SPOT_SIDE=SPOT_SIDE,req_position_type="Enter_long",BUY_ORDER_ID=BUY_ORDER_ID, SPOT_SYMBOL=SPOT_SYMBOL,SPOT_SELL_QUANTITY=SELLABLE_1,TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL_1,STOP_LOSS_PRICE_FINAL=STOP_LOSS_PRICE_FINAL, SPOT_ENTRY=SPOT_ENTRY,req_multi_tp=req_multi_tp,req_qty_size=req_tp1_qty_size,req_order_time_out=req_order_time_out))
                                t1.start()
                            if req_tp2_percent > 0:
                                t2 = threading.Thread(target=lambda: execute_limit_oco_order(SPOT_SIDE=SPOT_SIDE,req_position_type="Enter_long",BUY_ORDER_ID=BUY_ORDER_ID, SPOT_SYMBOL=SPOT_SYMBOL,SPOT_SELL_QUANTITY=SELLABLE_2,TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL_2,STOP_LOSS_PRICE_FINAL=STOP_LOSS_PRICE_FINAL, SPOT_ENTRY=SPOT_ENTRY,req_multi_tp=req_multi_tp,req_qty_size=req_tp2_qty_size,req_order_time_out=req_order_time_out))
                                t2.start()
                            if req_tp3_percent > 0:
                                t2 = threading.Thread(target=lambda: execute_limit_oco_order(SPOT_SIDE=SPOT_SIDE,req_position_type="Enter_long",BUY_ORDER_ID=BUY_ORDER_ID, SPOT_SYMBOL=SPOT_SYMBOL,SPOT_SELL_QUANTITY=SELLABLE_3,TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL_3,STOP_LOSS_PRICE_FINAL=STOP_LOSS_PRICE_FINAL, SPOT_ENTRY=SPOT_ENTRY,req_multi_tp=req_multi_tp,req_qty_size=req_tp3_qty_size,req_order_time_out=req_order_time_out))
                                t2.start()

                        elif req_long_stop_loss_percent > 0 and (req_tp1_percent == 0 and req_tp2_percent == 0 and req_tp3_percent == 0):
                            execute_limit_stop_loss_order(SPOT_SIDE=SPOT_SIDE,req_position_type="Enter_long",BUY_ORDER_ID=BUY_ORDER_ID, SPOT_SYMBOL=SPOT_SYMBOL, SPOT_SELL_QUANTITY=SPOT_SELL_QUANTITY, STOP_LOSS_PRICE_FINAL=STOP_LOSS_PRICE_FINAL,SPOT_ENTRY=SPOT_ENTRY,req_order_time_out=req_order_time_out)

                        elif (req_tp1_percent > 0 or req_tp2_percent > 0 or req_tp3_percent > 0) and (req_long_stop_loss_percent == "" or req_long_stop_loss_percent == 0):
                            if req_tp1_percent > 0:
                                t1 = threading.Thread(target=lambda: execute_limit_take_profit_order(SPOT_SIDE=SPOT_SIDE,req_position_type="Enter_long",BUY_ORDER_ID=BUY_ORDER_ID,SPOT_SYMBOL=SPOT_SYMBOL,SPOT_SELL_QUANTITY=SELLABLE_1,TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL_1,SPOT_ENTRY=SPOT_ENTRY,req_multi_tp=req_multi_tp,req_qty_size=req_tp1_qty_size,req_order_time_out=req_order_time_out))
                                t1.start()
                            if req_tp2_percent > 0:
                                t2 = threading.Thread(target=lambda: execute_limit_take_profit_order(SPOT_SIDE=SPOT_SIDE,req_position_type="Enter_long",BUY_ORDER_ID=BUY_ORDER_ID, SPOT_SYMBOL=SPOT_SYMBOL,SPOT_SELL_QUANTITY=SELLABLE_2,TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL_2,SPOT_ENTRY=SPOT_ENTRY,req_multi_tp=req_multi_tp,req_qty_size=req_tp2_qty_size,req_order_time_out=req_order_time_out))
                                t2.start()
                            if req_tp3_percent > 0:
                                t3 = threading.Thread(target=lambda: execute_limit_take_profit_order(SPOT_SIDE=SPOT_SIDE,req_position_type="Enter_long",BUY_ORDER_ID=BUY_ORDER_ID, SPOT_SYMBOL=SPOT_SYMBOL,SPOT_SELL_QUANTITY=SELLABLE_3,TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL_3,SPOT_ENTRY=SPOT_ENTRY,req_multi_tp=req_multi_tp,req_qty_size=req_tp2_qty_size,req_order_time_out=req_order_time_out))
                                t3.start()


            except Exception as e:
                error_occured = f"{e}"
                print(error_occured)

        def proceed_exit_long(req_position_type,SPOT_SELL_QUANTITY_EL,SPOT_SYMBOL,req_long_stop_loss_percent,req_long_take_profit_percent,req_multi_tp,req_tp1_percent,req_tp2_percent,req_tp3_percent,req_tp1_qty_size,req_tp2_qty_size,req_tp3_qty_size,req_order_time_out):
            SPOT_ENTRY = "NA"
            SPOT_SIDE = "SELL"

            cursor.execute("select entry_price from long_entry where symbol = %s", [SPOT_SYMBOL])
            r_3 = cursor.fetchall()
            price_results = r_3[0][0]
            previous_long_entry_price = float(price_results)
            print(f"previous_long_entry_price= {previous_long_entry_price}")

            if req_long_stop_loss_percent > 0 or req_long_take_profit_percent > 0 or req_multi_tp == "Yes":
                SPOT_EXIT = "LIMIT"

                long_stop_loss_bp = previous_long_entry_price - (previous_long_entry_price * req_long_stop_loss_percent)

                long_take_profit_bp = previous_long_entry_price + (previous_long_entry_price * req_long_take_profit_percent)

                STOP_LOSS_PRICE_FINAL = cal_price_with_precision(SPOT_SYMBOL=SPOT_SYMBOL, input_price=long_stop_loss_bp)
                print(f"Stop loss price final = {STOP_LOSS_PRICE_FINAL}")

                TAKE_PROFIT_PRICE_FINAL = cal_price_with_precision(SPOT_SYMBOL=SPOT_SYMBOL, input_price=long_take_profit_bp)
                print(f"Take profit price final = {TAKE_PROFIT_PRICE_FINAL}")

                BUY_ORDER_ID = 0

                if req_multi_tp == "No":
                    if req_long_stop_loss_percent > 0 and req_long_take_profit_percent > 0:
                        execute_limit_oco_order(SPOT_SIDE=SPOT_SIDE,req_position_type=req_position_type,BUY_ORDER_ID=BUY_ORDER_ID, SPOT_SYMBOL=SPOT_SYMBOL,SPOT_SELL_QUANTITY=SPOT_SELL_QUANTITY_EL,TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL,STOP_LOSS_PRICE_FINAL=STOP_LOSS_PRICE_FINAL, SPOT_ENTRY=SPOT_ENTRY,req_multi_tp=req_multi_tp, req_qty_size=0,req_order_time_out=req_order_time_out)
                    elif req_long_stop_loss_percent > 0 and (req_long_take_profit_percent == "" or req_long_take_profit_percent == 0):
                        execute_limit_stop_loss_order(SPOT_SIDE,req_position_type,BUY_ORDER_ID, SPOT_SYMBOL, SPOT_SELL_QUANTITY_EL, STOP_LOSS_PRICE_FINAL,SPOT_ENTRY,req_order_time_out)
                    elif req_long_take_profit_percent > 0 and (req_long_stop_loss_percent == "" or req_long_stop_loss_percent == 0):
                        execute_limit_take_profit_order(SPOT_SIDE=SPOT_SIDE,req_position_type=req_position_type,BUY_ORDER_ID=BUY_ORDER_ID, SPOT_SYMBOL=SPOT_SYMBOL,SPOT_SELL_QUANTITY=SPOT_SELL_QUANTITY_EL,TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL, SPOT_ENTRY=SPOT_ENTRY,req_multi_tp=req_multi_tp, req_qty_size=0,req_order_time_out=req_order_time_out)

                if req_multi_tp == "Yes":
                    SELLABLE_1 = trunc_calculate_sell_qty_with_precision(SPOT_SYMBOL, (SPOT_SELL_QUANTITY_EL * req_tp1_qty_size))
                    print(f"Sellable qty_1 = {SELLABLE_1}")
                    SELLABLE_2 = trunc_calculate_sell_qty_with_precision(SPOT_SYMBOL, (SPOT_SELL_QUANTITY_EL * req_tp2_qty_size))
                    print(f"Sellable qty_2 = {SELLABLE_2}")
                    SELLABLE_3 = trunc_calculate_sell_qty_with_precision(SPOT_SYMBOL, (SPOT_SELL_QUANTITY_EL * req_tp3_qty_size))
                    print(f"Sellable qty_3 = {SELLABLE_3}")

                    long_take_profit_bp_1 = previous_long_entry_price + (previous_long_entry_price * req_tp1_percent)
                    long_take_profit_bp_2 = previous_long_entry_price + (previous_long_entry_price * req_tp2_percent)
                    long_take_profit_bp_3 = previous_long_entry_price + (previous_long_entry_price * req_tp3_percent)
                    TAKE_PROFIT_PRICE_FINAL_1 = cal_price_with_precision(SPOT_SYMBOL=SPOT_SYMBOL,input_price=long_take_profit_bp_1)
                    TAKE_PROFIT_PRICE_FINAL_2 = cal_price_with_precision(SPOT_SYMBOL=SPOT_SYMBOL,input_price=long_take_profit_bp_2)
                    TAKE_PROFIT_PRICE_FINAL_3 = cal_price_with_precision(SPOT_SYMBOL=SPOT_SYMBOL,input_price=long_take_profit_bp_3)
                    print(f"Take profit price final_1 = {TAKE_PROFIT_PRICE_FINAL_1}")
                    print(f"Take profit price final_2 = {TAKE_PROFIT_PRICE_FINAL_2}")
                    print(f"Take profit price final_3 = {TAKE_PROFIT_PRICE_FINAL_3}")

                    if req_long_stop_loss_percent > 0 and (req_tp1_percent > 0 or req_tp2_percent > 0 or req_tp3_percent > 0):
                        if req_tp1_percent > 0:
                            t1 = threading.Thread(target=lambda: execute_limit_oco_order(SPOT_SIDE=SPOT_SIDE,req_position_type=req_position_type,BUY_ORDER_ID=BUY_ORDER_ID, SPOT_SYMBOL=SPOT_SYMBOL,SPOT_SELL_QUANTITY=SELLABLE_1,TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL_1,STOP_LOSS_PRICE_FINAL=STOP_LOSS_PRICE_FINAL,SPOT_ENTRY=SPOT_ENTRY, req_multi_tp=req_multi_tp,req_qty_size=req_tp1_qty_size,req_order_time_out=req_order_time_out))
                            t1.start()
                        if req_tp2_percent > 0:
                            t2 = threading.Thread(target=lambda: execute_limit_oco_order(SPOT_SIDE=SPOT_SIDE,req_position_type=req_position_type,BUY_ORDER_ID=BUY_ORDER_ID, SPOT_SYMBOL=SPOT_SYMBOL,SPOT_SELL_QUANTITY=SELLABLE_2,TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL_2,STOP_LOSS_PRICE_FINAL=STOP_LOSS_PRICE_FINAL,SPOT_ENTRY=SPOT_ENTRY, req_multi_tp=req_multi_tp,req_qty_size=req_tp2_qty_size,req_order_time_out=req_order_time_out))
                            t2.start()
                        if req_tp3_percent > 0:
                            t3 = threading.Thread(target=lambda: execute_limit_oco_order(SPOT_SIDE=SPOT_SIDE,req_position_type=req_position_type,BUY_ORDER_ID=BUY_ORDER_ID, SPOT_SYMBOL=SPOT_SYMBOL,SPOT_SELL_QUANTITY=SELLABLE_3,TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL_3,STOP_LOSS_PRICE_FINAL=STOP_LOSS_PRICE_FINAL,SPOT_ENTRY=SPOT_ENTRY, req_multi_tp=req_multi_tp,req_qty_size=req_tp3_qty_size,req_order_time_out=req_order_time_out))
                            t3.start()

                    elif req_long_stop_loss_percent > 0 and (req_tp1_percent == 0 and req_tp2_percent == 0 and req_tp3_percent == 0):
                        execute_limit_stop_loss_order(SPOT_SIDE,req_position_type,BUY_ORDER_ID, SPOT_SYMBOL, SPOT_SELL_QUANTITY_EL, STOP_LOSS_PRICE_FINAL,SPOT_ENTRY,req_order_time_out)

                    elif (req_tp1_percent > 0 or req_tp2_percent > 0 or req_tp3_percent > 0) and (req_long_stop_loss_percent == "" or req_long_stop_loss_percent == 0):
                        if req_tp1_percent > 0:
                            t1 = threading.Thread(target=lambda: execute_limit_take_profit_order(SPOT_SIDE=SPOT_SIDE,req_position_type=req_position_type,BUY_ORDER_ID=BUY_ORDER_ID,SPOT_SYMBOL=SPOT_SYMBOL,SPOT_SELL_QUANTITY=SELLABLE_1,TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL_1,SPOT_ENTRY=SPOT_ENTRY,req_multi_tp=req_multi_tp,req_qty_size=req_tp1_qty_size,req_order_time_out=req_order_time_out))
                            t1.start()
                        if req_tp2_percent > 0:
                            t2 = threading.Thread(target=lambda: execute_limit_take_profit_order(SPOT_SIDE=SPOT_SIDE,req_position_type=req_position_type,BUY_ORDER_ID=BUY_ORDER_ID,SPOT_SYMBOL=SPOT_SYMBOL,SPOT_SELL_QUANTITY=SELLABLE_2,TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL_2,SPOT_ENTRY=SPOT_ENTRY,req_multi_tp=req_multi_tp,req_qty_size=req_tp2_qty_size,req_order_time_out=req_order_time_out))
                            t2.start()
                        if req_tp3_percent > 0:
                            t3 = threading.Thread(target=lambda: execute_limit_take_profit_order(SPOT_SIDE=SPOT_SIDE,req_position_type=req_position_type,BUY_ORDER_ID=BUY_ORDER_ID,SPOT_SYMBOL=SPOT_SYMBOL,SPOT_SELL_QUANTITY=SELLABLE_3,TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL_3,SPOT_ENTRY=SPOT_ENTRY,req_multi_tp=req_multi_tp,req_qty_size=req_tp2_qty_size,req_order_time_out=req_order_time_out))
                            t3.start()


            elif req_long_stop_loss_percent == 0 and req_long_take_profit_percent == 0 and req_multi_tp == "No":
                SPOT_EXIT = "MARKET"
                try:
                    exit_long_sell_order = client.create_order(symbol=SPOT_SYMBOL, side=SPOT_SIDE, type=SPOT_EXIT,
                                                               quantity=SPOT_SELL_QUANTITY_EL)

                    time.sleep(5)
                    print(f"exit long sell order = {exit_long_sell_order}")
                except Exception as e:
                    error_occured = f"{e}"
                    print(error_occured)
                    error_occured_time = datetime.now()

                    cursor.execute(
                        "insert into error_log(symbol, order_action, entry_order_type, exit_order_type, quantity, occured_time, error_description) values (%s, %s, %s, %s, %s, %s, %s)",
                        [SPOT_SYMBOL, SPOT_SIDE, SPOT_ENTRY, SPOT_EXIT, SPOT_SELL_QUANTITY_EL, error_occured_time,
                         error_occured])
                    conn.commit()

                    error = "APIError(code=-2010): Account has insufficient balance for requested action."
                    if str(e) == error:
                        no_qty = True
                        oo_list = get_current_open_orders(SPOT_SYMBOL)

                        while no_qty == True:
                            for item in oo_list:
                                client.cancel_order(symbol=SPOT_SYMBOL, orderId=item)
                                try:
                                    exit_long_sell_order = client.create_order(symbol=SPOT_SYMBOL, side=SPOT_SIDE,
                                                                               type=SPOT_EXIT,
                                                                               quantity=SPOT_SELL_QUANTITY_EL)
                                    no_qty = False
                                    break
                                except Exception as e:
                                    print(e)
                                    pass


                try:

                    SELL_ORDER_ID = exit_long_sell_order["orderId"]
                    SELL_ORDER_SYMBOL = exit_long_sell_order["symbol"]
                    SELL_ORDER_QTY = float(exit_long_sell_order["executedQty"])
                    sell_cum_qty = float(exit_long_sell_order["cummulativeQuoteQty"])
                    TOTAL_SELL_SPEND = (sell_cum_qty/100)*99.9
                    print(f"Total buy spend = {TOTAL_SELL_SPEND}")
                    SELL_ORDER_PRICE = round((float(exit_long_sell_order["cummulativeQuoteQty"]) / float(exit_long_sell_order["executedQty"])),3)
                    SELL_ORDER_ACTION = exit_long_sell_order["side"]
                    SELL_ORDER_TYPE = exit_long_sell_order["type"]
                    sell_order_executed_time = datetime.now()

                    cursor.execute("select qty from long_entry where symbol = %s", [SPOT_SYMBOL])
                    r_3 = cursor.fetchall()
                    price_results = r_3[0][0]
                    previous_long_entry_qty = float(price_results)
                    print(f"previous_long_entry_qty = {previous_long_entry_qty}")

                    cursor.execute("select total_spend from long_entry where symbol = %s", [SPOT_SYMBOL])
                    r_3 = cursor.fetchall()
                    price_results = r_3[0][0]
                    previous_long_entry_spend = float(price_results)
                    print(f"previous_long_entry_spend = {previous_long_entry_spend}")

                    proportional_buy_spend = (previous_long_entry_spend / previous_long_entry_qty) * SELL_ORDER_QTY
                    SELL_ORDER_SELL_PNL = round((TOTAL_SELL_SPEND - proportional_buy_spend), 2)
                    sell_order_pnl_per = (SELL_ORDER_SELL_PNL / proportional_buy_spend) * 100
                    SELL_ORDER_SELL_PNL_PERCENTAGE = str((round(sell_order_pnl_per, 2))) + "%"

                    cursor.execute(sql.SQL("insert into trade_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty, pnl, percentage) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"),[sell_order_executed_time, SELL_ORDER_SYMBOL, SELL_ORDER_ID, SELL_ORDER_ACTION, SELL_ORDER_TYPE, SELL_ORDER_PRICE, SELL_ORDER_QTY, SELL_ORDER_SELL_PNL, SELL_ORDER_SELL_PNL_PERCENTAGE])
                    conn.commit()

                except Exception as e:
                    error_occured = f"{e}"
                    print(error_occured)

        def proceed_enter_short(req_position_type,SPOT_SELL_QUANTITY_EL,SPOT_SYMBOL,req_short_stop_loss_percent,req_short_take_profit_percent,req_multi_tp,req_tp1_percent,req_tp2_percent,req_tp3_percent,req_tp1_qty_size,req_tp2_qty_size,req_tp3_qty_size,req_order_time_out):

            SPOT_ENTRY = "NA"
            SPOT_SIDE = "SELL"

            prices = client.get_all_tickers()
            for ticker in prices:
                if ticker["symbol"] == SPOT_SYMBOL:
                    last_price = float(ticker["price"])
                    break

            if req_short_stop_loss_percent > 0 or req_short_take_profit_percent > 0 or req_multi_tp == "Yes":
                SPOT_EXIT = "LIMIT"

                short_stop_loss_bp = last_price - (last_price * req_short_stop_loss_percent)

                short_take_profit_bp = last_price + (last_price * req_short_take_profit_percent)

                STOP_LOSS_PRICE_FINAL = cal_price_with_precision(SPOT_SYMBOL=SPOT_SYMBOL, input_price=short_stop_loss_bp)
                print(f"Stop loss price final = {STOP_LOSS_PRICE_FINAL}")

                TAKE_PROFIT_PRICE_FINAL = cal_price_with_precision(SPOT_SYMBOL=SPOT_SYMBOL, input_price=short_take_profit_bp)
                print(f"Take profit price final = {TAKE_PROFIT_PRICE_FINAL}")

                BUY_ORDER_ID = 0

                if req_multi_tp == "No":
                    if req_short_stop_loss_percent > 0 and req_short_take_profit_percent > 0:
                        execute_limit_oco_order(SPOT_SIDE=SPOT_SIDE,req_position_type=req_position_type,BUY_ORDER_ID=BUY_ORDER_ID, SPOT_SYMBOL=SPOT_SYMBOL,SPOT_SELL_QUANTITY=SPOT_SELL_QUANTITY_EL,TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL,STOP_LOSS_PRICE_FINAL=STOP_LOSS_PRICE_FINAL, SPOT_ENTRY=SPOT_ENTRY,req_multi_tp=req_multi_tp, req_qty_size=0,req_order_time_out=req_order_time_out)
                    elif req_short_stop_loss_percent > 0 and (req_short_take_profit_percent == "" or req_short_take_profit_percent == 0):
                        execute_limit_stop_loss_order(SPOT_SIDE,req_position_type,BUY_ORDER_ID, SPOT_SYMBOL, SPOT_SELL_QUANTITY_EL, STOP_LOSS_PRICE_FINAL,SPOT_ENTRY,req_order_time_out)
                    elif req_short_take_profit_percent > 0 and (req_short_stop_loss_percent == "" or req_short_stop_loss_percent == 0):
                        execute_limit_take_profit_order(SPOT_SIDE=SPOT_SIDE,req_position_type=req_position_type,BUY_ORDER_ID=BUY_ORDER_ID, SPOT_SYMBOL=SPOT_SYMBOL,SPOT_SELL_QUANTITY=SPOT_SELL_QUANTITY_EL,TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL, SPOT_ENTRY=SPOT_ENTRY,req_multi_tp=req_multi_tp, req_qty_size=0,req_order_time_out=req_order_time_out)

                if req_multi_tp == "Yes":
                    SELLABLE_1 = calculate_sell_qty_with_precision(SPOT_SYMBOL, (SPOT_SELL_QUANTITY_EL * req_tp1_qty_size))
                    print(f"Sellable qty_1 = {SELLABLE_1}")
                    SELLABLE_2 = calculate_sell_qty_with_precision(SPOT_SYMBOL, (SPOT_SELL_QUANTITY_EL * req_tp2_qty_size))
                    print(f"Sellable qty_2 = {SELLABLE_2}")
                    SELLABLE_3 = calculate_sell_qty_with_precision(SPOT_SYMBOL, (SPOT_SELL_QUANTITY_EL * req_tp3_qty_size))
                    print(f"Sellable qty_3 = {SELLABLE_3}")

                    short_take_profit_bp_1 = last_price + (last_price * req_tp1_percent)
                    short_take_profit_bp_2 = last_price + (last_price * req_tp2_percent)
                    short_take_profit_bp_3 = last_price + (last_price * req_tp3_percent)
                    TAKE_PROFIT_PRICE_FINAL_1 = cal_price_with_precision(SPOT_SYMBOL=SPOT_SYMBOL,input_price=short_take_profit_bp_1)
                    TAKE_PROFIT_PRICE_FINAL_2 = cal_price_with_precision(SPOT_SYMBOL=SPOT_SYMBOL,input_price=short_take_profit_bp_2)
                    TAKE_PROFIT_PRICE_FINAL_3 = cal_price_with_precision(SPOT_SYMBOL=SPOT_SYMBOL,input_price=short_take_profit_bp_3)
                    print(f"Take profit price final_1 = {TAKE_PROFIT_PRICE_FINAL_1}")
                    print(f"Take profit price final_2 = {TAKE_PROFIT_PRICE_FINAL_2}")
                    print(f"Take profit price final_3 = {TAKE_PROFIT_PRICE_FINAL_3}")

                    if req_short_stop_loss_percent > 0 and (req_tp1_percent > 0 or req_tp2_percent > 0 or req_tp3_percent > 0):
                        if req_tp1_percent > 0:
                            t1 = threading.Thread(target=lambda: execute_limit_oco_order(SPOT_SIDE=SPOT_SIDE,req_position_type=req_position_type,BUY_ORDER_ID=BUY_ORDER_ID, SPOT_SYMBOL=SPOT_SYMBOL,SPOT_SELL_QUANTITY=SELLABLE_1,TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL_1,STOP_LOSS_PRICE_FINAL=STOP_LOSS_PRICE_FINAL,SPOT_ENTRY=SPOT_ENTRY, req_multi_tp=req_multi_tp,req_qty_size=req_tp1_qty_size,req_order_time_out=req_order_time_out))
                            t1.start()
                        if req_tp2_percent > 0:
                            t2 = threading.Thread(target=lambda: execute_limit_oco_order(SPOT_SIDE=SPOT_SIDE,req_position_type=req_position_type,BUY_ORDER_ID=BUY_ORDER_ID, SPOT_SYMBOL=SPOT_SYMBOL,SPOT_SELL_QUANTITY=SELLABLE_2,TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL_2,STOP_LOSS_PRICE_FINAL=STOP_LOSS_PRICE_FINAL,SPOT_ENTRY=SPOT_ENTRY, req_multi_tp=req_multi_tp,req_qty_size=req_tp2_qty_size,req_order_time_out=req_order_time_out))
                            t2.start()
                        if req_tp3_percent > 0:
                            t3 = threading.Thread(target=lambda: execute_limit_oco_order(SPOT_SIDE=SPOT_SIDE,req_position_type=req_position_type,BUY_ORDER_ID=BUY_ORDER_ID, SPOT_SYMBOL=SPOT_SYMBOL,SPOT_SELL_QUANTITY=SELLABLE_3,TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL_3,STOP_LOSS_PRICE_FINAL=STOP_LOSS_PRICE_FINAL,SPOT_ENTRY=SPOT_ENTRY, req_multi_tp=req_multi_tp,req_qty_size=req_tp3_qty_size,req_order_time_out=req_order_time_out))
                            t3.start()

                    elif req_short_stop_loss_percent > 0 and (req_tp1_percent == 0 and req_tp2_percent == 0 and req_tp3_percent == 0):
                        execute_limit_stop_loss_order(SPOT_SIDE,req_position_type,BUY_ORDER_ID, SPOT_SYMBOL, SPOT_SELL_QUANTITY_EL, STOP_LOSS_PRICE_FINAL,SPOT_ENTRY,req_order_time_out)


                    elif (req_tp1_percent > 0 or req_tp2_percent > 0 or req_tp3_percent > 0) and (req_short_stop_loss_percent == "" or req_short_stop_loss_percent == 0):
                        if req_tp1_percent > 0:
                            t1 = threading.Thread(target=lambda: execute_limit_take_profit_order(SPOT_SIDE=SPOT_SIDE,req_position_type=req_position_type,BUY_ORDER_ID=BUY_ORDER_ID,SPOT_SYMBOL=SPOT_SYMBOL,SPOT_SELL_QUANTITY=SELLABLE_1,TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL_1,SPOT_ENTRY=SPOT_ENTRY,req_multi_tp=req_multi_tp,req_qty_size=req_tp1_qty_size,req_order_time_out=req_order_time_out))
                            t1.start()
                        if req_tp2_percent > 0:
                            t2 = threading.Thread(target=lambda: execute_limit_take_profit_order(SPOT_SIDE=SPOT_SIDE,req_position_type=req_position_type,BUY_ORDER_ID=BUY_ORDER_ID,SPOT_SYMBOL=SPOT_SYMBOL,SPOT_SELL_QUANTITY=SELLABLE_2,TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL_2,SPOT_ENTRY=SPOT_ENTRY,req_multi_tp=req_multi_tp,req_qty_size=req_tp2_qty_size,req_order_time_out=req_order_time_out))
                            t2.start()
                        if req_tp3_percent > 0:
                            t3 = threading.Thread(target=lambda: execute_limit_take_profit_order(SPOT_SIDE=SPOT_SIDE,req_position_type=req_position_type,BUY_ORDER_ID=BUY_ORDER_ID,SPOT_SYMBOL=SPOT_SYMBOL,SPOT_SELL_QUANTITY=SELLABLE_3,TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL_3,SPOT_ENTRY=SPOT_ENTRY,req_multi_tp=req_multi_tp,req_qty_size=req_tp2_qty_size,req_order_time_out=req_order_time_out))
                            t3.start()



            elif req_short_stop_loss_percent == 0 and req_short_take_profit_percent == 0 and req_multi_tp == "No":
                SPOT_EXIT = "MARKET"
                try:
                    exit_long_sell_order = client.create_order(symbol=SPOT_SYMBOL, side=SPOT_SIDE, type=SPOT_EXIT,
                                                               quantity=SPOT_SELL_QUANTITY_EL)

                    time.sleep(5)
                    print(f"exit long sell order = {exit_long_sell_order}")
                except Exception as e:
                    error_occured = f"{e}"
                    print(error_occured)
                    error_occured_time = datetime.now()

                    cursor.execute("insert into error_log(symbol, order_action, entry_order_type, exit_order_type, quantity, occured_time, error_description) values (%s, %s, %s, %s, %s, %s, %s)",[SPOT_SYMBOL, SPOT_SIDE, SPOT_ENTRY, SPOT_EXIT, SPOT_SELL_QUANTITY_EL, error_occured_time, error_occured])
                    conn.commit()

                try:

                    SELL_ORDER_ID = exit_long_sell_order["orderId"]
                    SELL_ORDER_SYMBOL = exit_long_sell_order["symbol"]
                    SELL_ORDER_QTY = float(exit_long_sell_order["executedQty"])
                    TOTAL_SELL_SPEND = float(exit_long_sell_order["cummulativeQuoteQty"])
                    print(f"Total buy spend = {TOTAL_SELL_SPEND}")
                    SELL_ORDER_PRICE = round((float(exit_long_sell_order["cummulativeQuoteQty"]) / float(exit_long_sell_order["executedQty"])),3)
                    SELL_ORDER_ACTION = exit_long_sell_order["side"]
                    SELL_ORDER_TYPE = exit_long_sell_order["type"]
                    sell_order_executed_time = datetime.now()

                    cursor.execute("select exists (select 1 from short_entry)")
                    r_1 = cursor.fetchall()
                    live_r = r_1[0][0]

                    if live_r == False:
                        cursor.execute(sql.SQL("insert into short_entry(order_id, entry_price, total_spend, symbol, qty) values (%s, %s, %s, %s, %s)"),[SELL_ORDER_ID, SELL_ORDER_PRICE, TOTAL_SELL_SPEND, SELL_ORDER_SYMBOL,SELL_ORDER_QTY])
                        conn.commit()
                    if live_r == True:
                        cursor.execute("update short_entry set order_id = %s, entry_price = %s, total_spend = %s, symbol = %s, qty = %s",[SELL_ORDER_ID, SELL_ORDER_PRICE, TOTAL_SELL_SPEND, SELL_ORDER_SYMBOL,SELL_ORDER_QTY])
                        conn.commit()
                        print("Records inserted")

                    cursor.execute(sql.SQL("insert into trade_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty) values (%s, %s, %s, %s, %s, %s, %s)"),[sell_order_executed_time, SELL_ORDER_SYMBOL, SELL_ORDER_ID, SELL_ORDER_ACTION, SELL_ORDER_TYPE, SELL_ORDER_PRICE, SELL_ORDER_QTY])
                    conn.commit()

                except Exception as e:
                    error_occured = f"{e}"
                    print(error_occured)

        def proceed_exit_short(req_position_type,SPOT_BUY_QUANTITY_EL,SPOT_SYMBOL,req_short_stop_loss_percent,req_short_take_profit_percent,req_multi_tp,req_tp1_percent,req_tp2_percent,req_tp3_percent,req_tp1_qty_size,req_tp2_qty_size,req_tp3_qty_size,req_order_time_out):

            SPOT_EXIT = "NA"
            SPOT_SIDE = "BUY"

            if req_short_stop_loss_percent == 0 and req_short_take_profit_percent == 0 and req_multi_tp == "No":
                SPOT_ENTRY = "MARKET"
                try:
                    exit_short_buy_order = client.create_order(symbol=SPOT_SYMBOL, side=SPOT_SIDE, type=SPOT_ENTRY,quantity=SPOT_BUY_QUANTITY_EL)
                    time.sleep(5)
                    print(f"exit_short_buy_order = {exit_short_buy_order}")
                except Exception as e:
                    error_occured = f"{e}"
                    print(error_occured)
                    error_occured_time = datetime.now()

                    cursor.execute("insert into error_log(symbol, order_action, entry_order_type, exit_order_type, quantity, occured_time, error_description) values (%s, %s, %s, %s, %s, %s, %s)",[SPOT_SYMBOL, SPOT_SIDE, SPOT_ENTRY, SPOT_EXIT, SPOT_BUY_QUANTITY_EL, error_occured_time,error_occured])
                    conn.commit()
                try:
                    BUY_ORDER_ID = exit_short_buy_order["orderId"]
                    BUY_ORDER_SYMBOL = exit_short_buy_order["symbol"]
                    commision_in_coin = 0
                    ask_qty = float(exit_short_buy_order["executedQty"])
                    try:
                        for fill in exit_short_buy_order["fills"]:
                            comm = float(fill["commission"])
                            commision_in_coin += comm
                    except:
                        commision_in_coin = ask_qty * 0.001
                    BUY_ORDER_QTY = ask_qty - commision_in_coin
                    TOTAL_BUY_SPEND = float(exit_short_buy_order["cummulativeQuoteQty"])
                    print(f"Total buy spend = {TOTAL_BUY_SPEND}")
                    BUY_ORDER_PRICE = float(exit_short_buy_order["cummulativeQuoteQty"]) / float(exit_short_buy_order["executedQty"])
                    BUY_ORDER_ACTION = exit_short_buy_order["side"]
                    BUY_ORDER_TYPE = exit_short_buy_order["type"]
                    buy_order_executed_time = datetime.now()

                    cursor.execute("select total_spend from short_entry where symbol = %s", [SPOT_SYMBOL])
                    r_3 = cursor.fetchall()
                    price_results = r_3[0][0]
                    previous_short_entry_income = float(price_results)
                    print(f"previous_buy_income = {previous_short_entry_income}")

                    cursor.execute("select qty from short_entry where symbol = %s", [SPOT_SYMBOL])
                    r_3 = cursor.fetchall()
                    price_results = r_3[0][0]
                    previous_short_entry_qty = float(price_results)
                    print(f"previous_short_entry_qty = {previous_short_entry_qty}")

                    actual_sell_income = (previous_short_entry_income/100)*99.9
                    proportional_sell_income = (actual_sell_income/previous_short_entry_qty) * BUY_ORDER_QTY
                    SHORT_BUY_PNL = round((proportional_sell_income - TOTAL_BUY_SPEND), 2)
                    short_buy_per = (SHORT_BUY_PNL / proportional_sell_income) * 100
                    SHORT_BUY_PNL_PERCENTAGE = str((round(short_buy_per, 2))) + "%"

                    cursor.execute(sql.SQL(
                        "insert into trade_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty, pnl, percentage) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"),
                                   [buy_order_executed_time, BUY_ORDER_SYMBOL, BUY_ORDER_ID, BUY_ORDER_ACTION, BUY_ORDER_TYPE,
                                    BUY_ORDER_PRICE, BUY_ORDER_QTY,SHORT_BUY_PNL,SHORT_BUY_PNL_PERCENTAGE])
                    conn.commit()

                except Exception as e:
                    print(e)




            if req_short_stop_loss_percent > 0 or req_short_take_profit_percent > 0 or req_multi_tp == "Yes":
                SPOT_ENTRY = "LIMIT"

                cursor.execute("select entry_price from short_entry where symbol = %s", [SPOT_SYMBOL])
                r_3 = cursor.fetchall()
                price_results = r_3[0][0]
                previous_short_entry_price = float(price_results)
                print(f"previous_short_entry_price= {previous_short_entry_price}")

                short_stop_loss_bp = previous_short_entry_price + (previous_short_entry_price * req_short_stop_loss_percent)

                short_take_profit_bp = previous_short_entry_price - (previous_short_entry_price * req_short_take_profit_percent)

                STOP_LOSS_PRICE_FINAL = cal_price_with_precision(SPOT_SYMBOL=SPOT_SYMBOL, input_price=short_stop_loss_bp)
                print(f"Stop loss price final = {STOP_LOSS_PRICE_FINAL}")

                TAKE_PROFIT_PRICE_FINAL = cal_price_with_precision(SPOT_SYMBOL=SPOT_SYMBOL, input_price=short_take_profit_bp)
                print(f"Take profit price final = {TAKE_PROFIT_PRICE_FINAL}")

                BUY_ORDER_ID = 0

                if req_multi_tp == "No":
                    if req_short_stop_loss_percent > 0 and req_short_take_profit_percent > 0:
                        execute_limit_oco_order(SPOT_SIDE=SPOT_SIDE,req_position_type=req_position_type, BUY_ORDER_ID=BUY_ORDER_ID,
                                                SPOT_SYMBOL=SPOT_SYMBOL, SPOT_SELL_QUANTITY=SPOT_BUY_QUANTITY_EL,
                                                TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL,
                                                STOP_LOSS_PRICE_FINAL=STOP_LOSS_PRICE_FINAL, SPOT_ENTRY=SPOT_ENTRY,
                                                req_multi_tp=req_multi_tp, req_qty_size=0,req_order_time_out=req_order_time_out)
                    elif req_short_stop_loss_percent > 0 and (
                            req_short_take_profit_percent == "" or req_short_take_profit_percent == 0):
                        execute_limit_stop_loss_order(SPOT_SIDE,req_position_type, BUY_ORDER_ID, SPOT_SYMBOL, SPOT_BUY_QUANTITY_EL,
                                                      STOP_LOSS_PRICE_FINAL, SPOT_ENTRY,req_order_time_out)
                    elif req_short_take_profit_percent > 0 and (
                            req_short_stop_loss_percent == "" or req_short_stop_loss_percent == 0):
                        execute_limit_take_profit_order(SPOT_SIDE=SPOT_SIDE,req_position_type=req_position_type, BUY_ORDER_ID=BUY_ORDER_ID,
                                                        SPOT_SYMBOL=SPOT_SYMBOL, SPOT_SELL_QUANTITY=SPOT_BUY_QUANTITY_EL,
                                                        TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL, SPOT_ENTRY=SPOT_ENTRY,
                                                        req_multi_tp=req_multi_tp, req_qty_size=0,req_order_time_out=req_order_time_out)

                if req_multi_tp == "Yes":
                    SELLABLE_1 = calculate_sell_qty_with_precision(SPOT_SYMBOL, (SPOT_BUY_QUANTITY_EL * req_tp1_qty_size))
                    print(f"Sellable qty_1 = {SELLABLE_1}")
                    SELLABLE_2 = calculate_sell_qty_with_precision(SPOT_SYMBOL, (SPOT_BUY_QUANTITY_EL * req_tp2_qty_size))
                    print(f"Sellable qty_2 = {SELLABLE_2}")
                    SELLABLE_3 = calculate_sell_qty_with_precision(SPOT_SYMBOL, (SPOT_BUY_QUANTITY_EL * req_tp3_qty_size))
                    print(f"Sellable qty_3 = {SELLABLE_3}")

                    short_take_profit_bp_1 = previous_short_entry_price - (previous_short_entry_price * req_tp1_percent)
                    short_take_profit_bp_2 = previous_short_entry_price - (previous_short_entry_price * req_tp2_percent)
                    short_take_profit_bp_3 = previous_short_entry_price - (previous_short_entry_price * req_tp3_percent)
                    TAKE_PROFIT_PRICE_FINAL_1 = cal_price_with_precision(SPOT_SYMBOL=SPOT_SYMBOL,
                                                                         input_price=short_take_profit_bp_1)
                    TAKE_PROFIT_PRICE_FINAL_2 = cal_price_with_precision(SPOT_SYMBOL=SPOT_SYMBOL,
                                                                         input_price=short_take_profit_bp_2)
                    TAKE_PROFIT_PRICE_FINAL_3 = cal_price_with_precision(SPOT_SYMBOL=SPOT_SYMBOL,
                                                                         input_price=short_take_profit_bp_3)
                    print(f"Take profit price final_1 = {TAKE_PROFIT_PRICE_FINAL_1}")
                    print(f"Take profit price final_2 = {TAKE_PROFIT_PRICE_FINAL_2}")
                    print(f"Take profit price final_3 = {TAKE_PROFIT_PRICE_FINAL_3}")

                    if req_short_stop_loss_percent > 0 and (req_tp1_percent > 0 or req_tp2_percent > 0 or req_tp3_percent > 0):
                        if req_tp1_percent > 0:
                            t1 = threading.Thread(target=lambda: execute_limit_oco_order(SPOT_SIDE=SPOT_SIDE,req_position_type=req_position_type,
                                                                                         BUY_ORDER_ID=BUY_ORDER_ID,
                                                                                         SPOT_SYMBOL=SPOT_SYMBOL,
                                                                                         SPOT_SELL_QUANTITY=SELLABLE_1,
                                                                                         TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL_1,
                                                                                         STOP_LOSS_PRICE_FINAL=STOP_LOSS_PRICE_FINAL,
                                                                                         SPOT_ENTRY=SPOT_ENTRY,
                                                                                         req_multi_tp=req_multi_tp,
                                                                                         req_qty_size=req_tp1_qty_size,req_order_time_out=req_order_time_out))
                            t1.start()
                        if req_tp2_percent > 0:
                            t2 = threading.Thread(target=lambda: execute_limit_oco_order(SPOT_SIDE=SPOT_SIDE,req_position_type=req_position_type,
                                                                                         BUY_ORDER_ID=BUY_ORDER_ID,
                                                                                         SPOT_SYMBOL=SPOT_SYMBOL,
                                                                                         SPOT_SELL_QUANTITY=SELLABLE_2,
                                                                                         TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL_2,
                                                                                         STOP_LOSS_PRICE_FINAL=STOP_LOSS_PRICE_FINAL,
                                                                                         SPOT_ENTRY=SPOT_ENTRY,
                                                                                         req_multi_tp=req_multi_tp,
                                                                                         req_qty_size=req_tp2_qty_size,req_order_time_out=req_order_time_out))
                            t2.start()
                        if req_tp3_percent > 0:
                            t3 = threading.Thread(target=lambda: execute_limit_oco_order(SPOT_SIDE=SPOT_SIDE,req_position_type=req_position_type,
                                                                                         BUY_ORDER_ID=BUY_ORDER_ID,
                                                                                         SPOT_SYMBOL=SPOT_SYMBOL,
                                                                                         SPOT_SELL_QUANTITY=SELLABLE_3,
                                                                                         TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL_3,
                                                                                         STOP_LOSS_PRICE_FINAL=STOP_LOSS_PRICE_FINAL,
                                                                                         SPOT_ENTRY=SPOT_ENTRY,
                                                                                         req_multi_tp=req_multi_tp,
                                                                                         req_qty_size=req_tp3_qty_size,req_order_time_out=req_order_time_out))
                            t3.start()


                    elif req_short_stop_loss_percent > 0 and (req_tp1_percent == 0 and req_tp2_percent == 0 and req_tp3_percent == 0):
                        execute_limit_stop_loss_order(SPOT_SIDE,req_position_type, BUY_ORDER_ID, SPOT_SYMBOL, SPOT_BUY_QUANTITY_EL,
                                                      STOP_LOSS_PRICE_FINAL, SPOT_ENTRY,req_order_time_out)


                    elif (req_tp1_percent > 0 or req_tp2_percent > 0 or req_tp3_percent > 0) and (req_short_stop_loss_percent == "" or req_short_stop_loss_percent == 0):
                        if req_tp1_percent > 0:
                            t1 = threading.Thread(
                                target=lambda: execute_limit_take_profit_order(SPOT_SIDE=SPOT_SIDE,req_position_type=req_position_type,
                                                                               BUY_ORDER_ID=BUY_ORDER_ID,
                                                                               SPOT_SYMBOL=SPOT_SYMBOL,
                                                                               SPOT_SELL_QUANTITY=SELLABLE_1,
                                                                               TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL_1,
                                                                               SPOT_ENTRY=SPOT_ENTRY, req_multi_tp=req_multi_tp,
                                                                               req_qty_size=req_tp1_qty_size,req_order_time_out=req_order_time_out))
                            t1.start()
                        if req_tp2_percent > 0:
                            t2 = threading.Thread(
                                target=lambda: execute_limit_take_profit_order(SPOT_SIDE=SPOT_SIDE,req_position_type=req_position_type,
                                                                               BUY_ORDER_ID=BUY_ORDER_ID,
                                                                               SPOT_SYMBOL=SPOT_SYMBOL,
                                                                               SPOT_SELL_QUANTITY=SELLABLE_2,
                                                                               TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL_2,
                                                                               SPOT_ENTRY=SPOT_ENTRY, req_multi_tp=req_multi_tp,
                                                                               req_qty_size=req_tp2_qty_size,req_order_time_out=req_order_time_out))
                            t2.start()
                        if req_tp3_percent > 0:
                            t3 = threading.Thread(
                                target=lambda: execute_limit_take_profit_order(SPOT_SIDE=SPOT_SIDE,req_position_type=req_position_type,
                                                                               BUY_ORDER_ID=BUY_ORDER_ID,
                                                                               SPOT_SYMBOL=SPOT_SYMBOL,
                                                                               SPOT_SELL_QUANTITY=SELLABLE_3,
                                                                               TAKE_PROFIT_PRICE_FINAL=TAKE_PROFIT_PRICE_FINAL_3,
                                                                               SPOT_ENTRY=SPOT_ENTRY, req_multi_tp=req_multi_tp,
                                                                               req_qty_size=req_tp2_qty_size,req_order_time_out=req_order_time_out))
                            t3.start()


        # Stop bot if balance is below user defined amount

        if req_stop_bot_balance != 0:
            if check_base_coin_balance() > req_stop_bot_balance:
                # Check order position
                if req_position_type == "Enter_long":
                    SPOT_BUY_QUANTITY = calculate_buy_qty_with_precision(SPOT_SYMBOL, qty_in_base_coin)
                    proceed_enter_long(SPOT_BUY_QUANTITY,SPOT_SYMBOL,SPOT_ENTRY,req_long_stop_loss_percent,req_long_take_profit_percent,req_multi_tp,req_tp1_percent,req_tp2_percent,req_tp3_percent,req_tp1_qty_size,req_tp2_qty_size,req_tp3_qty_size,req_order_time_out)

                elif req_position_type == "Exit_short":
                    SPOT_BUY_QUANTITY_EL = calculate_buy_qty_with_precision(SPOT_SYMBOL, qty_in_base_coin)
                    proceed_exit_short(req_position_type, SPOT_BUY_QUANTITY_EL, SPOT_SYMBOL,req_short_stop_loss_percent,
                                      req_short_take_profit_percent, req_multi_tp, req_tp1_percent, req_tp2_percent,
                                      req_tp3_percent, req_tp1_qty_size, req_tp2_qty_size, req_tp3_qty_size,
                                      req_order_time_out)

                elif req_position_type == "Exit_long":
                    SPOT_SELL_QUANTITY_EL = calculate_buy_qty_with_precision(SPOT_SYMBOL, qty_in_base_coin)
                    proceed_exit_long(req_position_type,SPOT_SELL_QUANTITY_EL, SPOT_SYMBOL, req_long_stop_loss_percent,
                                       req_long_take_profit_percent, req_multi_tp, req_tp1_percent, req_tp2_percent,
                                       req_tp3_percent, req_tp1_qty_size, req_tp2_qty_size, req_tp3_qty_size,
                                       req_order_time_out)

                elif req_position_type == "Enter_short":
                    SPOT_SELL_QUANTITY_EL = calculate_buy_qty_with_precision(SPOT_SYMBOL, qty_in_base_coin)
                    proceed_enter_short(req_position_type, SPOT_SELL_QUANTITY_EL, SPOT_SYMBOL, req_short_stop_loss_percent,
                     req_short_take_profit_percent, req_multi_tp, req_tp1_percent, req_tp2_percent, req_tp3_percent,
                     req_tp1_qty_size, req_tp2_qty_size, req_tp3_qty_size, req_order_time_out)

        else:
            error_occured_time = datetime.now()
            error_occured = "Cant initiate the trade! Wallet balance is low!"
            cursor.execute("insert into error_log(occured_time, error_description) values (%s, %s)",[error_occured_time, error_occured])
            conn.commit()
except Exception as e:
    print(e)
    error_occured_time = datetime.now()
    error_occured = "Error in initiating Spot Order!"
    cursor.execute(
        "insert into error_log(occured_time, error_description) values (%s, %s)",
        [error_occured_time, error_occured])
    conn.commit()


if req_trade_type == "Futures":
    try:
        FUTURES_SYMBOL = req_coin_pair
        FUTURES_ENTRY = req_entry_type
        FUTURES_EXIT = req_exit_type
    except:
        pass

    def futures_calculate_buy_qty_with_precision(FUTURES_SYMBOL, qty_in_base_coin):
        prices = client.get_all_tickers()
        for ticker in prices:
            if ticker["symbol"] == FUTURES_SYMBOL:
                current_market_price = float(ticker["price"])
                break
        tradeable_qty = qty_in_base_coin / current_market_price
        info = client.get_symbol_info(FUTURES_SYMBOL)
        for x in info["filters"]:
            if x["filterType"] == "LOT_SIZE":
                stepSize = float(x["stepSize"])
                print(f"step size = {stepSize}")

        truncate_num = math.log10(1 / stepSize)
        BUY_QUANTITY = math.floor((tradeable_qty) * 10 ** truncate_num) / 10 ** truncate_num
        return BUY_QUANTITY

    def futures_calculate_sell_qty_with_precision(SPOT_SYMBOL, buy_qty):
        info = client.get_symbol_info(SPOT_SYMBOL)
        for x in info["filters"]:
            if x["filterType"] == "LOT_SIZE":
                stepSize = float(x["stepSize"])
                print(f"step size = {stepSize}")

        truncate_num = math.log10(1 / stepSize)
        SELL_QUANTITY = math.floor((buy_qty) * 10 ** truncate_num) / 10 ** truncate_num
        return SELL_QUANTITY


    def futures_cal_price_with_precision(FUTURES_SYMBOL, input_price):
        info = client.futures_exchange_info()
        for sym in info["symbols"]:
            if (sym["symbol"] == FUTURES_SYMBOL):
                price_precision = int(sym["pricePrecision"])
                break
        price = round(input_price, price_precision)
        return price


    def get_opened_position(FUTURES_SYMBOL):
        the_pos = ""
        all_positions = client.futures_position_information()
        for open_pos in all_positions:
            amt = round(float(open_pos["positionAmt"]))
            if (open_pos["symbol"] == FUTURES_SYMBOL and amt != 0):
                the_pos = open_pos
                break
        return the_pos


    def check_pnl(FUTURES_SYMBOL, stoploss_order_id, tp_order_id, tp_order_id_1, tp_order_id_2, tp_order_id_3,
                  exit_side, FUTURES_QUANTITY, req_multi_tp):
        executed_order_sl = ""
        executed_order_tp = ""
        executed_order1 = ""
        executed_order2 = ""
        executed_order3 = ""
        executed_order_liq = ""
        futures_trade_info = client.futures_account_trades(symbol=FUTURES_SYMBOL)
        for trade in reversed(futures_trade_info):
            if trade["orderId"] == stoploss_order_id:
                executed_order_sl = trade
            if req_multi_tp == "No":
                if trade["orderId"] == tp_order_id:
                    executed_order_tp = trade
            if req_multi_tp == "Yes":
                if trade["orderId"] == tp_order_id_1:
                    executed_order1 = trade
                if trade["orderId"] == tp_order_id_2:
                    executed_order2 = trade
                if trade["orderId"] == tp_order_id_3:
                    executed_order3 = trade
        if executed_order_sl == "" and executed_order_tp == "" and executed_order1 == "" and executed_order2 == "" and executed_order3 == "":
            for rev_trade in reversed(futures_trade_info):
                if rev_trade["symbol"] == FUTURES_SYMBOL and rev_trade["side"] == exit_side and rev_trade["qty"] == FUTURES_QUANTITY:
                    executed_order_liq = rev_trade
                    break
        else:
            pass

        if executed_order_sl != "":
            realized_pnl = float(executed_order_sl["realizedPnl"])
            exit_order_commission = float(executed_order_sl["commission"])

            if executed_order_sl["commissionAsset"] == "USDT":
                total_pnl = round((realized_pnl - exit_order_commission), 6)
            else:
                prices = client.get_all_tickers()
                bc = executed_order_sl["commissionAsset"]
                for ticker in prices:
                    if ticker["symbol"] == bc + "USDT":
                        current_market_price = float(ticker["price"])
                        break
                total_pnl = round(((realized_pnl - exit_order_commission) * current_market_price), 6)

            FINAL_ORDER_ID = executed_order_sl["orderId"]
            FINAL_ORDER_SYMBOL = executed_order_sl["symbol"]
            FINAL_ORDER_QTY = float(executed_order_sl["qty"])
            FINAL_ORDER_PRICE = float(executed_order_sl["price"])
            FINAL_ORDER_ACTION = executed_order_sl["side"]
            FINAL_ORDER_TYPE = "LIMIT"
            final_order_executed_time = datetime.now()

            cursor.execute(sql.SQL(
                "insert into futures_t_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty,pnl) values (%s, %s, %s, %s, %s, %s, %s,%s)"),
                [final_order_executed_time, FINAL_ORDER_SYMBOL, FINAL_ORDER_ID, FINAL_ORDER_ACTION,
                 FINAL_ORDER_TYPE, FINAL_ORDER_PRICE, FINAL_ORDER_QTY, total_pnl])
            conn.commit()

        if executed_order_tp != "":
            realized_pnl = float(executed_order_tp["realizedPnl"])
            exit_order_commission = float(executed_order_tp["commission"])

            if executed_order_tp["commissionAsset"] == "USDT":
                total_pnl = round((realized_pnl - exit_order_commission), 6)
            else:
                prices = client.get_all_tickers()
                bc = executed_order_tp["commissionAsset"]
                for ticker in prices:
                    if ticker["symbol"] == bc + "USDT":
                        current_market_price = float(ticker["price"])
                        break
                total_pnl = round(((realized_pnl - exit_order_commission) * current_market_price), 6)

            FINAL_ORDER_ID = executed_order_tp["orderId"]
            FINAL_ORDER_SYMBOL = executed_order_tp["symbol"]
            FINAL_ORDER_QTY = float(executed_order_tp["qty"])
            FINAL_ORDER_PRICE = float(executed_order_tp["price"])
            FINAL_ORDER_ACTION = executed_order_tp["side"]
            FINAL_ORDER_TYPE = "LIMIT"
            final_order_executed_time = datetime.now()

            cursor.execute(sql.SQL(
                "insert into futures_t_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty,pnl) values (%s, %s, %s, %s, %s, %s, %s,%s)"),
                [final_order_executed_time, FINAL_ORDER_SYMBOL, FINAL_ORDER_ID, FINAL_ORDER_ACTION,
                 FINAL_ORDER_TYPE, FINAL_ORDER_PRICE, FINAL_ORDER_QTY, total_pnl])
            conn.commit()

        if executed_order1 != "":
            realized_pnl = float(executed_order1["realizedPnl"])
            exit_order_commission = float(executed_order1["commission"])

            if executed_order1["commissionAsset"] == "USDT":
                total_pnl = round((realized_pnl - exit_order_commission), 6)
            else:
                prices = client.get_all_tickers()
                bc = executed_order1["commissionAsset"]
                for ticker in prices:
                    if ticker["symbol"] == bc + "USDT":
                        current_market_price = float(ticker["price"])
                        break
                total_pnl = round(((realized_pnl - exit_order_commission) * current_market_price), 6)

            FINAL_ORDER_ID = executed_order1["orderId"]
            FINAL_ORDER_SYMBOL = executed_order1["symbol"]
            FINAL_ORDER_QTY = float(executed_order1["qty"])
            FINAL_ORDER_PRICE = float(executed_order1["price"])
            FINAL_ORDER_ACTION = executed_order1["side"]
            FINAL_ORDER_TYPE = "LIMIT"
            final_order_executed_time = datetime.now()

            cursor.execute(sql.SQL(
                "insert into futures_t_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty,pnl) values (%s, %s, %s, %s, %s, %s, %s,%s)"),
                [final_order_executed_time, FINAL_ORDER_SYMBOL, FINAL_ORDER_ID, FINAL_ORDER_ACTION,
                 FINAL_ORDER_TYPE, FINAL_ORDER_PRICE, FINAL_ORDER_QTY, total_pnl])
            conn.commit()

        if executed_order2 != "":
            realized_pnl = float(executed_order2["realizedPnl"])
            exit_order_commission = float(executed_order2["commission"])

            if executed_order2["commissionAsset"] == "USDT":
                total_pnl = round((realized_pnl - exit_order_commission), 6)
            else:
                prices = client.get_all_tickers()
                bc = executed_order2["commissionAsset"]
                for ticker in prices:
                    if ticker["symbol"] == bc + "USDT":
                        current_market_price = float(ticker["price"])
                        break
                total_pnl = round(((realized_pnl - exit_order_commission) * current_market_price), 6)

            FINAL_ORDER_ID = executed_order2["orderId"]
            FINAL_ORDER_SYMBOL = executed_order2["symbol"]
            FINAL_ORDER_QTY = float(executed_order2["qty"])
            FINAL_ORDER_PRICE = float(executed_order2["price"])
            FINAL_ORDER_ACTION = executed_order2["side"]
            FINAL_ORDER_TYPE = "LIMIT"
            final_order_executed_time = datetime.now()

            cursor.execute(sql.SQL(
                "insert into futures_t_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty,pnl) values (%s, %s, %s, %s, %s, %s, %s,%s)"),
                [final_order_executed_time, FINAL_ORDER_SYMBOL, FINAL_ORDER_ID, FINAL_ORDER_ACTION,
                 FINAL_ORDER_TYPE, FINAL_ORDER_PRICE, FINAL_ORDER_QTY, total_pnl])
            conn.commit()

        if executed_order3 != "":
            realized_pnl = float(executed_order3["realizedPnl"])
            exit_order_commission = float(executed_order3["commission"])

            if executed_order3["commissionAsset"] == "USDT":
                total_pnl = round((realized_pnl - exit_order_commission), 6)
            else:
                prices = client.get_all_tickers()
                bc = executed_order3["commissionAsset"]
                for ticker in prices:
                    if ticker["symbol"] == bc + "USDT":
                        current_market_price = float(ticker["price"])
                        break
                total_pnl = round(((realized_pnl - exit_order_commission) * current_market_price), 6)

            FINAL_ORDER_ID = executed_order3["orderId"]
            FINAL_ORDER_SYMBOL = executed_order3["symbol"]
            FINAL_ORDER_QTY = float(executed_order3["qty"])
            FINAL_ORDER_PRICE = float(executed_order3["price"])
            FINAL_ORDER_ACTION = executed_order3["side"]
            FINAL_ORDER_TYPE = "LIMIT"
            final_order_executed_time = datetime.now()

            cursor.execute(sql.SQL(
                "insert into futures_t_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty,pnl) values (%s, %s, %s, %s, %s, %s, %s,%s)"),
                [final_order_executed_time, FINAL_ORDER_SYMBOL, FINAL_ORDER_ID, FINAL_ORDER_ACTION,
                 FINAL_ORDER_TYPE, FINAL_ORDER_PRICE, FINAL_ORDER_QTY, total_pnl])
            conn.commit()

        if executed_order_liq != "":
            realized_pnl = float(executed_order_liq["realizedPnl"])
            exit_order_commission = float(executed_order_liq["commission"])

            if executed_order_liq["commissionAsset"] == "USDT":
                total_pnl = round((realized_pnl - exit_order_commission), 6)
            else:
                prices = client.get_all_tickers()
                bc = executed_order_liq["commissionAsset"]
                for ticker in prices:
                    if ticker["symbol"] == bc + "USDT":
                        current_market_price = float(ticker["price"])
                        break
                total_pnl = round(((realized_pnl - exit_order_commission) * current_market_price), 6)

            FINAL_ORDER_ID = executed_order_liq["orderId"]
            FINAL_ORDER_SYMBOL = executed_order_liq["symbol"]
            FINAL_ORDER_QTY = float(executed_order_liq["qty"])
            FINAL_ORDER_PRICE = float(executed_order_liq["price"])
            FINAL_ORDER_ACTION = executed_order_liq["side"]
            FINAL_ORDER_TYPE = "LIMIT"
            final_order_executed_time = datetime.now()

            cursor.execute(sql.SQL(
                "insert into futures_t_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty,pnl) values (%s, %s, %s, %s, %s, %s, %s,%s)"),
                [final_order_executed_time, FINAL_ORDER_SYMBOL, FINAL_ORDER_ID, FINAL_ORDER_ACTION,
                 FINAL_ORDER_TYPE, FINAL_ORDER_PRICE, FINAL_ORDER_QTY, total_pnl])
            conn.commit()


    def check_exit_status(FUTURES_SYMBOL, stoploss_order_id, tp_order_id, tp_order_id_1, tp_order_id_2, tp_order_id_3,
                          exit_side, FUTURES_QUANTITY, req_multi_tp):
        while True:
            time.sleep(1)
            pos_result = get_opened_position(FUTURES_SYMBOL)
            if pos_result == "":
                check_pnl(FUTURES_SYMBOL, stoploss_order_id, tp_order_id, tp_order_id_1, tp_order_id_2, tp_order_id_3,
                          exit_side, FUTURES_QUANTITY, req_multi_tp)
                break


    def enter_order(FUTURES_ENTRY, FUTURES_SYMBOL, side, FUTURES_QUANTITY, req_order_time_out,
                    req_long_stop_loss_percent, req_long_take_profit_percent, req_short_stop_loss_percent,
                    req_short_take_profit_percent, req_multi_tp, req_tp1_qty_size, req_tp2_qty_size, req_tp3_qty_size,
                    req_tp1_percent, req_tp2_percent, req_tp3_percent):

        if FUTURES_ENTRY == "MARKET":

            try:
                futures_order = client.futures_create_order(symbol=FUTURES_SYMBOL, side=side, type='MARKET',
                                                            quantity=FUTURES_QUANTITY)
                print(f"futures order = {futures_order}")
                order_id = futures_order["orderId"]
            except Exception as e:
                error_occured = f"{e}"
                print(error_occured)
                error_occured_time = datetime.now()

                cursor.execute(
                    "insert into futures_e_log(symbol, order_action, entry_order_type, quantity, occured_time, error_description) values (%s, %s, %s, %s, %s, %s)",
                    [FUTURES_SYMBOL, side, FUTURES_ENTRY, FUTURES_QUANTITY, error_occured_time, error_occured])
                conn.commit()

            time.sleep(2)

        elif FUTURES_ENTRY == "LIMIT":
            prices = client.get_all_tickers()
            for ticker in prices:
                if ticker["symbol"] == FUTURES_SYMBOL:
                    last_price = float(ticker["price"])
                    break

            try:
                futures_order = client.futures_create_order(symbol=FUTURES_SYMBOL, side=side, type='LIMIT',
                                                            quantity=FUTURES_QUANTITY, price=last_price,
                                                            timeInForce='GTC')
                print(f"futures order = {futures_order}")
                order_id = futures_order["orderId"]
            except Exception as e:
                error_occured = f"{e}"
                print(error_occured)
                error_occured_time = datetime.now()

                cursor.execute(
                    "insert into futures_e_log(symbol, order_action, entry_order_type, quantity, occured_time, error_description) values (%s, %s, %s, %s, %s, %s)",
                    [FUTURES_SYMBOL, side, FUTURES_ENTRY, FUTURES_QUANTITY, error_occured_time, error_occured])
                conn.commit()

        # Loop and check if entry order is filled
        entry_order_timeout_start = time.time()

        while time.time() < (entry_order_timeout_start + req_order_time_out):
            try:
                active_order = client.futures_get_order(symbol=FUTURES_SYMBOL, orderId=order_id)
                active_order_status = active_order["status"]
                if active_order_status == "FILLED":
                    break
            except:
                pass
        if active_order_status == "FILLED":
            postioned_order = client.futures_get_order(symbol=FUTURES_SYMBOL, orderId=order_id)
            print(f"postioned futures order = {postioned_order}")
        else:
            check_for_partial = client.futures_get_order(symbol=FUTURES_SYMBOL, orderId=order_id)
            if check_for_partial["status"] == "PARTIALLY_FILLED":
                postioned_order = check_for_partial
            check_for_cancel = client.futures_get_order(symbol=FUTURES_SYMBOL, orderId=order_id)
            if check_for_cancel["status"] == "CANCELED" or check_for_cancel["status"] != "PARTIALLY_FILLED" or check_for_cancel["status"] != "FILLED":
                print("Already cancelled")
            else:
                cancel_futures_limit_order = client.futures_cancel_order(symbol=FUTURES_SYMBOL, orderId=order_id)
            error_occured = "Order time limit reached! Pending open limit orders has been cancelled"
            print(error_occured)
            error_occured_time = datetime.now()
            cursor.execute(
                "insert into futures_e_log(symbol, order_action, entry_order_type, quantity, occured_time, error_description) values (%s, %s, %s, %s, %s, %s)",
                [FUTURES_SYMBOL, side, FUTURES_ENTRY, FUTURES_QUANTITY, error_occured_time, error_occured])
            conn.commit()

        entry_price = float(postioned_order["avgPrice"])
        print(f"entry price = {entry_price}")

        INITIAL_ORDER_ID = postioned_order["orderId"]
        INITIAL_ORDER_SYMBOL = postioned_order["symbol"]
        INITIAL_ORDER_QTY = float(postioned_order["executedQty"])
        INITIAL_ORDER_PRICE = float(postioned_order["avgPrice"])
        INITIAL_ORDER_ACTION = postioned_order["side"]
        INITIAL_ORDER_TYPE = postioned_order["type"]
        initial_order_executed_time = datetime.now()

        live_trades_list = client.futures_account_trades(symbol=FUTURES_SYMBOL)
        for live_trade in reversed(live_trades_list):
            if live_trade['orderId'] == INITIAL_ORDER_ID:
                if live_trade["commissionAsset"] == "USDT":
                    entry_order_commission = (float(live_trade["commission"])) * -1
                else:
                    prices = client.get_all_tickers()
                    bc = live_trade["commissionAsset"]
                    for ticker in prices:
                        if ticker["symbol"] == bc + "USDT":
                            current_market_price = float(ticker["price"])
                            break
                    entry_order_commission = ((float(live_trade["commission"])) * -1) * current_market_price

                break

        cursor.execute(sql.SQL(
            "insert into futures_t_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty, pnl) values (%s, %s, %s, %s, %s, %s, %s,%s)"),
            [initial_order_executed_time, INITIAL_ORDER_SYMBOL, INITIAL_ORDER_ID, INITIAL_ORDER_ACTION,
             INITIAL_ORDER_TYPE, INITIAL_ORDER_PRICE, INITIAL_ORDER_QTY, entry_order_commission])
        conn.commit()

        if req_long_stop_loss_percent > 0 or req_long_take_profit_percent > 0 or req_multi_tp == "Yes" or req_short_stop_loss_percent > 0 or req_short_take_profit_percent > 0:
            # Assign leverage for quantity calculation
            FUTURES_EXIT = "LIMIT"
            if side == "BUY":
                exit_side = "SELL"
                short_stop_loss_bp = entry_price - (entry_price * req_short_stop_loss_percent)

                STOP_LOSS_PRICE_FINAL = futures_cal_price_with_precision(FUTURES_SYMBOL=FUTURES_SYMBOL,
                                                                 input_price=short_stop_loss_bp)
                print(f"Stop loss price final = {STOP_LOSS_PRICE_FINAL}")

                if req_multi_tp == "No":
                    short_take_profit_bp = entry_price + (entry_price * req_short_take_profit_percent)
                    TAKE_PROFIT_PRICE_FINAL = futures_cal_price_with_precision(FUTURES_SYMBOL=FUTURES_SYMBOL,
                                                                       input_price=short_take_profit_bp)
                    print(f"Take profit price final = {TAKE_PROFIT_PRICE_FINAL}")

                elif req_multi_tp == "Yes":
                    SELLABLE_1 = futures_calculate_sell_qty_with_precision(FUTURES_SYMBOL=FUTURES_SYMBOL,qty_in_base_coin=(FUTURES_QUANTITY * req_tp1_qty_size))
                    print(f"Sellable qty_1 = {SELLABLE_1}")
                    SELLABLE_2 = futures_calculate_sell_qty_with_precision(FUTURES_SYMBOL=FUTURES_SYMBOL,qty_in_base_coin=(FUTURES_QUANTITY * req_tp2_qty_size))
                    print(f"Sellable qty_2 = {SELLABLE_2}")
                    SELLABLE_3 = futures_calculate_sell_qty_with_precision(FUTURES_SYMBOL=FUTURES_SYMBOL,qty_in_base_coin=(FUTURES_QUANTITY * req_tp3_qty_size))
                    print(f"Sellable qty_3 = {SELLABLE_3}")

                    short_take_profit_bp_1 = entry_price + (entry_price * req_tp1_percent)
                    short_take_profit_bp_2 = entry_price + (entry_price * req_tp2_percent)
                    short_take_profit_bp_3 = entry_price + (entry_price * req_tp3_percent)
                    TAKE_PROFIT_PRICE_FINAL_1 = futures_cal_price_with_precision(FUTURES_SYMBOL=FUTURES_SYMBOL,
                                                                         input_price=short_take_profit_bp_1)
                    TAKE_PROFIT_PRICE_FINAL_2 = futures_cal_price_with_precision(FUTURES_SYMBOL=FUTURES_SYMBOL,
                                                                         input_price=short_take_profit_bp_2)
                    TAKE_PROFIT_PRICE_FINAL_3 = futures_cal_price_with_precision(FUTURES_SYMBOL=FUTURES_SYMBOL,
                                                                         input_price=short_take_profit_bp_3)

            elif side == "SELL":
                exit_side = "BUY"
                long_stop_loss_bp = entry_price + (entry_price * req_long_stop_loss_percent)
                STOP_LOSS_PRICE_FINAL = futures_cal_price_with_precision(FUTURES_SYMBOL=FUTURES_SYMBOL,
                                                                 input_price=long_stop_loss_bp)
                print(f"Stop loss price final = {STOP_LOSS_PRICE_FINAL}")

                if req_multi_tp == "No":
                    long_take_profit_bp = entry_price - (entry_price * req_long_take_profit_percent)
                    TAKE_PROFIT_PRICE_FINAL = futures_cal_price_with_precision(FUTURES_SYMBOL=FUTURES_SYMBOL,
                                                                       input_price=long_take_profit_bp)
                    print(f"Take profit price final = {TAKE_PROFIT_PRICE_FINAL}")

                elif req_multi_tp == "Yes":
                    SELLABLE_1 = futures_calculate_sell_qty_with_precision(FUTURES_SYMBOL=FUTURES_SYMBOL,qty_in_base_coin=(FUTURES_QUANTITY * req_tp1_qty_size))
                    print(f"Sellable qty_1 = {SELLABLE_1}")
                    SELLABLE_2 = futures_calculate_sell_qty_with_precision(FUTURES_SYMBOL=FUTURES_SYMBOL,qty_in_base_coin=(FUTURES_QUANTITY * req_tp2_qty_size))
                    print(f"Sellable qty_2 = {SELLABLE_2}")
                    SELLABLE_3 = futures_calculate_sell_qty_with_precision(FUTURES_SYMBOL=FUTURES_SYMBOL,qty_in_base_coin=(FUTURES_QUANTITY * req_tp3_qty_size))
                    print(f"Sellable qty_3 = {SELLABLE_3}")

                    long_take_profit_bp_1 = entry_price - (entry_price * req_tp1_percent)
                    long_take_profit_bp_2 = entry_price - (entry_price * req_tp2_percent)
                    long_take_profit_bp_3 = entry_price - (entry_price * req_tp3_percent)
                    TAKE_PROFIT_PRICE_FINAL_1 = futures_cal_price_with_precision(FUTURES_SYMBOL=FUTURES_SYMBOL,
                                                                         input_price=long_take_profit_bp_1)
                    TAKE_PROFIT_PRICE_FINAL_2 = futures_cal_price_with_precision(FUTURES_SYMBOL=FUTURES_SYMBOL,
                                                                         input_price=long_take_profit_bp_2)
                    TAKE_PROFIT_PRICE_FINAL_3 = futures_cal_price_with_precision(FUTURES_SYMBOL=FUTURES_SYMBOL,
                                                                         input_price=long_take_profit_bp_3)

            try:
                stoploss_order = client.futures_create_order(symbol=FUTURES_SYMBOL, side=exit_side, type='STOP_MARKET',
                                                             stopPrice=STOP_LOSS_PRICE_FINAL,
                                                             closePosition="true")
                print(stoploss_order)
                stoploss_order_id = stoploss_order["orderId"]

                cursor.execute("insert into f_id_list(order_id, entry_price, qty) values (%s, %s,  %s)",
                               [stoploss_order_id, entry_price, INITIAL_ORDER_QTY])
                conn.commit()

            except Exception as e:
                error_occured = f"{e}"
                print(error_occured)
                error_occured_time = datetime.now()

                cursor.execute(
                    "insert into futures_e_log(symbol, order_action, entry_order_type, exit_order_type, quantity, occured_time, error_description) values (%s, %s, %s, %s, %s, %s, %s)",
                    [FUTURES_SYMBOL, exit_side, FUTURES_ENTRY, FUTURES_EXIT, FUTURES_QUANTITY, error_occured_time,
                     error_occured])
                conn.commit()

            if req_multi_tp == "No":
                tp_order_id_1 = 0
                tp_order_id_2 = 0
                tp_order_id_3 = 0
                try:
                    take_profit_order = client.futures_create_order(symbol=FUTURES_SYMBOL, side=exit_side,
                                                                    type='TAKE_PROFIT_MARKET',
                                                                    stopPrice=TAKE_PROFIT_PRICE_FINAL,
                                                                    closePosition="true")
                    print(take_profit_order)
                    tp_order_id = take_profit_order["orderId"]

                    cursor.execute("insert into f_id_list(order_id, entry_price,qty) values (%s, %s,%s)",
                                   [tp_order_id, entry_price,INITIAL_ORDER_QTY])
                    conn.commit()

                except Exception as e:
                    error_occured = f"{e}"
                    print(error_occured)
                    error_occured_time = datetime.now()

                    cursor.execute(
                        "insert into futures_e_log(symbol, order_action, entry_order_type, exit_order_type, quantity, occured_time, error_description) values (%s, %s, %s, %s, %s, %s, %s)",
                        [FUTURES_SYMBOL, exit_side, FUTURES_ENTRY, FUTURES_EXIT, FUTURES_QUANTITY, error_occured_time,
                         error_occured])
                    conn.commit()

            if req_multi_tp == "Yes":
                tp_order_id = 0
                if req_tp1_percent > 0:
                    try:
                        take_profit_order_1 = client.futures_create_order(symbol=FUTURES_SYMBOL, side=exit_side,
                                                                          type='TAKE_PROFIT_MARKET',
                                                                          stopPrice=TAKE_PROFIT_PRICE_FINAL_1,
                                                                          quantity=SELLABLE_1)
                        print(take_profit_order_1)
                        tp_order_id_1 = take_profit_order_1["orderId"]

                        cursor.execute("insert into f_id_list(order_id, entry_price,qty) values (%s, %s, %s)",
                                       [tp_order_id_1, entry_price, SELLABLE_1])
                        conn.commit()

                    except Exception as e:
                        error_occured = f"{e}"
                        print(error_occured)
                        error_occured_time = datetime.now()

                        cursor.execute(
                            "insert into futures_e_log(symbol, order_action, entry_order_type, exit_order_type, quantity, occured_time, error_description) values (%s, %s, %s, %s, %s, %s, %s)",
                            [FUTURES_SYMBOL, exit_side, FUTURES_ENTRY, FUTURES_EXIT, FUTURES_QUANTITY,
                             error_occured_time,
                             error_occured])
                        conn.commit()
                if req_tp2_percent > 0:
                    try:
                        take_profit_order_2 = client.futures_create_order(symbol=FUTURES_SYMBOL, side=exit_side,
                                                                          type='TAKE_PROFIT_MARKET',
                                                                          stopPrice=TAKE_PROFIT_PRICE_FINAL_2,
                                                                          quantity=SELLABLE_2)
                        print(take_profit_order_2)
                        tp_order_id_2 = take_profit_order_2["orderId"]

                        cursor.execute("insert into f_id_list(order_id, entry_price, qty) values (%s, %s, %s)",
                                       [tp_order_id_2, entry_price, SELLABLE_2])
                        conn.commit()

                    except Exception as e:
                        error_occured = f"{e}"
                        print(error_occured)
                        error_occured_time = datetime.now()

                        cursor.execute(
                            "insert into futures_e_log(symbol, order_action, entry_order_type, exit_order_type, quantity, occured_time, error_description) values (%s, %s, %s, %s, %s, %s, %s)",
                            [FUTURES_SYMBOL, exit_side, FUTURES_ENTRY, FUTURES_EXIT, FUTURES_QUANTITY,
                             error_occured_time,
                             error_occured])
                        conn.commit()
                if req_tp3_percent > 0:
                    try:
                        take_profit_order_3 = client.futures_create_order(symbol=FUTURES_SYMBOL, side=exit_side,
                                                                          type='TAKE_PROFIT_MARKET',
                                                                          stopPrice=TAKE_PROFIT_PRICE_FINAL_3,
                                                                          quantity=SELLABLE_3)
                        print(take_profit_order_3)
                        tp_order_id_3 = take_profit_order_3["orderId"]

                        cursor.execute("insert into f_id_list(order_id, entry_price, qty) values (%s, %s, %s)",
                                       [tp_order_id_3, entry_price, SELLABLE_3])
                        conn.commit()

                    except Exception as e:
                        error_occured = f"{e}"
                        print(error_occured)
                        error_occured_time = datetime.now()

                        cursor.execute(
                            "insert into futures_e_log(symbol, order_action, entry_order_type, exit_order_type, quantity, occured_time, error_description) values (%s, %s, %s, %s, %s, %s, %s)",
                            [FUTURES_SYMBOL, exit_side, FUTURES_ENTRY, FUTURES_EXIT, FUTURES_QUANTITY,
                             error_occured_time,
                             error_occured])
                        conn.commit()

            t11 = threading.Thread(
                target=lambda: check_exit_status(FUTURES_SYMBOL=FUTURES_SYMBOL, stoploss_order_id=stoploss_order_id,
                                                 tp_order_id=tp_order_id, tp_order_id_1=tp_order_id_1,
                                                 tp_order_id_2=tp_order_id_2, tp_order_id_3=tp_order_id_3,
                                                 exit_side=exit_side,
                                                 FUTURES_QUANTITY=FUTURES_QUANTITY, req_multi_tp=req_multi_tp))
            t11.start()


    def exit_order(side, FUTURES_SYMBOL, FUTURES_EXIT, req_order_time_out):
        the_pos = ""
        all_positions = client.futures_position_information()
        for open_pos in all_positions:
            amt = round(float(open_pos["positionAmt"]))
            if (open_pos["symbol"] == FUTURES_SYMBOL and amt != 0):
                the_pos = open_pos
                break

        if float(the_pos["positionAmt"]) < 0:
            existing_side = "SELL"
        else:
            existing_side = "BUY"
        print(existing_side)

        if side == "BUY" and existing_side == "SELL":
            valid_order = "Yes"
        elif side == "SELL" and existing_side == "BUY":
            valid_order = "Yes"
        elif side == "BUY" and existing_side == "BUY":
            valid_order = "No"
        elif side == "SELL" and existing_side == "SELL":
            valid_order = "No"

        if the_pos == "" or valid_order == "No":
            if side == "BUY":
                error_occured = "No valid open short position for this symbol. Cannot proceed with the exit order"
            if side == "SELL":
                error_occured = "No valid open long position for this symbol. Cannot proceed with the exit order"
            error_occured_time = datetime.now()

            cursor.execute(
                "insert into futures_e_log(symbol, order_action, entry_order_type, occured_time, error_description) values (%s, %s, %s, %s, %s)",
                [FUTURES_SYMBOL, side, FUTURES_EXIT, error_occured_time, error_occured])
            conn.commit()
        else:
            if side == "BUY":
                exit_qty = (float(the_pos["positionAmt"])) * -1
            if side == "SELL":
                exit_qty = float(the_pos["positionAmt"])

            if FUTURES_EXIT == "MARKET":

                try:
                    futures_order = client.futures_create_order(symbol=FUTURES_SYMBOL, side=side, type='MARKET',
                                                                quantity=exit_qty)
                    print(f"futures order = {futures_order}")
                    order_id = futures_order["orderId"]
                except Exception as e:
                    error_occured = f"{e}"
                    print(error_occured)
                    error_occured_time = datetime.now()

                    cursor.execute(
                        "insert into futures_e_log(symbol, order_action, exit_order_type, quantity, occured_time, error_description) values (%s, %s, %s, %s, %s, %s)",
                        [FUTURES_SYMBOL, side, FUTURES_EXIT, exit_qty, error_occured_time, error_occured])
                    conn.commit()

                time.sleep(2)

            elif FUTURES_EXIT == "LIMIT":
                prices = client.get_all_tickers()
                for ticker in prices:
                    if ticker["symbol"] == FUTURES_SYMBOL:
                        last_price = float(ticker["price"])
                        break

                try:
                    futures_order = client.futures_create_order(symbol=FUTURES_SYMBOL, side=side, type='LIMIT',
                                                                quantity=exit_qty, price=last_price, timeInForce='GTC')
                    print(f"futures order = {futures_order}")
                    order_id = futures_order["orderId"]
                except Exception as e:
                    error_occured = f"{e}"
                    print(error_occured)
                    error_occured_time = datetime.now()

                    cursor.execute(
                        "insert into futures_e_log(symbol, order_action, exit_order_type, quantity, occured_time, error_description) values (%s, %s, %s, %s, %s, %s)",
                        [FUTURES_SYMBOL, side, FUTURES_EXIT, exit_qty, error_occured_time, error_occured])
                    conn.commit()

            time.sleep(req_order_time_out)

            try:
                live_trades_list = client.futures_account_trades(symbol=FUTURES_SYMBOL)
                for live_trade in reversed(live_trades_list):
                    if live_trade["orderId"] == order_id:
                        executed_order = live_trade
                        realized_pnl = float(live_trade["realizedPnl"])
                        commission_charged = float(live_trade["commission"])
                        if live_trade["commissionAsset"] == "USDT":
                            total_pnl = round((realized_pnl - commission_charged), 6)
                        else:
                            prices = client.get_all_tickers()
                            bc = live_trade["commissionAsset"]
                            for ticker in prices:
                                if ticker["symbol"] == bc + "USDT":
                                    current_market_price = float(ticker["price"])
                                    break
                            total_pnl = round(((realized_pnl - commission_charged) * current_market_price), 6)
                        break

                FINAL_ORDER_ID = executed_order["orderId"]
                FINAL_ORDER_SYMBOL = executed_order["symbol"]
                FINAL_ORDER_QTY = float(executed_order["qty"])
                FINAL_ORDER_PRICE = float(executed_order["price"])
                FINAL_ORDER_ACTION = executed_order["side"]
                FINAL_ORDER_TYPE = "LIMIT"
                final_order_executed_time = datetime.now()

                cursor.execute(sql.SQL(
                    "insert into futures_t_log(date_time, symbol, order_id, order_action, order_type, executed_price, executed_qty,pnl) values (%s, %s, %s, %s, %s, %s, %s,%s)"),
                    [final_order_executed_time, FINAL_ORDER_SYMBOL, FINAL_ORDER_ID, FINAL_ORDER_ACTION,
                     FINAL_ORDER_TYPE, FINAL_ORDER_PRICE, FINAL_ORDER_QTY, total_pnl])
                conn.commit()

            except Exception as e:
                print(e)

    try:
        # Check if order is entry
        if req_position_type == "Enter_long" or req_position_type == "Enter_short":

            if req_position_type == "Enter_long":
                side = "BUY"
                leverage = req_long_leverage
            elif req_position_type == "Enter_short":
                side = "SELL"
                leverage = req_short_leverage

            # Fetch wallet balance
            futures_info = client.futures_account_balance()
            futures_balance_in_selected_base_coin = 0.0
            for futures_asset in futures_info:
                name = futures_asset["asset"]
                balance = float(futures_asset["balance"])
                if name == req_base_coin:
                    futures_balance_in_selected_base_coin += balance

                else:
                    current_price_ff = client.get_symbol_ticker(symbol=name + req_base_coin)["price"]
                    futures_balance_in_selected_base_coin += balance * float(current_price_ff)
            print(f"Futures balance = {futures_balance_in_selected_base_coin}")

            # Set Buy/Sell Leverage & Margin Mode
            if req_margin_mode == "Isolated":
                try:
                    changed_margin_type = client.futures_change_margin_type(symbol=FUTURES_SYMBOL, marginType="ISOLATED")
                    print(changed_margin_type)
                except Exception as e:
                    FUTURES_SYMBOL = FUTURES_SYMBOL
                    F_SIDE = side
                    JSON_ENTRY = FUTURES_ENTRY
                    error_occured_time = datetime.now()
                    error_occured = e
                    cursor.execute(
                        "insert into futures_e_log(symbol, order_action, entry_order_type, occured_time, error_description) values (%s, %s, %s, %s, %s)",
                        [FUTURES_SYMBOL, F_SIDE, JSON_ENTRY, error_occured_time, error_occured])
                    conn.commit()
            elif req_margin_mode == "Cross":
                try:
                    changed_margin_type = client.futures_change_margin_type(symbol=FUTURES_SYMBOL, marginType="CROSSED")
                    print(changed_margin_type)
                except Exception as e:
                    FUTURES_SYMBOL = FUTURES_SYMBOL
                    F_SIDE = side
                    JSON_ENTRY = FUTURES_ENTRY
                    error_occured_time = datetime.now()
                    error_occured = e
                    cursor.execute(
                        "insert into futures_e_log(symbol, order_action, entry_order_type, occured_time, error_description) values (%s, %s, %s, %s, %s)",
                        [FUTURES_SYMBOL, F_SIDE, JSON_ENTRY, error_occured_time, error_occured])
                    conn.commit()

            # Set leverage
            try:
                changed_leverage = client.futures_change_leverage(symbol=FUTURES_SYMBOL, leverage=leverage)
                print("Changed leverage to: " + str(changed_leverage))
            except Exception as e:
                FUTURES_SYMBOL = FUTURES_SYMBOL
                F_SIDE = side
                JSON_ENTRY = FUTURES_ENTRY
                error_occured_time = datetime.now()
                error_occured = e
                cursor.execute(
                    "insert into futures_e_log(symbol, order_action, entry_order_type, occured_time, error_description) values (%s, %s, %s, %s, %s)",
                    [FUTURES_SYMBOL, F_SIDE, JSON_ENTRY, error_occured_time, error_occured])
                conn.commit()

            if req_qty_type == "Percentage":
                current_bal = futures_balance_in_selected_base_coin
                qty_in_base_coin = current_bal * req_qty
            elif req_qty_type == "Fixed":
                qty_in_base_coin = req_qty

            FUTURES_QUANTITY = futures_calculate_buy_qty_with_precision(FUTURES_SYMBOL, qty_in_base_coin)

            # Stop bot if balance is below user defined amount
            if req_stop_bot_balance != 0:
                if futures_balance_in_selected_base_coin < req_stop_bot_balance:
                    FUTURES_SYMBOL = FUTURES_SYMBOL
                    F_SIDE = side
                    JSON_ENTRY = FUTURES_ENTRY
                    error_occured_time = datetime.now()
                    error_occured = "Cant initiate the trade! Wallet balance is low!"
                    cursor.execute(
                        "insert into futures_e_log(symbol, order_action, entry_order_type, occured_time, error_description) values (%s, %s, %s, %s, %s)",
                        [FUTURES_SYMBOL, F_SIDE, JSON_ENTRY, error_occured_time, error_occured])
                    conn.commit()
                else:
                    # send values to enter trade function
                    enter_order(FUTURES_ENTRY, FUTURES_SYMBOL, side, FUTURES_QUANTITY, req_order_time_out,
                                req_long_stop_loss_percent, req_long_take_profit_percent, req_short_stop_loss_percent,
                                req_short_take_profit_percent, req_multi_tp, req_tp1_qty_size, req_tp2_qty_size,
                                req_tp3_qty_size, req_tp1_percent, req_tp2_percent, req_tp3_percent)

        # 7) check if order is exit
        elif req_position_type == "Exit_long" or req_position_type == "Exit_short":

            if req_position_type == "Exit_long":
                side = "SELL"
            elif req_position_type == "Exit_short":
                side = "BUY"

            exit_order(side, FUTURES_SYMBOL, FUTURES_EXIT, req_order_time_out)

    except:
        error_occured_time = datetime.now()
        error_occured = "Error in Initiating Futures Order!"
        cursor.execute(
            "insert into futures_e_log(occured_time, error_description) values (%s, %s)",
            [error_occured_time, error_occured])
        conn.commit()










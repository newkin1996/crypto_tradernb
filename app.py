from flask import Flask, render_template, request, jsonify
import psycopg2 # on ubuntu, sudo apt-get install libpq-dev, sudo pip install psycopg2/sudo pip install psycopg2-binary
from binance.client import Client
from datetime import datetime
from decimal import Decimal
import json
import math
import ast
import requests
from psycopg2 import sql
import time
import threading

app = Flask(__name__)

api_key = ""
api_secret = ""

dash_user_name = "tradernb"
dash_password = "NoToFOMO123"

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

client = Client(api_key, api_secret)

try:
    cursor.execute("select api_key from binance_keys")
    r_2 = cursor.fetchall()
    binance_api_key = r_2[0][0]
except:
    binance_api_key = "Enter Api Key"
    cursor.execute("insert into binance_keys(api_key) values (%s)",
                   [binance_api_key])
    conn.commit()
    print("Records inserted")

try:
    cursor.execute("select api_secret from binance_keys")
    r_2 = cursor.fetchall()
    binance_api_secret = r_2[0][0]
except:
    binance_api_secret = "Enter Api Secret"
    cursor.execute("insert into binance_keys(api_secret) values (%s)",
                   [binance_api_secret])
    conn.commit()
    print("Records inserted")

try:
    cursor.execute("select api_key from bybit_keys")
    r_2 = cursor.fetchall()
    bybit_api_key = r_2[0][0]
except:
    bybit_api_key = "Enter Api Key"
    cursor.execute("insert into bybit_keys(api_key) values (%s)",
                   [bybit_api_key])
    conn.commit()
    print("Records inserted")

try:
    cursor.execute("select api_secret from bybit_keys")
    r_2 = cursor.fetchall()
    bybit_api_secret = r_2[0][0]
except:
    bybit_api_secret = "Enter Api Secret"
    cursor.execute("insert into bybit_keys(api_secret) values (%s)",
                   [bybit_api_secret])
    conn.commit()
    print("Records inserted")


@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/profile',methods=["POST","GET"])
def get_profile():
    if request.method == "GET":
        try:
            cursor.execute("select api_key from binance_keys")
            r_2 = cursor.fetchall()
            binance_api_key = r_2[0][0]
        except:
            binance_api_key = "Enter Api Key"

        try:
            cursor.execute("select api_secret from binance_keys")
            r_2 = cursor.fetchall()
            binance_api_secret = r_2[0][0]
        except:
            binance_api_secret = "Enter Api Secret"

        try:
            cursor.execute("select api_key from bybit_keys")
            r_2 = cursor.fetchall()
            bybit_api_key = r_2[0][0]
        except:
            bybit_api_key = "Enter Api Key"

        try:
            cursor.execute("select api_secret from bybit_keys")
            r_2 = cursor.fetchall()
            bybit_api_secret = r_2[0][0]
        except:
            bybit_api_secret = "Enter Api Secret"


        return render_template('profile.html',bi_key=binance_api_key,bi_secret=binance_api_secret,by_key=bybit_api_key,by_secret=bybit_api_secret)
    if request.method == "POST":
        binance_api_key = request.form["binance_key"]
        binance_api_secret = request.form["binance_secret"]
        bybit_api_key = request.form["bybit_key"]
        bybit_api_secret = request.form["bybit_secret"]

        cursor.execute("update binance_keys set api_key = %s, api_secret = %s",[binance_api_key, binance_api_secret])
        conn.commit()
        print("Records inserted")
        print("Done")

        cursor.execute("update bybit_keys set api_key = %s, api_secret = %s", [bybit_api_key, bybit_api_secret])
        conn.commit()
        print("Records inserted")
        print("Done")

        return render_template('profile.html',bi_key=binance_api_key,bi_secret=binance_api_secret,by_key=bybit_api_key,by_secret=bybit_api_secret)

@app.route('/copy_msg',methods=["POST"])
def get_json():
    try:
        exchange = request.form["exchange"]
        exchange1 = '{"exchange"'
        exchange2 = exchange
        trade_type = request.form["trade_type"]
        trade_type1 = "trade_type"
        trade_type2 = trade_type
        base_coin = request.form["base_coin"]
        base_coin1 = "base_coin"
        base_coin2 = base_coin
        coin_pair = request.form["coin_pair"]
        coin_pair1 = "coin_pair"
        coin_pair2 = coin_pair
        entry_type = request.form["entry_type"]
        entry_type1 = "entry_type"
        entry_type2 = entry_type
        exit_type = request.form["exit_type"]
        exit_type1 = "exit_type"
        exit_type2 = exit_type
        margin_mode = request.form["margin_mode"]
        margin_mode1 = "margin_mode"
        margin_mode2 = margin_mode
        amt_type = request.form["amt_type"]
        amt_type1 = "qty_type"
        amt_type2 = amt_type
        enter_amt = request.form["enter_amt"]
        enter_amt1 = "qty"
        enter_amt2 = enter_amt
        long_lev = request.form["long_lev"]
        long_lev1 = "long_leverage"
        long_lev2 = long_lev
        short_lev = request.form["short_lev"]
        short_lev1 = "short_leverage"
        short_lev2 = short_lev
        long_sl = request.form["long_sl"]
        long_sl1 = "long_stop_loss_percent"
        long_sl2 = long_sl
        long_tp = request.form["long_tp"]
        long_tp1 = "long_take_profit_percent"
        long_tp2 = long_tp
        short_sl = request.form["short_sl"]
        short_sl1 = "short_stop_loss_percent"
        short_sl2 = short_sl
        short_tp = request.form["short_tp"]
        short_tp1 = "short_take_profit_percent"
        short_tp2 = short_tp
        multi_tp = request.form["multi_tp"]
        multi_tp1 = "enable_multi_tp"
        multi_tp2 = multi_tp
        tp1_pos_size = request.form["tp1_pos_size"]
        tp1_pos_size1 = "tp_1_pos_size"
        tp1_pos_size2 = tp1_pos_size
        tp2_pos_size = request.form["tp2_pos_size"]
        tp2_pos_size1 = "tp_2_pos_size"
        tp2_pos_size2 = tp2_pos_size
        tp3_pos_size = request.form["tp3_pos_size"]
        tp3_pos_size1 = "tp_3_pos_size"
        tp3_pos_size2 = tp3_pos_size
        tp1_percent = request.form["tp1_percent"]
        tp1_percent1 = "tp1_percent"
        tp1_percent2 = tp1_percent
        tp2_percent = request.form["tp2_percent"]
        tp2_percent1 = "tp2_percent"
        tp2_percent2 = tp2_percent
        tp3_percent = request.form["tp3_percent"]
        tp3_percent1 = "tp3_percent"
        tp3_percent2 = tp3_percent
        stop_bot = request.form["stop_bot"]
        stop_bot1 = "stop_bot_below_balance"
        stop_bot2 = stop_bot
        time_out = request.form["time_out"]
        time_out1 = "order_time_out"
        time_out2 = time_out
        alert_type = request.form["alert_type"]
        if alert_type == "Enter Long":
            al_type = '"Enter_long"}'
        if alert_type == "Exit Long":
            al_type = '"Exit_long"}'
        if alert_type == "Enter Short":
            al_type = '"Enter_short"}'
        if alert_type == "Exit Short":
            al_type = '"Exit_short"}'
        alert_type1 = "position_type"
        alert_type2 = al_type


        return render_template('copy_msg.html',exchange1=exchange1,exchange2=exchange2,trade_type1=trade_type1,trade_type2=trade_type2,base_coin1=base_coin1,base_coin2=base_coin2,coin_pair1=coin_pair1,coin_pair2=coin_pair2,entry_type1=entry_type1,entry_type2=entry_type2,exit_type1=exit_type1,exit_type2=exit_type2,margin_mode1=margin_mode1,margin_mode2=margin_mode2,amt_type1=amt_type1,amt_type2=amt_type2,enter_amt1=enter_amt1,enter_amt2=enter_amt2,long_lev1=long_lev1,long_lev2=long_lev2,short_lev1=short_lev1,short_lev2=short_lev2,long_sl1=long_sl1,long_sl2=long_sl2,long_tp1=long_tp1,long_tp2=long_tp2,short_sl1=short_sl1,short_sl2=short_sl2,short_tp1=short_tp1,short_tp2=short_tp2,multi_tp1=multi_tp1,multi_tp2=multi_tp2,tp1_pos_size1=tp1_pos_size1,tp1_pos_size2=tp1_pos_size2,tp2_pos_size1=tp2_pos_size1,tp2_pos_size2=tp2_pos_size2,tp3_pos_size1=tp3_pos_size1,tp3_pos_size2=tp3_pos_size2,tp1_percent1=tp1_percent1,tp1_percent2=tp1_percent2,tp2_percent1=tp2_percent1,tp2_percent2=tp2_percent2,tp3_percent1=tp3_percent1,tp3_percent2=tp3_percent2,stop_bot1=stop_bot1,stop_bot2=stop_bot2,time_out1=time_out1,time_out2=time_out2,alert_type1=alert_type1,alert_type2=alert_type2)
    except:
        return render_template('missing_fields.html')

@app.route('/json_generator',methods=["POST", "GET"])
def gen_json():
    if request.method == "POST":
        entered_un = request.form["Username"]
        entered_pw = request.form["Password"]
        if entered_un == dash_user_name and entered_pw == dash_password:
            exchange_info = client.get_exchange_info()
            list_of_coin_pairs = []
            for s in exchange_info['symbols']:
                sym = s['symbol']
                list_of_coin_pairs.append(sym)
            dup_removed_list = list(dict.fromkeys(list_of_coin_pairs))

            return render_template('json_gen.html', coin_list=dup_removed_list)
        else:
            return render_template('welcome_incorrect_credentials.html')

    if request.method == "GET":
        exchange_info = client.get_exchange_info()
        list_of_coin_pairs = []
        for s in exchange_info['symbols']:
            sym = s['symbol']
            list_of_coin_pairs.append(sym)
        dup_removed_list = list(dict.fromkeys(list_of_coin_pairs))

        return render_template('json_gen.html',coin_list=dup_removed_list)

@app.route('/binance_spot',methods=["POST", "GET"])
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
        cursor.execute("select api_key from binance_keys")
        r_2 = cursor.fetchall()
        if r_2[0][0] == "Enter Api Key":
            api_key = ""
        else:
            api_key = r_2[0][0]
    except:
        api_key = ""

    try:
        cursor.execute("select api_secret from binance_keys")
        r_2 = cursor.fetchall()
        if r_2[0][0] == "Enter Api Secret":
            api_secret = ""
        else:
            api_secret = r_2[0][0]
    except:
        api_secret = ""

    if api_key and api_secret != "":
        try:
            client = Client(api_key, api_secret)
        except:
            return render_template('invalid_key.html')

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

                prices = client.get_all_tickers()
                for ticker in prices:
                    if ticker["symbol"] == SPOT_SYM:
                        SPOT_SYM_CURRENT_PRICE = float(ticker["price"])
                        break

                try:
                    cursor.execute("select entry_price from s_id_list where order_id = %s", [SPOT_OR_ID])
                    result = cursor.fetchall()
                    ENTRY_PRICE_OF_BUY_ORDER = float(result[0][0])

                    # p_o_l = ((SPOT_SYM_CURRENT_PRICE - ENTRY_PRICE_OF_BUY_ORDER)/ENTRY_PRICE_OF_BUY_ORDER)
                    # p_o_l_r = round(p_o_l,6)
                    #
                    # PROFIT_OR_LOSS_FROM_ENTRY = ("{:.3%}".format(p_o_l_r))
                    p_n_l = round((SPOT_SYM_CURRENT_PRICE - ENTRY_PRICE_OF_BUY_ORDER),3)
                    p_o_l = ((SPOT_SYM_CURRENT_PRICE - ENTRY_PRICE_OF_BUY_ORDER) / ENTRY_PRICE_OF_BUY_ORDER) * 100
                    PROFIT_OR_LOSS_FROM_ENTRY = str((round(p_o_l, 3))) + "%"

                    print(PROFIT_OR_LOSS_FROM_ENTRY)

                    cursor.execute(
                        "insert into open_orders(created_date, symbol, order_id, price, quantity, order_action, order_type, entry_price, current_price, pnl,pnl_per) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)",
                        [SPOT_OR_CREATE_DATE, SPOT_SYM, SPOT_OR_ID, SPOT_PRICE, SPOT_QUANTITY, SPOT_OR_ACTION,
                         SPOT_OR_TYPE, ENTRY_PRICE_OF_BUY_ORDER, SPOT_SYM_CURRENT_PRICE, p_n_l,
                         PROFIT_OR_LOSS_FROM_ENTRY])
                    conn.commit()
                except:
                    cursor.execute(
                        "insert into open_orders(created_date, symbol, order_id, price, quantity, order_action, order_type, current_price) values (%s, %s, %s, %s, %s, %s, %s, %s)",
                        [SPOT_OR_CREATE_DATE, SPOT_SYM, SPOT_OR_ID, SPOT_PRICE, SPOT_QUANTITY, SPOT_OR_ACTION,
                         SPOT_OR_TYPE, SPOT_SYM_CURRENT_PRICE])
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

        try:
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
            deposits_display = f"Deposited Amt (USD): {round((total_deposited_amt), 2)}"
        except:
            return render_template('invalid_key.html')

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
            asset_balance_display = f"Asset Balance (USD): {round((total_asset_balance), 2)}"
            spot_balance_display = f"Asset Balance (USD): {round((sum_SPOT), 2)}"
        except:
            asset_balance_display = "Asset Balance (USD): NA"
            spot_balance_display = "Asset Balance (USD): NA"

        cursor.execute("select sum(pnl) as total from trade_log")
        results = cursor.fetchall()
        try:
            overall_pnl = float(round((results[0][0]), 2))
            pnl_display = f"Spot PnL (USD): {overall_pnl}"
        except:
            overall_pnl = "NA"
            pnl_display = "Spot PnL (USD): NA"

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

    else:
        return render_template('error.html')

@app.route('/binance_futures',methods=["POST", "GET"])
def get_futures():
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
        cursor.execute("select api_key from binance_keys")
        r_2 = cursor.fetchall()
        api_key = r_2[0][0]
    except:
        api_key = ""

    try:
        cursor.execute("select api_secret from binance_keys")
        r_2 = cursor.fetchall()
        api_secret = r_2[0][0]
    except:
        api_secret = ""

    if api_key and api_secret != "":
        try:
            client = Client(api_key, api_secret)
        except:
            return render_template('invalid_key.html')

        try:

            open_orders = client.futures_get_open_orders()

            sql = ''' DELETE FROM f_o_orders '''
            cursor.execute(sql)
            conn.commit()


            for order in open_orders:

                create_time = order["time"]
                create_date = datetime.fromtimestamp((create_time / 1000)).strftime("%Y-%m-%d")
                # SPOT_OR_CREATE_TIME = datetime.fromtimestamp((create_time / 1000)).strftime("%I:%M:%S")
                sym = order["symbol"]
                id = order["orderId"]
                p = order["stopPrice"]
                num = Decimal(p)
                price = num.normalize()

                action= order["side"]
                type = order["type"]

                prices = client.get_all_tickers()
                for ticker in prices:
                    if ticker["symbol"] == sym:
                        sym_current_price = float(ticker["price"])
                        break

                try:
                    cursor.execute("select entry_price from f_id_list where order_id = %s", [id])
                    result = cursor.fetchall()
                    ENTRY_PRICE_OF_INITIAL_ORDER = float(result[0][0])

                    cursor.execute("select qty from f_id_list where order_id = %s", [id])
                    result = cursor.fetchall()
                    QTY_OF_OPEN_ORDER = float(result[0][0])

                    p_n_l = round((sym_current_price - ENTRY_PRICE_OF_INITIAL_ORDER),3)
                    p_o_l = ((sym_current_price - ENTRY_PRICE_OF_INITIAL_ORDER) / ENTRY_PRICE_OF_INITIAL_ORDER) * 100
                    PROFIT_OR_LOSS_FROM_ENTRY = str((round(p_o_l, 3))) + "%"

                    print(PROFIT_OR_LOSS_FROM_ENTRY)

                    cursor.execute("insert into f_o_orders(created_date, symbol, order_id, price, quantity, order_action, order_type, entry_price, current_price, pnl, pnl_per) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",[create_date, sym, id, price, QTY_OF_OPEN_ORDER, action,type, ENTRY_PRICE_OF_INITIAL_ORDER, sym_current_price, p_n_l, PROFIT_OR_LOSS_FROM_ENTRY])
                    conn.commit()
                except:
                    cursor.execute(
                        "insert into f_o_orders(created_date, symbol, order_id, price, order_action, order_type, current_price) values (%s, %s, %s, %s, %s, %s, %s)",
                        [create_date, sym, id, price, action, type, sym_current_price])
                    conn.commit()

        except:
            pass

        try:

            open_positions = client.futures_position_information()

            sql = ''' DELETE FROM f_o_positions '''
            cursor.execute(sql)
            conn.commit()

            for order in open_positions:
                sym = order["symbol"]
                create_time = order["updateTime"]
                create_date = datetime.fromtimestamp((create_time / 1000)).strftime("%Y-%m-%d")
                # SPOT_OR_CREATE_TIME = datetime.fromtimestamp((create_time / 1000)).strftime("%I:%M:%S")
                pos_entry_price = float(order["entryPrice"])
                liquidation_price = float(order["liquidationPrice"])
                pos_current_price = float(order["markPrice"])

                margin_type = order["marginType"]
                leverage = int(order["leverage"])

                if float(order["positionAmt"]) < 0:
                    pos_qty = (float(order["positionAmt"]))*-1
                    pos_side = "SELL"
                else:
                    pos_qty = float(order["positionAmt"])
                    pos_side = "BUY"

                PROFIT_OR_LOSS_FROM_ENTRY = round((float(order["unRealizedProfit"])),6)

                amt = round(float(order["positionAmt"]))
                if amt != 0:
                    cursor.execute(
                        "insert into f_o_positions(created_date, symbol, side, entry_price, current_price, liq_price, margin_type, leverage, quantity, pnl) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        [create_date, sym, pos_side, pos_entry_price, pos_current_price, liquidation_price, margin_type, leverage, pos_qty,PROFIT_OR_LOSS_FROM_ENTRY])
                    conn.commit()
        except:
            pass

        order_statement='SELECT * FROM f_o_orders;'
        cursor.execute(order_statement)
        rowResults=cursor.fetchall()
        list_length = len(rowResults)

        order_statement = 'SELECT * FROM f_o_positions;'
        cursor.execute(order_statement)
        pos_rowResults = cursor.fetchall()
        pos_list_length = len(pos_rowResults)


        exchange_info = client.get_exchange_info()
        list_of_coin_pairs = []
        for s in exchange_info['symbols']:
            baseAsset = s['baseAsset']
            list_of_coin_pairs.append((baseAsset + "USD"))
        dup_removed_list = list(dict.fromkeys(list_of_coin_pairs))

        error_order_statement = 'SELECT * FROM futures_e_log;'
        cursor.execute(error_order_statement)
        error_rowResults = cursor.fetchall()
        error_list_length = len(error_rowResults)

        trade_order_statement = 'SELECT * FROM futures_t_log;'
        cursor.execute(trade_order_statement)
        trade_rowResults = cursor.fetchall()
        trade_list_length = len(trade_rowResults)

        try:
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
            deposits_display = f"Deposited Amt (USD): {round((total_deposited_amt), 2)}"
        except:
            return render_template('invalid_key.html')


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
            asset_balance_display = f"Asset Balance (USD): {round((total_asset_balance), 2)}"
            futures_balance_display = f"Asset Balance (USD): {round((futures_usd), 2)}"
        except:
            asset_balance_display = "Asset Balance (USD): NA"
            futures_balance_display = "Asset Balance (USD): NA"

        cursor.execute("select sum(pnl) as total from futures_t_log")
        results = cursor.fetchall()
        try:
            overall_pnl = float(round((results[0][0]), 2))
            pnl_display = f"Overall Futures PnL (USD): {overall_pnl}"
        except:
            overall_pnl = "NA"
            pnl_display = "Futures PnL (USD): NA"

        labels = []
        values = []

        labels.clear()
        values.clear()

        try:
            acc_info = client.futures_account_balance()
            prices = client.get_all_tickers()
            for asset in acc_info:
                pair_name = asset["asset"]
                total_bal = float(asset["balance"])
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


        return render_template('futures.html',pos_rowResults=pos_rowResults,pos_list_length=pos_list_length,recentRecords=rowResults,list_length=list_length,coin_list=dup_removed_list,coin_pair_name=coin_pair_name,modified_link=href_modified,labels=labels,values=values,colors=colors,error_recentRecords=error_rowResults,error_list_length=error_list_length,trade_recentRecords=trade_rowResults,trade_list_length=trade_list_length,deposits=deposits_display,assets=asset_balance_display,pnl=pnl_display,spot=futures_balance_display)

    else:
        return render_template('error.html')


@app.route('/webhook', methods=["POST"])
def process_alert():
    print("Webhook triggered")
    print(request)
    alert_response = request.get_data(as_text=True)

    alert_response = json.loads(alert_response)
    print(f"first method worked = {alert_response}")

    print(f"type = {type(alert_response)}")

    # with open("alerts.txt", mode="w") as alerts_file:
    #     alerts_file.write(f"response = {request}, content = {alert_response}")
    #
    req_exchange = alert_response["exchange"]
    print(f"req exchange = {req_exchange}")



if __name__ == "__main__":
    app.run(host='0.0.0.0',port=80,debug=True)


# Webhook triggered
# <Request 'http://3.126.245.49/webhook' [POST]>
# first method worked = {"use_bybit":"1","coin_pair":"BTCUSDT","entry_order_type":"0","exit_order_type":"0","margin_mode":"1","qty_in_percentage": "true","qty":"1476.2828415986","buy_leverage":"1","sell_leverage":"1","long_stop_loss_percent":0.2032130914,"long_take_profit_percent":0.3048196371,"short_stop_loss_percent":0.2032130914,"short_take_profit_percent":0.3048196371,"enable_multi_tp":"true","tp_1_pos_size":"33","tp_1_percent":"0.1005904802","tp_2_pos_size":"33","tp_2_percent":"0.2011809605","tp_3_pos_size":"100","tp_3_percent":"0.3048196371","advanced_mode": "1","stop_bot_below_balance":"20","order_time_out":"240","exit_existing_trade": "True","comment": "","position": "Enter Short",}
# 34.212.75.30 - - [17/Sep/2022 20:37:00] "POST /webhook HTTP/1.1" 200 -

from flask import Flask, render_template, request
import psycopg2 # on ubuntu, sudo apt-get install libpq-dev, sudo pip install psycopg2/sudo pip install psycopg2-binary
from binance.client import Client
from datetime import datetime
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
    print(request)
    global api_key
    global api_secret
    try:
        api_key = request.form["Api_Key"]
        api_secret = request.form["Api_Secret"]
    except:
        pass

    client = Client(api_key, api_secret)

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

    cursor.execute("select sum(pnl) as total from trade_log")
    results = cursor.fetchall()
    overall_pnl = float(round((results[0][0]), 2))
    pnl_display = f"Overall Spot Pnl (USD): {overall_pnl}"

    labels = []
    values = []

    labels.clear()
    values.clear()

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

    try:
        coin_pair_name = request.form["coins"]
        href_modified = f"https://www.tradingview.com/symbols/{coin_pair_name}/?exchange=BITSTAMP"
    except:
        coin_pair_name = "BTCUSD"
        href_modified = f"https://www.tradingview.com/symbols/{coin_pair_name}/?exchange=BITSTAMP"



    return render_template('index.html',recentRecords=rowResults,list_length=list_length,coin_list=dup_removed_list,coin_pair_name=coin_pair_name,modified_link=href_modified,labels=labels,values=values,colors=colors,error_recentRecords=error_rowResults,error_list_length=error_list_length,trade_recentRecords=trade_rowResults,trade_list_length=trade_list_length,deposits=deposits_display,assets=asset_balance_display,pnl=pnl_display,spot=spot_balance_display)

# @app.route('/select',methods=["POST"])
# def index_new():
#
#     #establishing the connection
#     conn = psycopg2.connect(
#        database="gpu", user='postgres', password='postgres', host='127.0.0.1', port= '5433'
#     )
#     #Creating a cursor object using the cursor() method
#     cursor = conn.cursor()
#
#     #Executing an MYSQL function using the execute() method
#     cursor.execute("select version()")
#
#     # Fetch a single row using fetchone() method.
#     data = cursor.fetchone()
#     print("Connection established to: ",data)
#
#     order_statement='SELECT * FROM open_orders;'
#     cursor.execute(order_statement)
#     rowResults=cursor.fetchall()
#     list_length = len(rowResults)
#     print(rowResults)
#
#     client = Client(api_key, api_secret)
#     exchange_info = client.get_exchange_info()
#     list_of_coin_pairs = []
#     for s in exchange_info['symbols']:
#        baseAsset = s['baseAsset']
#        list_of_coin_pairs.append((baseAsset+"USD"))
#     dup_removed_list = list(dict.fromkeys(list_of_coin_pairs))
#
#     coin_pair_name = request.form["coins"]
#     print(coin_pair_name)
#
#     href_modified = f"https://www.tradingview.com/symbols/{coin_pair_name}/?exchange=BITSTAMP"
#
#     pie_labels = labels
#     pie_values = values
#
# return render_template('index.html',recentRecords=rowResults,list_length=list_length,coin_list=dup_removed_list,coin_pair_name=coin_pair_name,modified_link=href_modified,set=zip(values, labels, colors))

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)

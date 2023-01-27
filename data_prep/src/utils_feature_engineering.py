
import os
import pandas as pd
import datetime
import numpy as np
from configparser import ConfigParser
import logging

import talib
import talib as tb

import sqlite3
from sqlalchemy import create_engine

import utils_validate_candlestick as u

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Create and configure logger
logging.basicConfig(filename="logs/utils_feature_engineering.log",
                    level=logging.INFO,
                    format='%(name)s|%(asctime)s|%(levelname)s|[%(filename)s:%(lineno)s - %(funcName)20s() ]|%(message)s',
                    filemode='w')

# Creating an object
logger = logging.getLogger()

configur = ConfigParser()
configur.read('../config_files/config_candlestick_patterns.ini')

def create_candlestick_patterns(list_asset_ticket, list_timestamp, db_address, start_date="", end_date=""):
    try:
        logger.info("start")

        # Candlesitck selected patterns
        candle_names = ['CDLINVERTEDHAMMER',
                        'CDLHAMMER',
                        'CDLPIERCING',
                        'CDLMORNINGSTAR',
                        'CDLSHOOTINGSTAR',
                        'CDLHANGINGMAN',
                        'CDLDARKCLOUDCOVER',
                        'CDLEVENINGSTAR',
                        'CDLENGULFING']

        for asset_ticket in list_asset_ticket:
            for timestamp in list_timestamp:

                engine = create_engine(db_address, echo=False)
                sqlite_connection = engine.connect()

                input_tbl_name = "tbl_raw_binance" + "_" + asset_ticket + "_" + timestamp
                
                sql_command = "SELECT * FROM " + input_tbl_name

                if(start_date!="" and end_date!=""):
                    
                    sd = datetime.datetime.strptime(start_date,'%d %b, %Y').strftime('%Y-%m-%d')
                    ed = datetime.datetime.strptime(end_date,'%d %b, %Y').strftime('%Y-%m-%d')

                    sql_append = " WHERE " + "date(date) >= " + "'" + sd + "'" + " AND date(date) <= " + "'" + ed + "'"
                    sql_command = sql_command + sql_append

                df = pd.read_sql(sql_command, sqlite_connection)

                sqlite_connection.close()

                # extract OHLC 
                op = df['open']
                hi = df['high']
                lo = df['low']
                cl = df['close']

                # create columns for each pattern
                for candle in candle_names:
                    # below is same as;
                    # df["CDL3LINESTRIKE"] = talib.CDL3LINESTRIKE(op, hi, lo, cl)
                    df[candle] = getattr(talib, candle)(op, hi, lo, cl)

                # Split CDLENGULFING into bullish and bearish
                list_open_time_bullish_engulfing = df[df['CDLENGULFING']==100]['date'].to_list()
                list_open_time_bearish_engulfing = df[df['CDLENGULFING']==-100]['date'].to_list()

                df['CDLENGULFINGBULLISH'] = np.where(df['date'].isin(list_open_time_bullish_engulfing), 100, 0)
                df['CDLENGULFINGBEARISH'] = np.where(df['date'].isin(list_open_time_bearish_engulfing), -100, 0)
                
                # Replace first (based on the 'window_size') Candlestick values for 0 
                window_size = configur.getint('candlestick_patterns', 'window_size')
                subset = ['CDLINVERTEDHAMMER', 'CDLHAMMER',
                            'CDLPIERCING', 'CDLMORNINGSTAR', 'CDLSHOOTINGSTAR', 'CDLHANGINGMAN',
                            'CDLDARKCLOUDCOVER', 'CDLEVENINGSTAR', 'CDLENGULFING',
                            'CDLENGULFINGBULLISH', 'CDLENGULFINGBEARISH']

                df.loc[:window_size, subset] = df.loc[:window_size, subset].replace([100, -100],[0, 0])

                # Format data type
                df['quote_asset_volume'] = df['quote_asset_volume'].astype(float)
                df['taker_buy_base_asset_volume'] = df['taker_buy_base_asset_volume'].astype(float)
                df['taker_buy_quote_asset_volume'] = df['taker_buy_quote_asset_volume'].astype(float)
                df['ignore'] = df['ignore'].astype(int)
                df['formatted_open_time'] = pd.to_datetime(df['date'])
                df['formatted_close_time'] = pd.to_datetime(df['date'])
                df['date'] = pd.to_datetime(df['date'])

                # Write to the db
                engine = create_engine(db_address, echo=False)
                sqlite_connection = engine.connect()

                output_tbl_name = "tbl_raw_candlesticks_signals" + "_" + asset_ticket + "_" + timestamp

                df.to_sql(output_tbl_name, sqlite_connection, if_exists='append', index=False)

                sqlite_connection.close()

    except Exception as e:
        logger.error(e)

def validate_candlesitck_patterns(list_asset_ticket, list_timestamp, db_address, start_date="", end_date=""):
    try:
        for asset_ticket in list_asset_ticket:
            for timestamp in list_timestamp:

                engine = create_engine(db_address, echo=False)
                sqlite_connection = engine.connect()

                input_tbl_name = "tbl_raw_candlesticks_signals" + "_" + asset_ticket + "_" + timestamp
                
                sql_command = "SELECT * FROM " + input_tbl_name

                if(start_date!="" and end_date!=""):
                    
                    sd = datetime.datetime.strptime(start_date,'%d %b, %Y').strftime('%Y-%m-%d')
                    ed = datetime.datetime.strptime(end_date,'%d %b, %Y').strftime('%Y-%m-%d')

                    sql_append = " WHERE " + "date(date) >= " + "'" + sd + "'" + " AND date(date) <= " + "'" + ed + "'"
                    sql_command = sql_command + sql_append

                df = pd.read_sql(sql_command, sqlite_connection)

                # Set the index on the dataframe
                df['date_index'] = df['date']
                df.set_index('date_index', inplace=True)

                # Set some parameters
                window_size = configur.getint('candlestick_patterns', 'window_size')
                slope_size = configur.getint('candlestick_patterns', 'slope_size')

                # Get the dates from the bullish candlesticks patterns
                list_dates_invertedhammer = df[df['CDLINVERTEDHAMMER'] == 100]['date'].to_list()
                list_dates_hammer = df[df['CDLHAMMER'] == 100]['date'].to_list()
                list_dates_piercing = df[df['CDLPIERCING'] == 100]['date'].to_list()
                list_dates_morningstar = df[df['CDLMORNINGSTAR'] == 100]['date'].to_list()
                list_dates_bullishengulfing = df[df['CDLENGULFINGBULLISH'] == 100]['date'].to_list()

                # Get all dates
                list_all_dates = df['date'].to_list()

                # Run the checks to identify the real candlesticks with reversal
                list_validate_dates_invertedhammer = []
                list_new_sign_invertedhammer = []
                list_sign_invertedhammer = [0] * len(list_all_dates)
                for date in list_dates_invertedhammer:
                    i = u.check_intensity_trend(df, date, window_size, slope_size)
                    if(i >= 0):
                        list_validate_dates_invertedhammer.append(date)
                        list_new_sign_invertedhammer.append(i*100)
                        list_sign_invertedhammer[list_all_dates.index(date)] = i*100


                list_validate_dates_hammer = []
                list_new_sign_hammer = []
                list_sign_hammer = [0] * len(list_all_dates)
                for date in list_dates_hammer:
                    i = u.check_intensity_trend(df, date, window_size, slope_size)
                    if(i >= 0):    
                        list_validate_dates_hammer.append(date)
                        list_new_sign_hammer.append(i*100)
                        list_sign_hammer[list_all_dates.index(date)] = i*100

                list_validate_dates_piercing = []
                list_new_sign_piercing = []
                list_sign_piercing = [0] * len(list_all_dates)
                for date in list_dates_piercing:
                    i = u.check_intensity_trend(df, date, window_size, slope_size)
                    if(i >= 0):
                        list_validate_dates_piercing.append(date)
                        list_new_sign_piercing.append(i*100)
                        list_sign_piercing[list_all_dates.index(date)] = i*100

                list_validate_dates_morningstar = []
                list_new_sign_morningstar = []
                list_sign_morningstar = [0] * len(list_all_dates)
                for date in list_dates_morningstar:
                    i = u.check_intensity_trend(df, date, window_size, slope_size)
                    if(i >= 0):
                        list_validate_dates_morningstar.append(date)
                        list_new_sign_morningstar.append(i*100)
                        list_sign_morningstar[list_all_dates.index(date)] = i*100

                list_validate_dates_bullishengulfing = []
                list_new_sign_bullishengulfing = []
                list_sign_bullishengulfing = [0] * len(list_all_dates)
                for date in list_dates_bullishengulfing:
                    i = u.check_intensity_trend(df, date, window_size, slope_size)
                    # print(f'date:{date}|i:{i}')
                    if(i >= 0):
                        list_validate_dates_bullishengulfing.append(date)
                        list_new_sign_bullishengulfing.append(i*100)
                        list_sign_bullishengulfing[list_all_dates.index(date)] = i*100

                # Get the dates from the bearish candlesticks patterns
                list_dates_shootingstar = df[df['CDLSHOOTINGSTAR'] == -100]['date'].to_list()
                list_dates_hangingman = df[df['CDLHANGINGMAN'] == -100]['date'].to_list()
                list_dates_darkcloudcover = df[df['CDLDARKCLOUDCOVER'] == -100]['date'].to_list()
                list_dates_eveningstar = df[df['CDLEVENINGSTAR'] == -100]['date'].to_list()
                list_dates_bearishengulfing = df[df['CDLENGULFINGBEARISH'] == -100]['date'].to_list()

                # Run the checks to identify the real candlesticks with reversal
                list_validate_dates_shootingstar = []
                list_new_sign_shootingstar = []
                list_sign_shootingstar = [0] * len(list_all_dates)
                for date in list_dates_shootingstar:
                    i = u.check_intensity_trend(df, date, window_size, slope_size)
                    if (i<=0):
                        list_validate_dates_shootingstar.append(date)
                        list_new_sign_shootingstar.append(i*100)
                        list_sign_shootingstar[list_all_dates.index(date)] = i*100


                list_validate_dates_hangingman = []
                list_new_sign_hangingman = []
                list_sign_hangingman = [0] * len(list_all_dates)
                for date in list_dates_hangingman:
                    i = u.check_intensity_trend(df, date, window_size, slope_size)
                    if (i<=0):
                        list_validate_dates_hangingman.append(date)
                        list_new_sign_hangingman.append(i*100)
                        list_sign_hangingman[list_all_dates.index(date)] = i*100

                list_validate_dates_darkcloudcover = []
                list_new_sign_darkcloudcover = []
                list_sign_darkcloudcover = [0] * len(list_all_dates)
                for date in list_dates_darkcloudcover:
                    i = u.check_intensity_trend(df, date, window_size, slope_size)
                    if (i<=0):
                        list_validate_dates_darkcloudcover.append(date)
                        list_new_sign_darkcloudcover.append(i*100)
                        list_sign_darkcloudcover[list_all_dates.index(date)] = i*100  

                list_validate_dates_eveningstar = []
                list_new_sign_eveningstar = []
                list_sign_eveningstar = [0] * len(list_all_dates)
                for date in list_dates_eveningstar:
                    i = u.check_intensity_trend(df, date, window_size, slope_size)
                    if (i<=0):
                        list_validate_dates_eveningstar.append(date)
                        list_new_sign_eveningstar.append(i*100)
                        list_sign_eveningstar[list_all_dates.index(date)] = i*100

                list_validate_dates_bearishengulfing = []
                list_new_sign_bearishengulfing = []
                list_sign_bearishengulfing = [0] * len(list_all_dates)
                for date in list_dates_bearishengulfing:
                    i = u.check_intensity_trend(df, date, window_size, slope_size)
                    if (i<=0):
                        list_validate_dates_bearishengulfing.append(date)
                        list_new_sign_bearishengulfing.append(i*100)
                        list_sign_bearishengulfing[list_all_dates.index(date)] = i*100

                # Create the data with the validation results

                list_new_column_name_pos = ['CDLINVERTEDHAMMER_NEW', 'CDLHAMMER_NEW', 'CDLPIERCING_NEW', 'CDLMORNINGSTAR_NEW', 'CDLENGULFINGBULLISH_NEW']
                list_new_column_name_neg = ['CDLSHOOTINGSTAR_NEW', 'CDLHANGINGMAN_NEW', 'CDLDARKCLOUDCOVER_NEW', 'CDLEVENINGSTAR_NEW', 'CDLENGULFINGBEARISH_NEW']

                list_of_list_valid_dates_pos = [list_validate_dates_invertedhammer, list_validate_dates_hammer, list_validate_dates_piercing, list_validate_dates_morningstar, list_validate_dates_bullishengulfing]
                list_of_list_valid_dates_neg = [list_validate_dates_shootingstar, list_validate_dates_hangingman, list_validate_dates_darkcloudcover, list_validate_dates_eveningstar, list_validate_dates_bearishengulfing]

                list_of_list_sign_pos = [list_sign_invertedhammer, list_sign_hammer, list_sign_piercing, list_sign_morningstar, list_sign_bullishengulfing]
                list_of_list_sign_neg = [list_sign_shootingstar, list_sign_hangingman, list_sign_darkcloudcover, list_sign_eveningstar, list_sign_bearishengulfing]

                for i in range(0, len(list_new_column_name_pos)):
                    df[list_new_column_name_pos[i]] = np.where(df['date'].isin(list_of_list_valid_dates_pos[i]), list_of_list_sign_pos[i], 0)

                for i in range(0, len(list_new_column_name_neg)):
                    df[list_new_column_name_neg[i]] = np.where(df['date'].isin(list_of_list_valid_dates_neg[i]), list_of_list_sign_neg[i], 0)

                # Format data type
                df['quote_asset_volume'] = df['quote_asset_volume'].astype(float)
                df['taker_buy_base_asset_volume'] = df['taker_buy_base_asset_volume'].astype(float)
                df['taker_buy_quote_asset_volume'] = df['taker_buy_quote_asset_volume'].astype(float)
                df['ignore'] = df['ignore'].astype(int)
                df['formatted_open_time'] = pd.to_datetime(df['date'])
                df['formatted_close_time'] = pd.to_datetime(df['date'])
                df['date'] = pd.to_datetime(df['date'])

                # Write to the db
                engine = create_engine(db_address, echo=False)
                sqlite_connection = engine.connect()

                output_tbl_name = "tbl_candlesticks_signals_processed" + "_" + asset_ticket + "_" + timestamp

                df.to_sql(output_tbl_name, sqlite_connection, if_exists='append', index=False)

                sqlite_connection.close()                

    except Exception as e:
        logger.error(e)

def create_technical_indicators_df(df_price_ohcl):
    try:
        o = df_price_ohcl['open'].values
        c = df_price_ohcl['close'].values
        h = df_price_ohcl['high'].values
        l = df_price_ohcl['low'].values
        v = df_price_ohcl['volume'].astype(float).values
        
        # Most data series are normalized by their series' mean
        ta = df_price_ohcl.copy()
        
        #ta['reference_date'] = df_price_ohcl.index
        
        # All Moving Average
        ta['MA5'] = tb.MA(c, timeperiod=5) #/ tb.MA(c, timeperiod=5).mean()
        ta['MA10'] = tb.MA(c, timeperiod=10) #/ tb.MA(c, timeperiod=10).mean()
        ta['MA20'] = tb.MA(c, timeperiod=20) #/ tb.MA(c, timeperiod=20).mean()
        ta['MA60'] = tb.MA(c, timeperiod=60) #/ tb.MA(c, timeperiod=60).mean()
        ta['MA120'] = tb.MA(c, timeperiod=120) #/ tb.MA(c, timeperiod=120).mean()
        ta['volume_MA5'] = tb.MA(v, timeperiod=5) #/ tb.MA(v, timeperiod=5).mean()
        ta['volume_MA10'] = tb.MA(v, timeperiod=10) #/ tb.MA(v, timeperiod=10).mean()
        ta['volume_MA20'] = tb.MA(v, timeperiod=20) #/ tb.MA(v, timeperiod=20).mean()
        
        # Simple Moving Average (SMA)
        ta['SMA5'] = tb.SMA(c, timeperiod=5) #/ tb.SMA(c, timeperiod=5).mean()
        ta['SMA10'] = tb.SMA(c, timeperiod=10) #/ tb.SMA(c, timeperiod=10).mean()
        ta['SMA20'] = tb.SMA(c, timeperiod=20) #/ tb.SMA(c, timeperiod=20).mean()
        ta['SMA60'] = tb.SMA(c, timeperiod=60) #/ tb.SMA(c, timeperiod=60).mean()
        ta['SMA120'] = tb.SMA(c, timeperiod=120) #/ tb.SMA(c, timeperiod=120).mean()
        ta['volume_SMA5'] = tb.SMA(v, timeperiod=5) #/ tb.SMA(v, timeperiod=5).mean()
        ta['volume_SMA10'] = tb.SMA(v, timeperiod=10) #/ tb.SMA(v, timeperiod=10).mean()
        ta['volume_SMA20'] = tb.SMA(v, timeperiod=20) #/ tb.SMA(v, timeperiod=20).mean()
        
        # Weighted Moving Average (WMA)
        ta['WMA5'] = tb.WMA(c, timeperiod=5) #/ tb.WMA(c, timeperiod=5).mean()
        ta['WMA10'] = tb.WMA(c, timeperiod=10) #/ tb.WMA(c, timeperiod=10).mean()
        ta['WMA20'] = tb.WMA(c, timeperiod=20) #/ tb.WMA(c, timeperiod=20).mean()
        ta['WMA60'] = tb.WMA(c, timeperiod=60) #/ tb.WMA(c, timeperiod=60).mean()
        ta['WMA120'] = tb.WMA(c, timeperiod=120) #/ tb.WMA(c, timeperiod=120).mean()
        ta['volume_WMA5'] = tb.WMA(v, timeperiod=5) #/ tb.WMA(v, timeperiod=5).mean()
        ta['volume_WMA10'] = tb.WMA(v, timeperiod=10) #/ tb.WMA(v, timeperiod=10).mean()
        ta['volume_WMA20'] = tb.WMA(v, timeperiod=20) #/ tb.WMA(v, timeperiod=20).mean()
        
        # Exponential Moving Average (EMA)
        ta['EMA5'] = tb.EMA(c, timeperiod=5) #/ tb.WMA(c, timeperiod=5).mean()
        ta['EMA10'] = tb.EMA(c, timeperiod=10) #/ tb.WMA(c, timeperiod=10).mean()
        ta['EMA20'] = tb.EMA(c, timeperiod=20) #/ tb.WMA(c, timeperiod=20).mean()
        ta['EMA60'] = tb.EMA(c, timeperiod=60) #/ tb.WMA(c, timeperiod=60).mean()
        ta['EMA120'] = tb.EMA(c, timeperiod=120) #/ tb.WMA(c, timeperiod=120).mean()
        ta['volume_EMA5'] = tb.EMA(v, timeperiod=5) #/ tb.WMA(v, timeperiod=5).mean()
        ta['volume_EMA10'] = tb.EMA(v, timeperiod=10) #/ tb.WMA(v, timeperiod=10).mean()
        ta['volume_EMA20'] = tb.EMA(v, timeperiod=20) #/ tb.WMA(v, timeperiod=20).mean()        
        
        # William'%R (WILLR)
        ta['WILLR_14'] = tb.WILLR(h, l, c, timeperiod=14)
        
        # Normalized Average True Range (NATR)
        ta['NATR_14'] = tb.NATR(h, l, c, timeperiod=14)
        
        # Percentage Price Oscillator (PPO)
        ta['PPO_12_26'] = tb.PPO(c, fastperiod=12, slowperiod=26, matype=0)
        
        # Commodity Channel Index (CCI)
        ta['CCI_14'] = tb.CCI(h, l, c, timeperiod=14)
        
        # Average Directional Movement Index
        ta['ADX_14'] = tb.ADX(h, l, c, timeperiod=14) #/ tb.ADX(h, l, c, timeperiod=14).mean()
        
        # Average Directional Movement Index Rating
        ta['ADXR_14'] = tb.ADXR(h, l, c, timeperiod=14) #/ tb.ADXR(h, l, c, timeperiod=14).mean()

        # Moving Average Convergence/Divergence
        ta['MACD_12_26_9'] = tb.MACD(c, fastperiod=12, slowperiod=26, signalperiod=9)[0] #/ tb.MACD(c, fastperiod=12, slowperiod=26, signalperiod=9)[0].mean()
        
        # Relative Strength Index
        ta['RSI_14'] = tb.RSI(c, timeperiod=14) #/ tb.RSI(c, timeperiod=14).mean()
        
        # Bollinger Bands
        ta['BBANDS_U'] = tb.BBANDS(c, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)[0] #/ \tb.BBANDS(c, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)[0].mean()
        ta['BBANDS_M'] = tb.BBANDS(c, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)[1] #/ \tb.BBANDS(c, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)[1].mean()
        ta['BBANDS_L'] = tb.BBANDS(c, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)[2] #/ tb.BBANDS(c, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)[2].mean()

        # Chaikin A/D Line
        ta['AD'] = tb.AD(h, l, c, v) #/ tb.AD(h, l, c, v).mean()
        
        # Average True Range
        ta['ATR'] = tb.ATR(h, l, c, timeperiod=14) #/ tb.ATR(h, l, c, timeperiod=14).mean()
        
        # Hilbert Transform - Dominant Cycle Period
        ta['HT_DC'] = tb.HT_DCPERIOD(c) #/ tb.HT_DCPERIOD(c).mean()

        # Parabolic SAR
        ta['SAR'] = tb.SAR(h, l, acceleration=0.02, maximum=0.2)        
        
        # prices ratio
        ta["ratio_high_open"] = h / o
        ta["ratio_low_open"] = l / o
        ta["ratio_close_open"] = c / o
        
        return ta
        
    except Exception as e:
        logger.error(e)

def create_risk_and_technical_indicators(list_asset_ticket, list_timestamp, db_address, start_date="", end_date=""):
    try:
        for asset_ticket in list_asset_ticket:
            for timestamp in list_timestamp:

                engine = create_engine(db_address, echo=False)
                sqlite_connection = engine.connect()

                input_tbl_name = "tbl_candlesticks_signals_processed" + "_" + asset_ticket + "_" + timestamp
                
                sql_command = "SELECT * FROM " + input_tbl_name

                if(start_date!="" and end_date!=""):
                    
                    sd_temp = datetime.datetime.strptime(start_date,'%d %b, %Y').strftime('%Y-%m-%d')
                    sd_dt = datetime.datetime.strptime(sd_temp,'%Y-%m-%d')
                    sd_dt = sd_dt + datetime.timedelta(days=-180)
                    sd = sd_dt.strftime('%Y-%m-%d')
                    ed = datetime.datetime.strptime(end_date,'%d %b, %Y').strftime('%Y-%m-%d')

                    sql_append = " WHERE " + "date(date) >= " + "'" + sd + "'" + " AND date(date) <= " + "'" + ed + "'"
                    sql_command = sql_command + sql_append

                df = pd.read_sql(sql_command, sqlite_connection)

                # Set the index on the dataframe
                df['date_index'] = df['date']
                df.set_index('date_index', inplace=True)
                
                df = create_technical_indicators_df(df)
                df = df.dropna()

                # Format data type
                df['quote_asset_volume'] = df['quote_asset_volume'].astype(float)
                df['taker_buy_base_asset_volume'] = df['taker_buy_base_asset_volume'].astype(float)
                df['taker_buy_quote_asset_volume'] = df['taker_buy_quote_asset_volume'].astype(float)
                df['ignore'] = df['ignore'].astype(int)
                df['formatted_open_time'] = pd.to_datetime(df['date'])
                df['formatted_close_time'] = pd.to_datetime(df['date'])
                df['date'] = pd.to_datetime(df['date'])

                # Write to the db
                engine = create_engine(db_address, echo=False)
                sqlite_connection = engine.connect()

                output_tbl_name = "tbl_candlesticks_processed_risk_technical_indicators" + "_" + asset_ticket + "_" + timestamp

                df.to_sql(output_tbl_name, sqlite_connection, if_exists='append', index=False)

                sqlite_connection.close()

    except Exception as e:
        logger.error(e)

def create_crypto_index(list_asset_ticket, list_timestamp, db_address, start_date="", end_date=""):
    try:
        for asset_ticket in list_asset_ticket:
            for timestamp in list_timestamp:

                engine = create_engine(db_address, echo=False)
                sqlite_connection = engine.connect()

                input_tbl_name = "tbl_candlesticks_processed_risk_technical_indicators" + "_" + asset_ticket + "_" + timestamp
                
                sql_command = "SELECT * FROM " + input_tbl_name

                if(start_date!="" and end_date!=""):
                    
                    sd_temp = datetime.datetime.strptime(start_date,'%d %b, %Y').strftime('%Y-%m-%d')
                    sd_dt = datetime.datetime.strptime(sd_temp,'%Y-%m-%d')
                    sd_dt = sd_dt + datetime.timedelta(days=-10)
                    sd = sd_dt.strftime('%Y-%m-%d')
                    ed = datetime.datetime.strptime(end_date,'%d %b, %Y').strftime('%Y-%m-%d')

                    sql_append = " WHERE " + "date(date) >= " + "'" + sd + "'" + " AND date(date) <= " + "'" + ed + "'"
                    sql_command = sql_command + sql_append

                df = pd.read_sql(sql_command, sqlite_connection)

                # Set the index on the dataframe
                df['date_index'] = df['date']
                df.set_index('date_index', inplace=True)

                df['time_to_chart_return'] = (df['close']/ df['close'].shift(1)) -1

                # Drop all Not a number values using drop method.
                df.dropna(inplace = True)

                # Add the [crypto_index]
                df['crypto_index'] = ((1 + df['time_to_chart_return']).cumprod()) * 1000

                # Format data type
                df['quote_asset_volume'] = df['quote_asset_volume'].astype(float)
                df['taker_buy_base_asset_volume'] = df['taker_buy_base_asset_volume'].astype(float)
                df['taker_buy_quote_asset_volume'] = df['taker_buy_quote_asset_volume'].astype(float)
                df['ignore'] = df['ignore'].astype(int)
                df['formatted_open_time'] = pd.to_datetime(df['date'])
                df['formatted_close_time'] = pd.to_datetime(df['date'])
                df['date'] = pd.to_datetime(df['date'])

                # Write to the db
                engine = create_engine(db_address, echo=False)
                sqlite_connection = engine.connect()

                output_tbl_name = "tbl_all_features" + "_" + asset_ticket + "_" + timestamp

                df.to_sql(output_tbl_name, sqlite_connection, if_exists='append', index=False)

                sqlite_connection.close()

    except Exception as e:
        logger.error(e)    
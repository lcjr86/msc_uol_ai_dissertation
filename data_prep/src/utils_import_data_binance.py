
from binance.client import Client
from dotenv import load_dotenv
import os
import pandas as pd
import datetime
import sqlite3
from sqlalchemy import create_engine

import logging

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Create and configure logger
logging.basicConfig(filename="logs/utils_import_data_binance.log",
                    level=logging.INFO,
                    format='%(name)s|%(asctime)s|%(levelname)s|[%(filename)s:%(lineno)s - %(funcName)20s() ]|%(message)s',
                    filemode='w')

# Creating an object
logger = logging.getLogger()

def get_raw_period_date_data_binance(list_asset_ticket, list_timestamp, db_address, now_flag, start_date, end_date):
    try:

        load_dotenv(dotenv_path='../config_files/.env')

        # Create the Binance API client
        client = Client(os.environ["BINANCE_API_KEY"], os.environ["BINANCE_SECRET_KEY"])

        for asset_ticket in list_asset_ticket:
            for timestamp in list_timestamp:
                
                logger.info(f'asset_ticket:{asset_ticket}')
                logger.info(f'timestamp:{timestamp}')

                # Get the data
                if(now_flag):
                    klines = client.get_historical_klines(asset_ticket, timestamp, start_date)
                else:
                    klines = client.get_historical_klines(asset_ticket, timestamp, start_date, end_date)
                logger.info("Get data from API completed")

                # Convert list of lists to pandas df
                df_klines = pd.DataFrame(klines, columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
                logger.info("Convert data to df completed")

                # Copy original data to other dataframe
                df_klines_copy = df_klines.copy()

                # Convert 'object' to float pandas
                df_klines_copy['open'] = pd.to_numeric(df_klines_copy['open'])
                df_klines_copy['high'] = pd.to_numeric(df_klines_copy['high'])
                df_klines_copy['low'] = pd.to_numeric(df_klines_copy['low'])
                df_klines_copy['close'] = pd.to_numeric(df_klines_copy['close'])
                df_klines_copy['volume'] = pd.to_numeric(df_klines_copy['volume'])

                # Convert the 'open_time' and 'close_time' to a Pandas DataTime format
                df_klines_copy['formatted_open_time'] = pd.to_datetime(df_klines_copy['open_time'], infer_datetime_format=True, unit="ms")
                df_klines_copy['formatted_close_time'] = pd.to_datetime(df_klines_copy['close_time'], infer_datetime_format=True, unit="ms")

                # Set the index on the dataframe
                # Converting Date Column to DateTime Type
                df_klines_copy['date'] = pd.to_datetime(df_klines_copy['formatted_close_time']) + pd.to_timedelta(1, unit='s')
                df_klines_copy['date'] = pd.to_datetime(df_klines_copy['date']).dt.strftime('%Y-%m-%d %H:%M:%S')

                # Format data type
                df_klines_copy['quote_asset_volume'] = df_klines_copy['quote_asset_volume'].astype(float)
                df_klines_copy['taker_buy_base_asset_volume'] = df_klines_copy['taker_buy_base_asset_volume'].astype(float)
                df_klines_copy['taker_buy_quote_asset_volume'] = df_klines_copy['taker_buy_quote_asset_volume'].astype(float)
                df_klines_copy['ignore'] = df_klines_copy['ignore'].astype(int)
                df_klines_copy['date'] = pd.to_datetime(df_klines_copy['date'])

                logger.info("Datatype convertions completed")

                # Create the 'upper_shadow', 'lower_shadow' and 'real_body' values (to compose the CURL)
                df_klines_copy = create_curl_values(df_klines_copy)

                logger.info("CURL creation completed")

                # Write to the db
                engine = create_engine(db_address, echo=False)
                sqlite_connection = engine.connect()

                output_tbl_name = "tbl_raw_binance" + \
                                "_" + asset_ticket + \
                                "_" + timestamp

                df_klines_copy.to_sql(output_tbl_name, sqlite_connection, if_exists='append', index=False)

                sqlite_connection.close()

                logger.info("Export data completed")        

    except Exception as e:
        logger.error(e)

def get_raw_1y_data_binance(list_asset_ticket, list_timestamp, list_year, db_address):
    try:

        load_dotenv(dotenv_path='../config_files/.env')

        # Create the Binance API client
        client = Client(os.environ["BINANCE_API_KEY"], os.environ["BINANCE_SECRET_KEY"])

        prefix_start_date = "1 Jan, "
        prefix_end_date = "1 Jan, "

        for y in range(0,len(list_year)-1):
            
            start_date = prefix_start_date + str(list_year[y])
            end_date = prefix_end_date + str(list_year[y+1])

            for asset_ticket in list_asset_ticket:
                for timestamp in list_timestamp:
                    
                    logger.info(f'asset_ticket:{asset_ticket}')
                    logger.info(f'timestamp:{timestamp}')

                    # Get the data
                    klines = client.get_historical_klines(asset_ticket, timestamp, start_date, end_date)
                    logger.info("Get data from API completed")

                    # Convert list of lists to pandas df
                    df_klines = pd.DataFrame(klines, columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
                    logger.info("Convert data to df completed")

                    # Copy original data to other dataframe
                    df_klines_copy = df_klines.copy()

                    # Convert 'object' to float pandas
                    df_klines_copy['open'] = pd.to_numeric(df_klines_copy['open'])
                    df_klines_copy['high'] = pd.to_numeric(df_klines_copy['high'])
                    df_klines_copy['low'] = pd.to_numeric(df_klines_copy['low'])
                    df_klines_copy['close'] = pd.to_numeric(df_klines_copy['close'])
                    df_klines_copy['volume'] = pd.to_numeric(df_klines_copy['volume'])

                    # Convert the 'open_time' and 'close_time' to a Pandas DataTime format
                    df_klines_copy['formatted_open_time'] = pd.to_datetime(df_klines_copy['open_time'], infer_datetime_format=True, unit="ms")
                    df_klines_copy['formatted_close_time'] = pd.to_datetime(df_klines_copy['close_time'], infer_datetime_format=True, unit="ms")

                    # Set the index on the dataframe
                    # Converting Date Column to DateTime Type
                    df_klines_copy['date'] = pd.to_datetime(df_klines_copy['formatted_close_time']) + pd.to_timedelta(1, unit='s')
                    df_klines_copy['date'] = pd.to_datetime(df_klines_copy['date']).dt.strftime('%Y-%m-%d %H:%M:%S')

                    # Format data type
                    df_klines_copy['quote_asset_volume'] = df_klines_copy['quote_asset_volume'].astype(float)
                    df_klines_copy['taker_buy_base_asset_volume'] = df_klines_copy['taker_buy_base_asset_volume'].astype(float)
                    df_klines_copy['taker_buy_quote_asset_volume'] = df_klines_copy['taker_buy_quote_asset_volume'].astype(float)
                    df_klines_copy['ignore'] = df_klines_copy['ignore'].astype(int)
                    df_klines_copy['date'] = pd.to_datetime(df_klines_copy['date'])

                    logger.info("Datatype convertions completed")

                    # Create the 'upper_shadow', 'lower_shadow' and 'real_body' values (to compose the CURL)
                    df_klines_copy = create_curl_values(df_klines_copy)

                    logger.info("CURL creation completed")

                    # Write to the db
                    engine = create_engine(db_address, echo=False)
                    sqlite_connection = engine.connect()

                    output_tbl_name = "tbl_raw_binance" + \
                                    "_" + asset_ticket + \
                                    "_" + timestamp

                    df_klines_copy.to_sql(output_tbl_name, sqlite_connection, if_exists='append',index=False)

                    sqlite_connection.close()

                    logger.info("Export data completed")        

    except Exception as e:
        logger.error(e)

def create_curl_values(df):
    try:
        results_upper_shadow = []
        results_lower_shadow = []
        results_real_body = []
        for index, row in df.iterrows():
            if row.open > row.close:
                results_upper_shadow.append(row.high - row.open)
                results_lower_shadow.append(row.close - row.low)
                results_real_body.append(row.open - row.close)
            else:
                results_upper_shadow.append(row.high - row.close)
                results_lower_shadow.append(row.open - row.low)
                results_real_body.append(row.close - row.open)

        df['upper_shadow'] = results_upper_shadow
        df['lower_shadow'] = results_lower_shadow
        df['real_body'] = results_real_body

        return df

    except Exception as e:
        logger.error(e)
# Python program to demonstrate
# main() function

from binance.client import Client
import utils_import_data_binance as uidb
import utils_feature_engineering as ufe

import logging

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Create and configure logger
logging.basicConfig(filename="logs/pipeline_full_year.log",
                    level=logging.INFO,
                    format='%(name)s|%(asctime)s|%(levelname)s|[%(filename)s:%(lineno)s - %(funcName)20s() ]|%(message)s',
                    filemode='w')

# Creating an object
logger = logging.getLogger()

# Defining main function
def main():
    
    ### Initial inputs
    #list_asset_ticket = ["BTCUSDT"]
    #list_timestamp = [Client.KLINE_INTERVAL_1DAY]
    list_asset_ticket = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    list_timestamp = [Client.KLINE_INTERVAL_5MINUTE, Client.KLINE_INTERVAL_15MINUTE, Client.KLINE_INTERVAL_30MINUTE, Client.KLINE_INTERVAL_1HOUR, Client.KLINE_INTERVAL_1DAY]
    #list_timestamp = [Client.KLINE_INTERVAL_1MINUTE]
    list_year = [2017, 2018, 2019, 2020, 2021, 2022, 2023]
    #list_year = [2022, 2023]

    db_address = 'sqlite:///../../data/db/crypto.db'

    logger.info("start ufe.get_raw_1y_data_binance")
    uidb.get_raw_1y_data_binance(list_asset_ticket, list_timestamp, list_year, db_address)
    logger.info("end ufe.get_raw_1y_data_binance")

    logger.info("start ufe.get_candlestick_patterns")
    ufe.create_candlestick_patterns(list_asset_ticket, list_timestamp, db_address)
    logger.info("end ufe.get_candlestick_patterns")

    logger.info("start ufe.validate_candlesitck_patterns")
    ufe.validate_candlesitck_patterns(list_asset_ticket, list_timestamp, db_address)
    logger.info("end ufe.validate_candlesitck_patterns")

    logger.info("start ufe.create_risk_and_technical_indicators")
    ufe.create_risk_and_technical_indicators(list_asset_ticket, list_timestamp, db_address)
    logger.info("end ufe.create_risk_and_technical_indicators")

    logger.info("start ufe.create_crypto_index")
    ufe.create_crypto_index(list_asset_ticket, list_timestamp, db_address)
    logger.info("end ufe.create_crypto_index")

# Using the special variable 
# __name__
if __name__=="__main__":
    main()
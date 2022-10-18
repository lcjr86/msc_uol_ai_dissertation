from re import L
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn import preprocessing
from statsmodels.tsa.api import SimpleExpSmoothing
import math
import numpy as np
import logging

# Create and configure logger
logging.basicConfig(filename="logs/tests_utils.log",
                    format='%(name)s|%(asctime)s|%(levelname)s|[%(filename)s:%(lineno)s - %(funcName)20s() ]|%(message)s',
                    filemode='w')

# Creating an object
logger = logging.getLogger()
 
# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)

# def test_log():
#     logger.info("test")

def reverse_list(lst):
    try:
        reversed_lst = []
        
        # iterate to reverse the list
        for i in lst:
            # reversing the list
            reversed_lst.insert(0, i)
        
        return reversed_lst

    except Exception as e:
        logger.error("Exception occurred", exc_info=True)

def check_candlestick_color(df_ohlc):
    try:
        if df_ohlc['open'].value > df_ohlc['close']:
            return "black"
        elif df_ohlc['open'].value < df_ohlc['close']:
            return "white"
        else:
            return "no_color"
    except Exception as e:
        logger.error("Exception occurred", exc_info=True)

def check_morning_star_signal(df_ohlc):
    '''
        Input: 
            Dataframe with the reference dates (index) + OHLC with the 'potential' date of the signal in the middle (D0);
            Ex: 
                Reference_dates: [D-3, D-2, D-1, D0, D+1, D+2, D+3]
        Output:
            left_sign, right_sign
    '''

    try:
        pass
    except Exception as e:
        logger.error("Exception occurred", exc_info=True)

def check_reversal(df, event_date, window_size):
    try:
        #get the location of the event_date
        idx = df.index.get_loc(event_date)

        #get the data from that interval
        df_temp = df.iloc[idx - window_size : idx + window_size + 1]

        #Predict the trend from the left side
        x_left = df_temp[df_temp.index < event_date].open_time.values.reshape((-1,1))
        y_left = df_temp[df_temp.index < event_date].close.values

        model_left = LinearRegression()

        model_left.fit(x_left, y_left)
        
        left_sign = math.copysign(1,model_left.coef_[0])

        #Predict the trend from the right side
        x_right = df_temp[df_temp.index > event_date].open_time.values.reshape((-1,1))
        y_right = df_temp[df_temp.index > event_date].close.values

        model_right = LinearRegression()

        model_right.fit(x_right, y_right)

        right_sign = math.copysign(1,model_right.coef_[0])

        return left_sign, right_sign

    except Exception as e:
        logger.error("Exception occurred", exc_info=True)

def check_trend(df, event_date, window_size, slope_size):
    '''
        Input: 
            Dataframe with the reference dates (index) + OHLC with the 'potential' date of the signal in the end (last observed data);
            window_size: How many datapoints will be used (total window)
            slope_size: How many datapoints will be used on each slope
            Ex: 
                Reference_dates: [D-n, ..., D-3, D-2, D-1, D0]
        Output:
            1: uptrend
            -1: downtrend
            0: no-trend
    '''    
    try:
        #get the location of the event_date
        idx = df.index.get_loc(event_date)

        #get the data from that interval
        df_temp = df.iloc[idx - window_size:idx + 1]

        list_coeficients = []
        for i in range(window_size, slope_size - 1, -1):
            df_slope_temp = df_temp[['open_time', 'close']].iloc[i-slope_size:i]
            x = df_slope_temp.open_time.values.reshape((-1,1))
            y = df_slope_temp.close.values
            model = LinearRegression()
            model.fit(x, y)
            list_coeficients.append(model.coef_[0])

        recent_slope_coef = list_coeficients[0]
        # logger.info(f'recent_slope_coef:{recent_slope_coef}')

        p70_all_slope_coef = np.percentile(list_coeficients, 70)
        # logger.info(f'p70_all_slope_coef:{p70_all_slope_coef}')
        
        sign_recent_slope_coef = math.copysign(1,recent_slope_coef)
        # logger.info(f'sign_recent_slope_coef:{sign_recent_slope_coef}')

        sign_p70_all_slope_coef = math.copysign(1,p70_all_slope_coef)
        # logger.info(f'sign_p70_all_slope_coef:{sign_p70_all_slope_coef}')

        if(sign_recent_slope_coef == sign_p70_all_slope_coef):
            return sign_recent_slope_coef
        else:
            return 0

    except Exception as e:
        logger.error("Exception occurred", exc_info=True)

def check_intensity_trend(df, event_date, window_size, slope_size):
    '''
        Input: 
            Dataframe with the reference dates (index) + OHLC with the 'potential' date of the signal in the end (last observed data);
            window_size: How many datapoints will be used (total window)
            slope_size: How many datapoints will be used on each slope
            Ex: 
                Reference_dates: [D-n, ..., D-3, D-2, D-1, D0]
        Output:
            the intensity
    '''    
    try:
        #get the location of the event_date
        idx = df.index.get_loc(event_date)

        #get the data from that interval
        df_temp = df.iloc[idx - window_size:idx + 1]

        list_coeficients = []
        for i in range(window_size, slope_size - 1, -1):
            df_slope_temp = df_temp[['open_time', 'close']].iloc[i-slope_size:i]
            x = df_slope_temp.open_time.values.reshape((-1,1))
            y = df_slope_temp.close.values
            model = LinearRegression()
            model.fit(x, y)
            list_coeficients.append(model.coef_[0])

        reversed_list_coeficients = reverse_list(list_coeficients)

        fit_SES_0dot2 = SimpleExpSmoothing(reversed_list_coeficients, initialization_method="heuristic").fit(smoothing_level=0.2, optimized=False)

        list_temp = np.array(fit_SES_0dot2.fittedvalues.tolist()).reshape(-1,1)
        scaler = preprocessing.MaxAbsScaler()
        normalizedlist=scaler.fit_transform(list_temp)
        reversed_list_coeficients_scaled = normalizedlist.reshape(1,-1)[0].tolist()

        intensity_index = sum(reversed_list_coeficients_scaled) / len(reversed_list_coeficients_scaled)

        return intensity_index

    except Exception as e:
        logger.error("Exception occurred", exc_info=True)
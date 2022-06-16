import pandas as pd

def check_candlestick_color(df_ohlc):
    try:
        if df_ohlc['open'].value > df_ohlc['close']:
            return "black"
        elif df_ohlc['open'].value < df_ohlc['close']:
            return "white"
        else:
            return "no_color"
    except Exception as e:
        print(e)

def check_morning_star_signal(df_ohlc):
    '''
        Input: 
            Dataframe with the reference dates (index) + OHLC with the 'potential' date of the signal in the middle (D0);
            Ex: 
                Reference_dates: [D-3, D-2, D-1, D0, D+1, D+2, D+3]
        Output:
            Boolean: True (confirmed event) or not (False)
    '''

    try:
        pass
    except Exception as e:
        print(e)
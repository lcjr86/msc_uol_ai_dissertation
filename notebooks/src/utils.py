import pandas as pd
from sklearn.linear_model import LinearRegression
import math

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
        print(e)
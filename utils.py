import streamlit as st
import os

@st.cache_data
def create_path_if_not_exists(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    return dir_name

def store_data_on_local_csv(store_path, df):
    if os.path.exists(store_path):
        df.to_csv(store_path, mode="a", header=False, index=False)
    else:
        df.to_csv(store_path, index=False)
        

def get_over_string(over_num, ball_num):
    if ball_num % 6 == 0:
        over_string = "({} Overs)".format(over_num)
    else:
        over_string = "({}.{} Overs)".format(over_num - 1, ball_num)
    return over_string


def get_current_run_rate(runs, over_num, ball_num):
    print(runs, over_num, ball_num)
    num_balls = (over_num - 1) * 6 + ball_num
    if num_balls > 0:
        return runs / num_balls * 6
    else:
        return 0
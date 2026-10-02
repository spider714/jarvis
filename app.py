import streamlit as st
import time
from datetime import datetime
import pandas as pd

ts = time.time()
date = datetime.fromtimestamp(ts).strftime("%d-%m-%y")
timestamp = datetime.fromtimestamp(ts).strftime("%H:%M-%S")
        
df =pd.read_csv("attendance/attendance_" + date + ".csv")

st.dataframe(df.style.highlight_max(axis =0))
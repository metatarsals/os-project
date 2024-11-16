import pandas as pd
from network_disk_battery_module import DiskMonitor
from collections import deque
import threading
import time
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    layout='wide'
)

package_data_manager = DiskMonitor().disk_generator

st.write("# Disk Monitor")
time_placeholder = st.empty()
col1,col2=st.columns([3,1])
col1.markdown("small descriptor for disks and monitoring them")
c1 = col1.empty()
col2.markdown("## important text shit here ig")

while True:
    with time_placeholder:
        st.write("Last Update: `" + str(time.time()) + "`")
    
    df,df1 = next(package_data_manager())

    with c1:
        tab1, tab2 = st.tabs(["Metrics", "Partition Details"])
        
        with tab1:
            c11, c12, c13, c14 = st.columns(4)
            with c11:
                st.metric('Read Count', list(df1['read_count'])[-1])
            with c12:
                st.metric('Write Count', list(df1['write_count'])[-1])
            with c13:
                st.metric('MB read', list(df1['read_bytes'])[-1])
            with c14:
                st.metric('MB written', list(df1['write_bytes'])[-1])
        
        with tab2:
            st.dataframe(df, use_container_width=True)
        


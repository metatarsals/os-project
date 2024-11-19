import pandas as pd
from process_module import Process_Analytics_Module
from collections import deque
import threading
import time
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    layout='wide'
)

package_data_manager = Process_Analytics_Module().generator

st.write("# Process Monitor")
time_placeholder = st.empty()
# col1,col2=st.columns(2)
# mem_g=col1.empty()
# cpu_g=col2.empty()
g = st.empty()
df_placeholder = st.empty()
k=0

while True:
    with time_placeholder:
        st.write("Last Update: `" + str(time.time()) + "`")
        df = next(package_data_manager())

    with g:
        if len(df)>0:
            # Initialize the figure
            fig = go.Figure()

            # Iterate over each process in the dataframe
            for index, row in df.iterrows():
                process_name = row['name']
                mem_percent = row['memory_percent']
                cpu_percent = row['cpu_percent']
                
                # Add a trace for the process
                fig.add_trace(go.Bar(
                    y=['memory usage', 'cpu usage'],
                    x=[mem_percent, cpu_percent],
                    name=process_name,
                    orientation="h",
                    width=0.2
                ))

            # Update layout
            fig.update_layout(
                title="Process Resource Usage",
                barmode='stack',  # Stack the bars
                yaxis={
                    'categoryorder': 'array',
                    'categoryarray': ['memory usage', 'cpu usage']
                },
                legend_title="Processes",
                bargap=0.001
            )

            # Display the chart using Streamlit
            st.plotly_chart(fig, use_container_width=True,key=f"key{k}")
            k+=1

            time.sleep(0.5)
            


    with df_placeholder:
        st.dataframe(df)
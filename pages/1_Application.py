import pandas as pd
from application_module import App_Analytics_Module
from collections import deque
import threading
import time
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    layout='wide'
)

package_data_manager = App_Analytics_Module().generator

st.write("# App Monitor")
time_placeholder = st.empty()
col1, col2, col3 = st.columns(3)

c1 = col1.empty()
c2 = col2.empty()
c3 = col3.empty()
df_placeholder = st.empty()

co1=0
co2=0
co3=0

while True: 
    with time_placeholder:
        st.write("Last Update: `" + str(time.time()) + "`")
    df = next(package_data_manager())
    
    with c1:
        if len(df) > 0:
            top_10 = df.nlargest(10, 'memory_usage(B)')
            
            # Convert bytes to MB for better readability
            top_10['memory_MB'] = top_10['memory_usage(B)'] / (1024 * 1024)
            
            fig1 = go.Figure(data=[
                go.Bar(
                    x=top_10['memory_MB'],
                    y=top_10['name'],
                    text=top_10['memory_MB'].round(2).astype(str) + ' MB',
                    textposition='auto',
                    marker=dict(
                        color="#9C4DDC",  # Outline for better visibility
                ), orientation="h"
                )
            ],layout=dict(
                barcornerradius=30,
            ))
            
            fig1.update_layout(
                title='By Memory Usage (in MB)',
                showlegend=False,
                height=300,
                margin=dict(t=30, l=0, r=0, b=0),
                xaxis_tickangle=-45,
                xaxis_visible=False,
                yaxis_visible=False,
                yaxis=dict(autorange="reversed")
            )
            
            st.plotly_chart(fig1, use_container_width=True, key= f"first{co1}")
            co1+=1
        else:
            st.write('Loading ...')

    with c2:
        if len(df) > 0:
            top_10 = df.nlargest(10, 'installed_size(B)')
            
            # Convert bytes to MB for better readability
            top_10['size_MB'] = top_10['installed_size(B)'] / (1024 * 1024)
            
            fig2 = go.Figure(data=[
                go.Bar(
                    x=top_10['size_MB'],
                    y=top_10['name'],
                    text=top_10['size_MB'].round(2).astype(str) + ' MB',
                    textposition='auto',
                    marker=dict(
                        color="#C57CFE",  # Outline for better visibility
                    ),
                    orientation="h"
                )
                    ],layout=dict(
                barcornerradius=10,
            ),)
            
            fig2.update_layout(
                title='By Installed Size (in MB)',
                showlegend=False,
                height=300,
                margin=dict(t=30, l=0, r=0, b=0),
                xaxis_tickangle=-45,
                xaxis_visible=False,
                yaxis_visible=False,
                yaxis=dict(autorange="reversed")
            )
            
            st.plotly_chart(fig2, use_container_width=True, key=f"second{co2}")
            co2+=1
        else:
            st.write('Loading ...')
    with c3:
        if len(df) > 0:
            top_10 = df.nlargest(10, 'memory_percentage(%)')
            
            # Create bar chart with log scale
            fig3 = go.Figure(data=[
                go.Bar(
                    x=top_10['memory_percentage(%)'],
                    y=top_10['name'],
                    text=top_10['memory_percentage(%)'].round(2).astype(str) + '%',
                    textposition='auto',
                    marker=dict(
                        color="#DFA9FD",  # Outline for better visibility
                ),orientation = "h"
                )
            ],layout=dict(
                barcornerradius=15,
            ))
            
            fig3.update_layout(
                title='Memory Usage Distribution',
                xaxis_type="log",  # Log scale for better visibility of small values
                showlegend=False,
                height=300,
                margin=dict(t=30, l=0, r=0, b=0),
                xaxis_tickangle=-45,
                xaxis_visible=False,
                yaxis_visible=False,
                yaxis=dict(autorange="reversed")
            )
            
            st.plotly_chart(fig3, use_container_width=True, key=f"third{co3}")
            co3+=1
        else:
            st.write('Loading ...')
        # st.write(time.time())
    

    with df_placeholder:
        st.dataframe(df)
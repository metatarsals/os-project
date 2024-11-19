import pandas as pd
from memory_module import Memory_Module
from collections import deque
import threading
import time
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    layout='wide'
)

package_data_manager = Memory_Module().generator


st.write("# Memory Monitor")
time_placeholder = st.empty()
# g_placeholder = st.empty()
col1, col2 = st.columns([2,1])
c1 = col1.empty()
col2.markdown(f"#### **then there's swap memory.**")
# col2.text(f"Swap is hard disk space used as RAM. It is (relatively speaking) very slow, but stops computers from crashing when they are trying to deal with more data then their RAM can handle. To stop processes from using swap — install more RAM.")
col2.markdown("""
*Swap is hard disk space used as RAM. It is (relatively speaking) very slow, 
but stops computers from crashing when they are trying to deal with more data 
than their RAM can handle. To stop processes from using swap — install more RAM.
This is the current state of your swap memory.*
""")
c2 = col2.empty()

# df_placeholder = st.empty()
k=0

while True:
    with time_placeholder:
        st.write("Last Update: `" + str(time.time()) + "`")

    df, df_swap = next(package_data_manager())

    with c1:
        if len(df)>0:
            fig = go.Figure(data=[go.Pie(
            labels=['Available', 'Used', 'Free', 'Buffers & Cached', 'Shared', 'Active'],
            values=[
                df['available'].iloc[0],
                df['used'].iloc[0],
                df['free'].iloc[0],
                df['buffers'].iloc[0] + df['cached'].iloc[0],
                df['shared'].iloc[0],
                df['active'].iloc[0]
            ],
            hole=0.8,
            marker=dict(colors=['#3498db', '#e74c3c', '#2ecc71', '#f1c40f', '#9b59b6', '#e67e22']),
            textinfo='none',
            hovertemplate="<b>%{label}</b><br>" +
                        "Amount: %{value:.2f} GB<br>" +
                        "Percentage of Total: %{percent}<br>" +
                        "<extra></extra>",
            
            )])

            fig.update_layout(
                title={
                    'text': f"your total memory is {df['total'].iloc[0]:.2f} GB. out of which,",
                    'y':0.95,
                    'x':0,
                    'xanchor': 'left',
                    'yanchor': 'top'
                },
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="left",
                    x=1.1
                ),
                height=600,
                margin=dict(t=0, l=0, r=0, b=150)
            )

            st.plotly_chart(fig, use_container_width=True,key=f"key{k}")
            k+=1

    with c2:
    #     c2.header(f"wellp")
        if len(df_swap)>0:

    #         upper_right_panel = st.container(height=200, border=True)
    #         # lower_right_panel = st.container(height=200, border=True)

    #         with upper_right_panel:
    #             "A bunch of text"

    #         # with lower_right_panel:
    #         #     c11, c12, c13 = st.columns(3)

            c11, c12, c13 = st.columns(3)

            with c11:
                st.metric('Total', list(df_swap['total'])[-1])
            with c12:
                st.metric('Free', list(df_swap['free'])[-1])
            with c13:
                st.metric('Used', list(df_swap['used'])[-1])
            

            
    # with df_placeholder:
    #     st.dataframe(df)


import pandas as pd
from cpu_module import CPUMonitor
from collections import deque
import threading
import time
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    layout='wide'
)

package_data_manager = CPUMonitor().monitor_cpu

st.write("# CPU Monitor")
time_placeholder = st.empty()

cols1, cols2, cols3, cols4 = st.columns(4)
c11 = cols1.empty()
c12 = cols2.empty()
c13 = cols3.empty()
c14 = cols4.empty()

col1,col2 = st.columns(2)
c1 = col1.empty()
c2 = col2.empty()

# cola, colb, colc, cold = st.columns(4)
# ca = cola.empty()
# cb = cola.empty()
# cc = cola.empty()
# cd = cola.empty()

while True: 
    with time_placeholder:
        st.write("Last Update: `" + str(time.time()) + "`")

    df = next(package_data_manager())
    num_cores = int((len(df.columns)-35)/12)
    
    with c1:
        if len(df) > 0:
            top_10 = df[['index', 'Overall_CPU_Usage']]

            # Create the Plotly line chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=top_10['index'], y=top_10['Overall_CPU_Usage'], mode='none', fill='tozeroy'))

            # Customize the chart
            fig.update_layout(
                title='your CPU needs a breather sometimes too.',
                xaxis_title='Index',
                yaxis_title='CPU Usage',
                xaxis_type='category',  # Treat 'index' as categorical data
                yaxis_range=[0, min(100, max(top_10['Overall_CPU_Usage']) + 10)],  # Set the y-axis range to 0-100
                xaxis_tickangle=-45,  # Rotate the x-axis labels by 45 degrees
                xaxis_visible=False  # Hide the x-axis labels
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.write('Loading ...')

    with c2:
        st.dataframe(df[['index','User Time','Overall_CPU_Usage']],use_container_width=True)
    
    # with ca:
    #     for i in range(1,num_cores+1):
    #         if i%4==1:
    #             core_usage = f'Core_{i}_Usage'
    #             graphed = df[['index',core_usage]]

    #             per_core_fig = go.Figure()
    #             per_core_fig.add_trace(go.Scatter(x=graphed['index'], y=graphed[core_usage], mode='lines'))
    #             per_core_fig.update_layout(
    #                 title=f'Core {i} Usage',
    #                 xaxis_type='category',  # Treat 'index' as categorical data
    #                 yaxis_range=[0, min(100, max(top_10['Overall_CPU_Usage']) + 10)],  # Set the y-axis range to 0-100
    #                 xaxis_visible=False  # Hide the x-axis labels
    #             )

    #             st.plotly_chart(per_core_fig, use_container_width=True)

    # with cb:
    #     for i in range(1,num_cores+1):
    #         if i%4==2:
    #             core_usage = f'Core_{i}_Usage'
    #             graphed = df[['index',core_usage]]

    #             per_core_fig = go.Figure()
    #             per_core_fig.add_trace(go.Scatter(x=graphed['index'], y=graphed[core_usage], mode='lines'))
    #             per_core_fig.update_layout(
    #                 title=f'Core {i} Usage',
    #                 xaxis_type='category',  # Treat 'index' as categorical data
    #                 yaxis_range=[0, min(100, max(top_10['Overall_CPU_Usage']) + 10)],  # Set the y-axis range to 0-100
    #                 xaxis_visible=False  # Hide the x-axis labels
    #             )

    #             st.plotly_chart(per_core_fig, use_container_width=True)

    # with cc:
    #     for i in range(1,num_cores+1):
    #         if i%4==3:
    #             core_usage = f'Core_{i}_Usage'
    #             graphed = df[['index',core_usage]]

    #             per_core_fig = go.Figure()
    #             per_core_fig.add_trace(go.Scatter(x=graphed['index'], y=graphed[core_usage], mode='lines'))
    #             per_core_fig.update_layout(
    #                 title=f'Core {i} Usage',
    #                 xaxis_type='category',  # Treat 'index' as categorical data
    #                 yaxis_range=[0, min(100, max(top_10['Overall_CPU_Usage']) + 10)],  # Set the y-axis range to 0-100
    #                 xaxis_visible=False  # Hide the x-axis labels
    #             )

    #             st.plotly_chart(per_core_fig, use_container_width=True)

    # with cd:
    #     for i in range(1,num_cores+1):
    #         if i%4==0:
    #             core_usage = f'Core_{i}_Usage'
    #             graphed = df[['index',core_usage]]

    #             per_core_fig = go.Figure()
    #             per_core_fig.add_trace(go.Scatter(x=graphed['index'], y=graphed[core_usage], mode='lines'))
    #             per_core_fig.update_layout(
    #                 title=f'Core {i} Usage',
    #                 xaxis_type='category',  # Treat 'index' as categorical data
    #                 yaxis_range=[0, min(100, max(top_10['Overall_CPU_Usage']) + 10)],  # Set the y-axis range to 0-100
    #                 xaxis_visible=False  # Hide the x-axis labels
    #             )

    #             st.plotly_chart(per_core_fig, use_container_width=True)
    

    if len(df) > 0:
        with c11:
            st.metric(
                'Soft Interrupts',
                list(df['Soft_Interrupts'])[-1]
                
            )
        with c12:
            st.metric(
                'Syscalls',
                list(df['Syscalls'])[-1]
            )
        with c13:
            st.metric(
                'Interrupts',
                list(df['Interrupts'])[-1]
            )
        with c14:
            st.metric(
                'Context Switches',
                list(df['Context_Switches'])[-1]
            )


    
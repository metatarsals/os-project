import pandas as pd
from network_disk_battery_module import BatteryMonitor, NetworkMonitor
from memory_module import Memory_Module
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

package_data_manager = BatteryMonitor().battery_generator
package_net_data_manager = NetworkMonitor().network_generator
package_cpu_data_manager = CPUMonitor().monitor_cpu
package_mem_data_manager = Memory_Module().generator

st.write("# Welcome back")
time_placeholder = st.empty()
col1,col2=st.columns([6,3])
col1.markdown("text")
col2.markdown("smth about battery health")
c1 = col1.empty()
c2 = col2.empty()
k=0

while True:
    with time_placeholder:
        st.write("Last Update: `" + str(time.time()) + "`")

    df = next(package_data_manager())
    df1 = next(package_net_data_manager())
    df2 = next(package_cpu_data_manager())
    df3, df4 = next(package_mem_data_manager())

    with c1:
        nc=5

        tab_data = {
        "CPU": [
            {"label": "CPU usage (%)", "value": float(df2['Overall_CPU_Usage'][0])},
            {"label": "User Time (h)", "value": round(float(df2['User Time'][0])/(60*60),2)},
            {"label": "System Time (h)", "value": round(float(df2['System Time'][0])/(60*60),2)},
            {"label": "Physical Cores", "value": df2['Physical Cores'][0]},
            {"label": "Logical Cores", "value": df2['Logical Cores'][0]},
        ],
        "Network": [
            {
                "label": f"{col} (GB)" if col in ['bytes_sent', 'bytes_recv'] else col,
                "value": round(df1[col].iloc[0] / 1_000_000_000, 2) if col in ['bytes_sent', 'bytes_recv'] else df1[col].iloc[0]
            }
            for col in df1.columns
        ],
        "Memory":[
            {"label": "Total (GB)", "value": (df3['total'][0])},
            {"label": "Available (GB)", "value": (df3['available'][0])},
            {"label": "Cached (GB)", "value": (df3['cached'][0])},
            {"label": "Active (GB)", "value": (df3['active'][0])},
            {"label": "Swap (GB)", "value": (df4['total'][0])},
        ]
        }

        tabs = st.tabs(tab_data.keys())

        # Populate each tab with metrics from the tab_data dictionary
        for tab, (tab_name, metrics) in zip(tabs, tab_data.items()):
            with tab:
                cols = st.columns(nc)  # Create a grid with the desired number of columns
                for i, metric in enumerate(metrics):
                    col = cols[i % nc]  # Distribute metrics across columns
                    with col:
                        st.metric(label=metric["label"].replace("_", " "), value=metric["value"])

    with c2:
        # Get the battery percentage
        battery_percent = df['percent'].iloc[0]
        power_plugged = df['power_plugged'].iloc[0]  # Assuming 'power_plugged' is in the DataFrame

        # Create the title text
        title_text = f"{battery_percent}% charge left"
        if power_plugged:
            title_text += "  (🔌 Plugged in)"
        else:
            title_text += "  (🔋 Not plugged in)"

        # Create the battery bar
        fig = go.Figure()

        # Add the outer rectangle for the battery outline
        fig.add_shape(
            type="rect",
            x0=0, y0=0, x1=1, y1=1,
            line=dict(width=0),
            fillcolor="gray"
        )

        # Add the inner rectangle representing the battery charge
        fig.add_shape(
            type="rect",
            x0=0, y0=0, x1=battery_percent / 100, y1=1,
            line=dict(width=0),  # No border for the fill
            fillcolor="green" if battery_percent > 20 else "red"  # Green for safe, red for low charge
        )

        # Add text annotation for the percentage
        fig.add_trace(go.Scatter(
            x=[0.5], y=[0.5],  # Centered in the battery
            text=[f"{battery_percent}%"],
            mode="text",
            textfont=dict(size=20, color="black")
        ))

        # Update layout to remove axes and add padding
        fig.update_layout(
            title={
                'text': title_text,
                'y':0.95,
                'x':0,
                'xanchor': 'left',
                'yanchor': 'top'},
            height=65,
            margin=dict(l=0, r=20, t=40, b=20),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )

        # Display the figure in Streamlit
        st.plotly_chart(fig, use_container_width=True, key=f"key1{k}")
        k += 1

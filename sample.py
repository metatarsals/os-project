import pandas as pd
from application_module import App_Analytics_Module
from collections import deque
import threading
import time
import plotly.express as px
import streamlit as st

st.set_page_config(
    layout='wide'
)
class DataManager:
    def __init__(self, data_generator):
        self.data_generator = data_generator
        self.data_queue = deque(maxlen=1)
        self.lock = threading.Lock()
        self.running = True
        self.collection_thread = threading.Thread(target=self._collect_data)
        self.collection_thread.daemon = True
        self.collection_thread.start()
    
    def _collect_data(self):
        generator = self.data_generator()
        while self.running:
            try:
                data = next(generator)
                with self.lock:
                    self.data_queue.append(data)
                time.sleep(1)
            except Exception as e:
                print(f"Error collecting data: {e}, {generator}")
                time.sleep(1)
    
    def get_current_data(self):
        with self.lock:
            return self.data_queue[-1] if self.data_queue else pd.DataFrame()
    
    def stop(self):
        self.running = False
        self.collection_thread.join()

package_data_manager = DataManager(App_Analytics_Module().generator)

x = st.empty()
y = st.empty()
while True:
    df = package_data_manager.get_current_data()
    with x:
        if len(df) > 0:
            st.write(max(
                df['cpu_usage(%)']
            ))
        else:
            st.write(time.time())
    with y:
        st.dataframe(df)

    time.sleep(0.01)

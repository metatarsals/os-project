import psutil
import csv
import os
from time import sleep
import subprocess
import shutil
import pandas as pd
from typing import Generator, Dict, Any

refresh_rate = 1  # seconds
csv_max_size = 10000000  # Bytes

class Memory_Module:
    def __init__(self):
        self.res = []
        self.res1=[]
        self.attrs = [
            'total',
            'available',
            'used',
            'free',
            'active',
            'inactive',
            'buffers',
            'cached',
            'shared',
            'slab'
        ]

    def generator(self, interval: float = 1.0) -> Generator[pd.DataFrame, None, None]:
        """
        Generator function that yields process metrics as a DataFrame
        
        Args:
            interval (float): Time between measurements in seconds
            
        Yields:
            pd.DataFrame: DataFrame containing all process metrics
        """
        while True:
            self.get_memory_analytics()
            df = pd.DataFrame(self.res)
            df = df.reindex(columns=self.attrs)

            self.get_swap_memory_details()
            df_swap = pd.DataFrame(self.res1)
            df_swap = df_swap.reindex(columns=['total','used','free'])

            yield (df, df_swap)
            sleep(interval)

    # def get_memory_analytics(self):
    #     memory_stats = psutil.virtual_memory()

    #     # Prepare data for CSV
    #     data = {
    #         'total_memory(B)': memory_stats.total,
    #         'available_memory(B)': memory_stats.available,
    #         'used_memory(B)': memory_stats.used,
    #         'free_memory(B)': memory_stats.free,
    #         'percent_used(%)': memory_stats.percent,
    #         'active_memory(B)': memory_stats.active,  # Active memory
    #         'inactive_memory(B)': memory_stats.inactive,  # Inactive memory
    #         'buffers(B)': memory_stats.buffers,  # Buffers
    #         'cached(B)': memory_stats.cached,  # Cached
    #         'shared_memory(B)': memory_stats.shared,  # Shared memory
    #         'slab(B)': memory_stats.slab  # Slab
    #     }

    #     # Write data to CSV
    #     file_name = 'memory_analytics.csv'

    #     # Cheking if file exists or if the file is empty
    #     file_exists = os.path.isfile(file_name)
    #     file_is_empty = os.stat(file_name).st_size == 0 if file_exists else True

    #     # Delete file if to big in size
    #     if (file_exists and os.stat(file_name).st_size >= csv_max_size):
    #         os.remove(file_name)

    #     with open(file_name, mode='a', newline='') as file:
    #         writer = csv.DictWriter(file, fieldnames=data.keys())
            
    #         # Write header if file is new
    #         if file_is_empty:
    #             writer.writeheader()
            
    #         # Write the memory stats
    #         writer.writerow(data)

    def get_memory_analytics(self):
        """Collect current memory information"""
        data = []
        
        try:
            memory_stats = psutil.virtual_memory()
            memory_info = {}
            
            # Get all available memory attributes
            for attr in self.attrs:
                try:
                    value = getattr(memory_stats, attr)
                # Convert to GB if the value is in bytes (skip percent which is already a percentage)
                    value = value / (1024 ** 3)  # Convert bytes to GB
                    memory_info[attr] = round(value, 2)  # Round to 2 decimal places
                except AttributeError:
                    memory_info[attr] = None
            
            data.append(memory_info)
            
        except Exception as e:
            print(f"Error collecting memory info: {e}")
            
        self.res = data
        return data
    
    def get_swap_memory_details(self):
        dataswap = []
        
        try:
            swap_stats = psutil.swap_memory()
            swap_info = {}
            for attr in ['total','used','free']:
                try:
                    value = getattr(swap_stats, attr)
                # Convert to GB if the value is in bytes (skip percent which is already a percentage)
                    value = value / (1024 ** 3)  # Convert bytes to GB
                    swap_info[attr] = round(value, 2)  # Round to 2 decimal places
                except AttributeError:
                    swap_info[attr] = None
            dataswap.append(swap_info)
        except Exception as e:
            print(f"Error collecting memory info: {e}")
            
        self.res1 = dataswap
        return dataswap

    # def get_swap_memory_details(self):
    #     # Get swap memory stats
    #     swap_stats = psutil.swap_memory()

    #     # Prepare data for CSV
    #     data = {
    #         'total_swap(B)': swap_stats.total,
    #         'used_swap(B)': swap_stats.used,
    #         'free_swap(B)': swap_stats.free,
    #         'percent_used(%)': swap_stats.percent,
    #         'swap_in(B)': swap_stats.sin,  # Cumulative swap in
    #         'swap_out(B)': swap_stats.sout  # Cumulative swap out
    #     }

    #     # Write data to CSV
    #     file_name = 'swap_memory_analytics.csv'

    #     # Cheking if file exists or if the file is empty
    #     file_exists = os.path.isfile(file_name)
    #     file_is_empty = os.stat(file_name).st_size == 0 if file_exists else True

    #     # Delete file if to big in size
    #     if (file_exists and os.stat(file_name).st_size >= csv_max_size):
    #         os.remove(file_name)

    #     with open(file_name, mode='a', newline='') as file:
    #         writer = csv.DictWriter(file, fieldnames=data.keys())

    #         # Write header if file is new
    #         if not file_exists or file_is_empty:
    #             writer.writeheader()

    #         # Write the swap memory stats
    #         writer.writerow(data)


if __name__ == '__main__':
    Memory_Module()

import psutil
import pandas as pd
from time import sleep
from typing import Generator, Dict, Any

refresh_rate = 1  # seconds
csv_max_size = 10000000  # Bytes

class Memory_Module:
    def __init__(self):
        self.res = []
        self.res1 = []
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
        Generator function that yields memory and swap metrics as DataFrames
        
        Args:
            interval (float): Time between measurements in seconds
            
        Yields:
            pd.DataFrame: DataFrame containing all memory and swap metrics
        """
        while True:
            # Collect memory data
            self.get_memory_analytics()
            df = pd.DataFrame(self.res)
            df = df.reindex(columns=self.attrs)

            # Collect swap memory data
            self.get_swap_memory_details()
            df_swap = pd.DataFrame(self.res1)
            df_swap = df_swap.reindex(columns=['total', 'used', 'free'])

            # Yield the memory and swap DataFrames
            yield (df, df_swap)
            sleep(interval)

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
                    # Convert to GB if the value is in bytes
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
        """Collect current swap memory information"""
        dataswap = []
        
        try:
            swap_stats = psutil.swap_memory()
            swap_info = {}
            for attr in ['total', 'used', 'free']:
                try:
                    value = getattr(swap_stats, attr)
                    # Convert to GB if the value is in bytes
                    value = value / (1024 ** 3)  # Convert bytes to GB
                    swap_info[attr] = round(value, 2)  # Round to 2 decimal places
                except AttributeError:
                    swap_info[attr] = None
            dataswap.append(swap_info)
        except Exception as e:
            print(f"Error collecting swap memory info: {e}")
            
        self.res1 = dataswap
        return dataswap


if __name__ == '__main__':
    memory_module = Memory_Module()
    memory_generator = memory_module.generator(interval=refresh_rate)
    
    try:
        # Example: Collect 5 measurements
        for _ in range(5):
            df_memory, df_swap = next(memory_generator)
            print("\nNew memory metrics:")
            print(df_memory.head())
            print("\nNew swap memory metrics:")
            print(df_swap.head())
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")

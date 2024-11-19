from time import sleep
import psutil
import pandas as pd
from datetime import datetime
from typing import Generator


# Class for Network Monitoring
class NetworkMonitor:
    def __init__(self):
        self.attrs1 = [
            "bytes_sent", 
            "bytes_recv", 
            "packets_sent", 
            "packets_recv"
        ]
        self.res1 = []

        # self.attrs2 = [
        #     "NIC",
        #     "isup", 
        #     #"duplex", 
        #     "speed", 
        #     "mtu", 
        # ]
        # self.res2 = []


    def get_network_info(self):
        data = []
        """
        Collect network I/O statistics and store them in res1.
        """
        try:
            network_stats = psutil.net_io_counters()
            network_info = {}

            for attr in self.attrs1:
                try:
                    value = getattr(network_stats, attr)
                    network_info[attr] = value
                except AttributeError:
                    network_info[attr]=None
            data.append(network_info)

        except Exception as e:
            print(f"Error collecting network I/O info: {e}")
        
        self.res1 = data
        return data

    # def get_NIC_info(self):
    #     """
    #     Collect NIC statistics and store them in res2.
    #     """
    #     try:
    #         NIC_stats = {iface: stats._asdict() for iface, stats in psutil.net_if_stats().items()}
    #         for attr in self.attrs2:
    #             self.res2[attr] = []

    #         for key, stats in NIC_stats.items():
    #             self.res2["NIC"].append(key)
    #             for attr in self.attrs2[1:]:
    #                 value = stats.get(attr, None)
    #                 self.res2[attr].append(value)
    #     except Exception as e:
    #         print(f"Error collecting NIC info: {e}")

    def network_generator(self, interval: float = 1.0) -> Generator[pd.DataFrame, None, None]:
        """
        Generate DataFrames of network I/O and NIC stats at specified intervals.
        """
        while True:
            # network I/O data
            self.get_network_info()
            df = pd.DataFrame(self.res1)
            df = df.reindex(columns=self.attrs1)

            # # NIC stats
            # self.get_NIC_info()
            # df2 = pd.DataFrame(self.res2)
            # df2 = df2.reindex(columns=self.attrs2)

            yield df
            sleep(interval)

# Class for Disk Monitoring
class DiskMonitor:
    def __init__(self):
        self.attrs = ['device', 'mountpoint', 'fstype', 'opts']
        self.res = {attr: [] for attr in self.attrs}  
        self.attrs1 = ['read_count','write_count','read_bytes','write_bytes']
        self.res1 = []
    
    def get_disk_info(self):
        """
        Collect disk partition information in a column-based format.
        Each attribute (device, mountpoint, etc.) is a key with a list of values.
        """
        try:
            # Reset data structure for new readings
            new_data = {attr: [] for attr in self.attrs}
            
            partitions = psutil.disk_partitions()
            for partition in partitions:
                # For each partition, append its values to the corresponding attribute lists
                for attr in self.attrs:
                    try:
                        value = getattr(partition, attr)
                        new_data[attr].append(value)
                    except AttributeError:
                        new_data[attr].append(None)
                        
            self.res = new_data
            return new_data
                
        except Exception as e:
            print(f"Error collecting disk info: {e}")
            return self.res
        
    def get_disk_analytics(self):
        """Collect current memory information"""
        datadisk = []
        
        try:
            disk_stats = psutil.disk_io_counters()
            disk_info = {}
            
            # Get all available memory attributes
            for attr in self.attrs1:
                try:
                    value = getattr(disk_stats, attr)
                    if attr in ('read_bytes', 'write_bytes'):
                        value = round(value / (1024 ** 2), 2)
                    disk_info[attr] = value  # Round to 2 decimal places
                except AttributeError:
                    disk_info[attr] = None
            
            datadisk.append(disk_info)
            
        except Exception as e:
            
            print(f"Error collecting read write info: {e}")
            
        self.res1 = datadisk
        return datadisk
    
    def disk_generator(self, interval: float = 1.0) -> Generator[pd.DataFrame, None, None]:
        """
        Generate DataFrames of disk information at specified intervals.
        Each row represents a partition, columns are the attributes.
        """
        while True:
            self.get_disk_info()
            df = pd.DataFrame(self.res)
            df = df.reindex(columns=self.attrs)
            
            self.get_disk_analytics()
            df1 = pd.DataFrame(self.res1)
            df1 = df1.reindex(columns=self.attrs1)
            
            # Yield the DataFrame
            yield (df,df1)
            sleep(interval)

# Class for Battery Monitoring
class BatteryMonitor:
    def __init__(self):
        self.attrs = [
            "percent", 
            "power_plugged", 
            "secsleft"
        ]
        self.res = []

    def get_battery_info(self):
        data=[]
        
        try:
            battery_stats = psutil.sensors_battery()
            battery_info = {}

            for attr in self.attrs:
                try:
                    value = getattr(battery_stats, attr)
                    if attr == 'secsleft':
                        value = value // 60
                    battery_info[attr] = value
                except AttributeError:
                    battery_info[attr] = None

            data.append(battery_info)

        except Exception as e:
            print(f"Error collecting battery info: {e}")
        
        self.res = data
        return data

    def battery_generator(self, interval: float = 1.0) -> Generator[pd.DataFrame, None, None]:
        """
        Generate DataFrames of battery information at specified intervals.
        """
        while True:
            self.get_battery_info()
            df = pd.DataFrame(self.res)
            df = df.reindex(columns=self.attrs)

            yield df
            sleep(interval)

# Main process to gather and yield data
def main():
    # Yielding network data
    network_monitor = NetworkMonitor()
    network_info_generator = network_monitor.get_network_info()
    for df in network_info_generator:
        print("Network Info DataFrame:")
        print(df)
        print("\n")

    # Yielding disk data
    disk_monitor = DiskMonitor()
    disk_info_generator = disk_monitor.get_disk_info()
    for df in disk_info_generator:
        print("Disk Info DataFrame:")
        print(df)
        print("\n")

    # Yielding battery data
    battery_monitor = BatteryMonitor()
    battery_info_generator = battery_monitor.get_battery_info()
    for df in battery_info_generator:
        print("Battery Info DataFrame:")
        print(df)
        print("\n")


if __name__ == "__main__":
    main()

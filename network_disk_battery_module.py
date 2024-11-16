from time import sleep
import psutil
import pandas as pd
from datetime import datetime
from typing import Generator


# Class for Network Monitoring
class NetworkMonitor:
    def __init__(self):
        self.attrs_network_io = [
            "Bytes Sent", 
            "Bytes Received", 
            "Packets Sent", 
            "Packets Received"
        ]
        self.attrs_interfaces = [
            "Interface", 
            "Status", 
            "Speed (Mbps)", 
            "MTU", 
            "Family", 
            "Address", 
            "Broadcast", 
            "Netmask"
        ]

    @staticmethod
    def get_network_info() -> Generator[pd.DataFrame, None, None]:
        network_info = {
            "Network I/O": {
                "Bytes Sent": psutil.net_io_counters().bytes_sent,
                "Bytes Received": psutil.net_io_counters().bytes_recv,
                "Packets Sent": psutil.net_io_counters().packets_sent,
                "Packets Received": psutil.net_io_counters().packets_recv
            },
            "Interfaces": {}
        }

        interfaces = psutil.net_if_stats()
        addresses = psutil.net_if_addrs()

        # Collect general network I/O info in a DataFrame
        io_data = {
            "Bytes Sent": [network_info["Network I/O"]["Bytes Sent"]],
            "Bytes Received": [network_info["Network I/O"]["Bytes Received"]],
            "Packets Sent": [network_info["Network I/O"]["Packets Sent"]],
            "Packets Received": [network_info["Network I/O"]["Packets Received"]],
        }
        df_io = pd.DataFrame(io_data)
        df_io = df_io.reindex(columns=df_io.columns)  # Reindex to match attributes
        yield df_io

        # Collect interface information and convert to DataFrame
        interfaces_data = []
        for interface, stats in interfaces.items():
            interface_info = {
                "Interface": interface,
                "Status": "UP" if stats.isup else "DOWN",
                "Speed (Mbps)": stats.speed,
                "MTU": stats.mtu
            }
            if interface in addresses:
                for addr in addresses[interface]:
                    address_info = {
                        "Interface": interface,
                        "Family": str(addr.family),
                        "Address": addr.address,
                        "Broadcast": addr.broadcast if addr.broadcast else None,
                        "Netmask": addr.netmask if addr.netmask else None
                    }
                    interfaces_data.append(address_info)

        df_interfaces = pd.DataFrame(interfaces_data)
        df_interfaces = df_interfaces.reindex(columns=["Interface", "Status", "Speed (Mbps)", "MTU", "Family", "Address", "Broadcast", "Netmask"])
        yield df_interfaces


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
        self.attrs_battery = [
            "Percentage", 
            "Plugged In", 
            "Time Left (minutes)"
        ]

    @staticmethod
    def get_battery_info() -> Generator[pd.DataFrame, None, None]:
        battery = psutil.sensors_battery()
        battery_info = {
            "Percentage": battery.percent,
            "Plugged In": battery.power_plugged,
            "Time Left (minutes)": battery.secsleft // 60 if battery.secsleft != psutil.POWER_TIME_UNLIMITED else "Charging"
        }

        df_battery = pd.DataFrame([battery_info])
        df_battery = df_battery.reindex(columns=["Percentage", "Plugged In", "Time Left (minutes)"])
        yield df_battery


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

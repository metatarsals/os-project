import psutil
import pandas as pd
from datetime import datetime
from typing import Generator


# Class for Network Monitoring
class NetworkMonitor:
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
        yield df_interfaces


# Class for Disk Monitoring
class DiskMonitor:
    @staticmethod
    def get_disk_info() -> Generator[pd.DataFrame, None, None]:
        disk_info = {
            "Disk Usage": [],
            "Disk I/O": []
        }

        # Collect disk usage information and convert to DataFrame
        partitions = psutil.disk_partitions()
        disk_usage_data = []
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_usage_data.append({
                    "Partition": partition.device,
                    "Mountpoint": partition.mountpoint,
                    "File System Type": partition.fstype,
                    "Total Space (GB)": usage.total / (1024 ** 3),
                    "Used Space (GB)": usage.used / (1024 ** 3),
                    "Free Space (GB)": usage.free / (1024 ** 3),
                    "Percentage Used (%)": usage.percent
                })
            except PermissionError:
                continue

        df_disk_usage = pd.DataFrame(disk_usage_data)
        yield df_disk_usage

        # Collect disk I/O information and convert to DataFrame
        io_counters = psutil.disk_io_counters(perdisk=True)
        disk_io_data = []
        for disk, io in io_counters.items():
            disk_io_data.append({
                "Disk": disk,
                "Read Count": io.read_count,
                "Write Count": io.write_count,
                "Bytes Read": io.read_bytes,
                "Bytes Written": io.write_bytes,
                "Read Time (ms)": io.read_time,
                "Write Time (ms)": io.write_time
            })

        df_disk_io = pd.DataFrame(disk_io_data)
        yield df_disk_io


# Class for Battery Monitoring
class BatteryMonitor:
    @staticmethod
    def get_battery_info() -> Generator[pd.DataFrame, None, None]:
        battery = psutil.sensors_battery()
        battery_info = {
            "Percentage": battery.percent,
            "Plugged In": battery.power_plugged,
            "Time Left (minutes)": battery.secsleft // 60 if battery.secsleft != psutil.POWER_TIME_UNLIMITED else "Charging"
        }

        df_battery = pd.DataFrame([battery_info])
        yield df_battery


# Main process to gather and yield data
def main():
    # Yielding network data
    network_info_generator = NetworkMonitor.get_network_info()
    for df in network_info_generator:
        print("Network Info DataFrame:")
        print(df)
        print("\n")

    # Yielding disk data
    disk_info_generator = DiskMonitor.get_disk_info()
    for df in disk_info_generator:
        print("Disk Info DataFrame:")
        print(df)
        print("\n")

    # Yielding battery data
    battery_info_generator = BatteryMonitor.get_battery_info()
    for df in battery_info_generator:
        print("Battery Info DataFrame:")
        print(df)
        print("\n")


if __name__ == "__main__":
    main()

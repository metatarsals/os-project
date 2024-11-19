import time
import pandas as pd
from time import sleep
from typing import Generator, Dict, Any
import psutil

class CPUMonitor:
    def __init__(self):
        # Initialize core counts for later use
        self.physical_cores = psutil.cpu_count(logical=False)
        self.logical_cores = psutil.cpu_count(logical=True)
        self.res = []
    
    def get_num_cores(self) -> Dict[str,int]:
        return {
        'Physical Cores': psutil.cpu_count(logical=False),
        'Logical Cores': psutil.cpu_count(logical=True)
    }
    
    def get_cpu_times(self) -> Dict[str, float]:
        """Get system-wide CPU times"""
        cpu_stats = psutil.cpu_times(percpu=False)
        return {
            'User Time': cpu_stats.user,
            'System Time': cpu_stats.system,
            'Idle Time': cpu_stats.idle,
            'IO Wait': getattr(cpu_stats, 'iowait', None),
            'IRQ': getattr(cpu_stats, 'irq', None),
            'SoftIRQ': getattr(cpu_stats, 'softirq', None),
            'Steal': getattr(cpu_stats, 'steal', None),
            'Guest': getattr(cpu_stats, 'guest', None),
            'Guest Nice': getattr(cpu_stats, 'guest_nice', None)
        }
        # self.res += [dict_]
        # return pd.DataFrame(self.res)
    
    def get_cpu_times_per_core(self) -> Dict[str, float]:
        """Get CPU times for each core"""
        cpu_stats = psutil.cpu_times(percpu=True)
        data = {}
        for i, core_stats in enumerate(cpu_stats):
            core_prefix = f'Core_{i+1}_'
            data.update({
                f'{core_prefix}User_Time': core_stats.user,
                f'{core_prefix}System_Time': core_stats.system,
                f'{core_prefix}Idle_Time': core_stats.idle,
                f'{core_prefix}IO_Wait': getattr(core_stats, 'iowait', None),
                f'{core_prefix}IRQ': getattr(core_stats, 'irq', None),
                f'{core_prefix}SoftIRQ': getattr(core_stats, 'softirq', None),
                f'{core_prefix}Steal': getattr(core_stats, 'steal', None),
                f'{core_prefix}Guest': getattr(core_stats, 'guest', None),
                f'{core_prefix}Guest_Nice': getattr(core_stats, 'guest_nice', None)
            })
        return data
    
    def get_cpu_percent(self) -> Dict[str, float]:
        """Get CPU usage percentages"""
        overall_usage = psutil.cpu_percent(percpu=False)
        per_core_usage = psutil.cpu_percent(percpu=True)
        
        data = {'Overall_CPU_Usage': overall_usage, 'ts' :  time.time()}
        for i, usage in enumerate(per_core_usage):
            data[f'Core_{i+1}_Usage'] = usage
        return data
    
    def get_cpu_freq(self) -> Dict[str, float]:
        """Get CPU frequency information"""
        overall_freq = psutil.cpu_freq(percpu=False)
        per_core_freq = psutil.cpu_freq(percpu=True)
        
        data = {
            'CPU_Current_Freq': overall_freq.current,
            'CPU_Min_Freq': overall_freq.min,
            'CPU_Max_Freq': overall_freq.max
        }
        
        for i, freq in enumerate(per_core_freq):
            core_prefix = f'Core_{i+1}_'
            data.update({
                f'{core_prefix}Current_Freq': freq.current,
                f'{core_prefix}Min_Freq': freq.min,
                f'{core_prefix}Max_Freq': freq.max
            })
        return data
    
    def get_cpu_stats(self) -> Dict[str, int]:
        """Get CPU statistics"""
        stats = psutil.cpu_stats()
        return {
            'Context_Switches': stats.ctx_switches,
            'Interrupts': stats.interrupts,
            'Soft_Interrupts': stats.soft_interrupts,
            'Syscalls': stats.syscalls
        }
    
    def monitor_cpu(self, interval: float = 1.0) -> Generator[pd.DataFrame, None, None]:
        """
        Generator function that yields CPU metrics as a DataFrame
        
        Args:
            interval (float): Time between measurements in seconds
            
        Yields:
            pd.DataFrame: DataFrame containing all CPU metrics
        """
        while True:
            data = {}
            # Collect all metrics
            data.update({
                'index' : pd.Timestamp.now()
            })
            data.update(self.get_num_cores())
            data.update(self.get_cpu_times())
            data.update(self.get_cpu_times_per_core())
            data.update(self.get_cpu_percent())
            data.update(self.get_cpu_freq())
            data.update(self.get_cpu_stats())
            
            # Add timestamp
            self.res += [data]
            df = pd.DataFrame(self.res)
            yield df
            
            sleep(interval)

def main():
    """Example usage of the CPUMonitor class"""
    monitor = CPUMonitor()
    cpu_generator = monitor.monitor_cpu(interval=1.0)
    
    try:
        # Example: Collect 5 measurements
        for _ in range(5):
            df = next(cpu_generator)
            print("\nNew CPU measurements:")
            print(df.head())
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")

if __name__ == "__main__":
    main()
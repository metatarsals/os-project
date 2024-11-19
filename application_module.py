import subprocess
import psutil
import pandas as pd
import os
import shutil
from time import sleep

refresh_rate = 1  # seconds

class App_Analytics_Module:
    def __init__(self):
        # self._sort = sort_by
        # self.d = dir
        pass

    def generator(self):
        installed_apps = self.get_installed_apps()

        while True:
            self.get_running_apps_info(installed_apps)
            yield(pd.DataFrame.from_dict(installed_apps))
            # sleep(refresh_rate)

    def get_installed_apps(self):
        """Retrieve installed applications on a Linux system."""

        try:
            # dpkg works only for Debian/Ubuntu systems
            command = "dpkg-query -W --showformat='${Package},${Version},${Architecture},${Installed-Size}\n'"
            result = subprocess.run(command, capture_output=True, text=True, shell=True, check=True)
            installed_apps = result.stdout.strip().split('\n')
            
            # Obtain the installed apps into a list of dictionaries
            apps = []
            for app in installed_apps:
                name, version, architecture, installed_size = app.strip("'").split(',')
                apps.append({
                    'name': name,
                    'version': version,
                    'architecture': architecture,
                    'installed_size(B)': int(installed_size) * 1024,  # Convert from kilobytes to bytes
                    'cpu_usage(%)': 0.0,
                    'memory_usage(B)': 0.0,
                    'memory_percentage(%)': 0.0  # Initialize memory percentage
                })
            return apps
        
        except subprocess.CalledProcessError as e:
            print(f"Error retrieving installed applications: {e}")
            return []

    def get_running_apps_info(self, installed_apps):
        """Retrieve running applications and their resource usage."""
        total_memory = psutil.virtual_memory().total  # Get total system memory

        for app in installed_apps:

            # Search for the app in the running processes
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                try:
                    # Check if the installed app name is in the process name
                    if app['name'] in proc.info['name']:
                        app['cpu_usage(%)'] += proc.info['cpu_percent']
                        app['memory_usage(B)'] += proc.info['memory_info'].rss  # in bytes
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Calculate memory percentage used by the application
            if total_memory > 0:
                app['memory_percentage(%)'] = (app['memory_usage(B)'] / total_memory) * 100  # Convert to percentage


class App_Interaction_Module:
    def __init__(self, app, command = 'none'):
        if command == 'none':
            pass
        
        elif command == 'uninstall':
            self.uninstall(app)

        elif command == 'delete_cached_info':
            # Implement delete cache function
            self.delete_cached_info(app)
            pass

    def uninstall(self, app_name):
        """Uninstall the specified application using apt-get on Debian/Ubuntu systems."""
        try:
            # Command to uninstall the application
            command = f"sudo apt-get remove --purge -y {app_name}"

            # Execute the command
            result = subprocess.run(command, capture_output=True, text=True, shell=True, check=True)

        except subprocess.CalledProcessError as e:
            print(f"Error uninstalling '{app_name}': {e.stderr}")


    def delete_cached_info(self, app_name):
        """Delete cached information for the specified application."""
        try:
            cache_paths = []
            
            # Check common cache directories
            common_cache_dirs = [f"/var/cache/{app_name}", f"/home/$USER/.cache/{app_name}"]
            for cache_dir in common_cache_dirs:
                if os.path.exists(cache_dir):
                    cache_paths.append(cache_dir)
            
            # Use psutil to find temporary files or folders linked to running processes
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if app_name in proc.info['name']:
                        # Locate additional temporary files associated with the app process
                        proc_cache_dir = f"/tmp/{proc.info['name']}_{proc.info['pid']}"
                        if os.path.exists(proc_cache_dir):
                            cache_paths.append(proc_cache_dir)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Delete located cache files and directories
            for path in cache_paths:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                elif os.path.isfile(path):
                    os.remove(path)
        
        except Exception as e:
            print(f"Error deleting cache for '{app_name}': {e}")
    

if __name__ == '__main__':
    App_Analytics_Module('cpu_usage','desc')
    # App_Interactive_Module('google_chrome', 'delete_cached_info')
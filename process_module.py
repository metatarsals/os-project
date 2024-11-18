from datetime import datetime
import psutil
import subprocess
from time import sleep
import csv
import os
import stat
import time
import pandas as pd
from typing import Generator, Dict, Any

refresh_rate = 1  # seconds
csv_max_size = 100000000  # Bytes

class Process_Analytics_Module:
    def __init__(self):
        self.res = []
        self.attrs = [
            'pid', 'name', 'exe', 'status', 'memory_percent', 'cpu_num', 'cpu_percent',
            'num_ctx_switches', 'num_fds', 'threads', 
            'num_threads', 'io_counters'
        ]

    def get_process_info(self):
        """Collect current process information"""
        data = []
        
        for proc in psutil.process_iter(attrs=self.attrs):
            try:
                # Get process info as a dictionary
                proc_info = proc.info
                data.append(proc_info)

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        self.res = data
        return data

    def generator(self, interval: float = 1.0) -> Generator[pd.DataFrame, None, None]:
        """
        Generator function that yields process metrics as a DataFrame
        
        Args:
            interval (float): Time between measurements in seconds
            
        Yields:
            pd.DataFrame: DataFrame containing all process metrics
        """
        while True:
            self.get_process_info()
            df = pd.DataFrame(self.res)
            df = df.reindex(columns=self.attrs)

            yield df
            sleep(interval)

class Process_Interactive_Module:
    """Creates, assigns work to, and kills processes.
    
    run_process() -> Runs the created process.
    wait_for_process() -> Waits until the complete execution of the running process before control moves further.
    kill_process() -> Kills the process immediately.
    """
    
    worker_script_path = os.path.join(os.path.dirname(__file__), 'worker.py')
    worker_executable_path = ''
    extension = '.py'

    SCHEDULED_BACKUP_SCRIPT = r"""
#!/bin/bash

# Configuration
SOURCE_DIR="/path/to/source"       # Directory to back up
BACKUP_DIR="/path/to/backup"       # Directory to save backups
INTERVAL="daily"                   # Interval options: "daily", "weekly", or "monthly"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"

# Create the backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Function to create a backup
create_backup() {
    echo "Starting backup of $SOURCE_DIR to $BACKUP_FILE..."
    tar -czf "$BACKUP_FILE" -C "$SOURCE_DIR" .
    echo "Backup complete: $BACKUP_FILE"
}

# Schedule the backup
case "$INTERVAL" in
    daily)
        echo "Scheduling daily backups..."
        echo "0 2 * * * $(whoami) $0" | crontab -   # Every day at 2:00 AM
        ;;
    weekly)
        echo "Scheduling weekly backups..."
        echo "0 2 * * 0 $(whoami) $0" | crontab -   # Every Sunday at 2:00 AM
        ;;
    monthly)
        echo "Scheduling monthly backups..."
        echo "0 2 1 * * $(whoami) $0" | crontab -   # First day of each month at 2:00 AM
        ;;
    *)
        echo "Invalid interval specified. Choose 'daily', 'weekly', or 'monthly'."
        exit 1
        ;;
esac

create_backup
"""

    def __init__(self, task_string, ext, preemtable=False):
        try:
            self.preemptable = preemtable
            self.task_string = task_string
            
            if ext == '.c':
                self.worker_script_path = os.path.join(os.path.dirname(__file__), 'worker.c')
                self.worker_executable_path = os.path.join(os.path.dirname(__file__), 'worker')
                self.__create_worker()  # Create the worker script
                self.__compile_worker()  # Compile the C work script
                self.extension = '.c'
            
            elif ext == '.sh':
                self.worker_script_path = os.path.join(os.path.dirname(__file__), 'worker.sh')
                self.__create_worker()  # Create the worker Bash script
                self.extension = '.sh'

        except Exception as e:
            print(f"An error occurred: {e}")

    ### PRIVATE METHODS
    def __create_worker(self):
        # Write the work script to a temporary file
        with open(self.worker_script_path, 'w') as file:
            file.write(self.task_string)
        
        # Give permission to execute the created script file
        os.chmod(self.worker_script_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                 stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    def __compile_worker(self):
        # Compile the C code into an executable
        compile_command = ['gcc', self.worker_script_path, '-o', self.worker_executable_path]
        subprocess.run(compile_command, check=True)  # Raises an error if the compilation fails

    def __create_process(self):
        if self.extension == '.py':
            # Create task to give process
            self.__create_worker()
            command = ['python3', self.worker_script_path]  # Run Python script

        elif self.extension == '.c':
            command = [self.worker_executable_path]  # Run compiled C executable

        elif self.extension == '.sh':
            self.__create_worker()
            command = ['bash', self.worker_script_path]  # Run Bash script
        
        # Create a subprocess
        process = subprocess.Popen(command)
        return process

    ### PUBLIC METHODS
    def run_process(self):
        self.process = self.__create_process()  # Create the process
        print(f"PROCESS PID: {self.process.pid} EXECUTION BEGUN.")

        if not self.preemptable:
            # Wait for the process to complete
            self.process.wait()
            print(f"PROCESS PID: {self.process.pid} EXECUTION COMPLETE.")

            # Terminate the process (optional since we are waiting)
            self.kill_process()

    def wait_for_process(self):
        self.process.wait()

    def kill_process(self):
        try:
            self.process.terminate()  # Terminate the process
            self.process.wait()  # Wait for it to exit
            print(f"PROCESS PID: {self.process.pid} KILLED.")

        except Exception as e:
            print(f"Error killing the process: {e}")
        
        # Cleanup: Remove the work script file
        if os.path.exists(self.worker_script_path):
            os.remove(self.worker_script_path)

        if self.extension == '.c' and os.path.exists(self.worker_executable_path):
            # Cleanup: Remove the C executable
            os.remove(self.worker_executable_path)

class Backups_Module:
    def __init__(self, source_dir, backup_dir, interval):
        self.src = source_dir
        self.dst = backup_dir
        self.interval = interval

    ### PRIVATE METHODS
    def __create_backup_script(self):
        """Create a backup Bash script that will copy files from source to destination."""
        # Define the backup script content
        script_content = f"""#!/bin/bash

    # Configuration
    SOURCE_DIR="{self.src}"       # Directory to back up
    BACKUP_DIR="{self.dst}"       # Directory to save backups
    INTERVAL="{self.interval}"                   # Interval options: "daily", "weekly", or "monthly"
    TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
    BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"

    # Create the backup directory if it doesn't exist
    mkdir -p "$BACKUP_DIR"

    # Function to create a backup
    create_backup() {{
        echo "Starting backup of $SOURCE_DIR to $BACKUP_FILE..."
        tar -czf "$BACKUP_FILE" -C "$SOURCE_DIR" .
        echo "Backup complete: $BACKUP_FILE"
    }}

    # Schedule the backup
    case "$INTERVAL" in
        daily)
            echo "Scheduling daily backups..."
            echo "0 2 * * * $(whoami) $0" | crontab -   # Every day at 2:00 AM
            ;;
        weekly)
            echo "Scheduling weekly backups..."
            echo "0 2 * * 0 $(whoami) $0" | crontab -   # Every Sunday at 2:00 AM
            ;;
        monthly)
            echo "Scheduling monthly backups..."
            echo "0 2 1 * * $(whoami) $0" | crontab -   # First day of each month at 2:00 AM
            ;;
        *)
            echo "Invalid interval specified. Choose 'daily', 'weekly', or 'monthly'."
            exit 1
            ;;
    esac

    # Run the backup immediately
    create_backup
    """

        # Write the script to a temporary file
        script_path = "/tmp/backup_script.sh"  # Temporary location
        with open(script_path, 'w') as script_file:
            script_file.write(script_content)

        # Make the script executable
        os.chmod(script_path, 0o755)
        return script_path

    ### PUBLIC METHODS
    def run_backup(self):
        """Run the backup Bash script using psutil."""
        script_path = self.__create_backup_script()

        entry = {
            'from': self.src,  # The source directory
            'to': self.dst,    # The backup directory
        }
        
        try:
            # Run the backup script as a subprocess
            process = subprocess.Popen(['bash', script_path])
            print(f"Running backup script with PID: {process.pid}")

            # Wait for the process to complete
            process.wait()
            print(f"Backup script completed with PID: {process.pid}")
        
        except Exception as e:
            print(f"Error running the backup script: {e}")
            entry['status'] = 'failed'  # Add a failure status to the entry
            entry['when'] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")  # Timestamp when failure occurs
            return entry

        finally:
            # Clean up: remove the script after execution
            if os.path.exists(script_path):
                os.remove(script_path)

        # entry = {
        # 'from': self.src,  # Assuming self.source_dir is set during object initialization
        # 'to': self.dst,    # Assuming self.backup_dir is set during object initialization
        # 'when': datetime.now().strftime("%d-%m-%Y %H:%M:%S"),  # Get current timestamp
        # 'status': 'successful' if k else 'failed'
        # }
            entry['when'] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")  # Timestamp when the backup finishes
            entry['status'] = 'successful'  # Mark as successful once backup completes
        
        # Return the new log entry
        return entry

if __name__ == '__main__':
    process_module = Process_Analytics_Module()

    # Start the generator
    process_generator = process_module.generator(interval=2.0)

    # Iterate through the generator to collect process data
    for process_df in process_generator:
        # Print the DataFrame to the terminal
        print(process_df)
        print("\n" + "-"*50 + "\n")  # Add a separator for readability

    task_string = """#!/usr/bin/env python3
import time

def perform_work():
    for i in range(10):
        print(f"Worfing... {i + 1}")
        time.sleep(1)

if __name__ == "__main__":
    perform_work()
"""

    task_string2 = """#!/usr/bin/env python3
import math

def prime_gen(n = 1000):
    for i in range(2, n+1):
        for j in range(2, int(math.sqrt(i))+1):
            if i%j == 0:
                break
        else:
            print(i)        

if __name__ == "__main__":
    prime_gen()
"""
    task_string3 = r"""#include <stdio.h>
#include <unistd.h>

void perform_work() {
    for (int i = 0; i < 10; i++) {
        printf("Working... %d\n", i + 1);
        sleep(1);  // Sleep for 1 second
    }
}

int main() {
    perform_work();
    return 0;
}
"""
    task_string4 = """
    #!/bin/bash

# Loop from 1 to 100
for ((i=1; i<=100; i++))
do
  echo $i
done
"""
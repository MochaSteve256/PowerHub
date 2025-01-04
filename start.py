import os
import subprocess

# Kill old process
try:
    result = subprocess.check_output(
        "ps aux | grep 'python3 main' | grep -v grep | grep -v sudo",
        shell=True,
        text=True
    )
    if result.strip():
        pid = result.split()[1]  # The PID is usually the second column in `ps aux` output
        print(f"Found PID: {pid}")
        
        # Step 2: Kill the Process
        os.system(f"sudo kill {pid}")
        print(f"Process {pid} has been killed.")
    else:
        print("No matching process found.")
except subprocess.CalledProcessError as e:
    print("Failed to find or kill the process:", e)

# Pull changes
os.system("git pull")

# Start new process
os.system("nohup sudo python3 main.py")
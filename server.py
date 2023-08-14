import subprocess
import sys
import psutil
import time


def terminate():
    # Kill previous chromium instances
    for proc in psutil.process_iter():
        try:
            # Get process details as a named tuple
            pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline'])

            # Check if the process name or its command line contains 'google-chrome'
            if 'google-chrome' in pinfo['name'] or 'google-chrome' in ' '.join(pinfo.get('cmdline', [])):
                proc.terminate()
                print(f"Terminated previous Chrome instance with PID {pinfo['pid']}")

            # Similarly, check for 'server.py' in the cmdline to kill the server script
            if 'server.py' in ' '.join(pinfo.get('cmdline', [])):
                proc.terminate()
                print(f"Terminated server.py script with PID {pinfo['pid']}")

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass


if '--kill' in sys.argv:
    terminate()
else:
    try:
        chrome_command = ['google-chrome', '--remote-debugging-port=9222', 'https://chromium.org']
        if "--headless" in sys.argv:
            chrome_command.insert(1, '--headless')

        print("Starting Chrome in headless mode..." if '--headless' in chrome_command else "Starting Chrome...")
        chrome_process = subprocess.Popen(chrome_command)

        if '--daemon' in sys.argv:
            print("Running in daemon mode...")
            while True:  # Infinite loop to keep server running
                time.sleep(1)  # Sleep for a second to reduce CPU usage
        else:
            print("Press any key to exit...")
            sys.stdin.read(1)
    finally:
        print("Terminating Chrome instance...")
        chrome_process.terminate()
        print("Done.")

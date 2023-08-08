import subprocess
import os
import sys

try:
    print("Starting Chrome in headless mode...")
    chrome_process = subprocess.Popen(['google-chrome', '--remote-debugging-port=9222', 'https://chromium.org'])
    
    print("Press any key to exit...")
    sys.stdin.read(1)
finally:
    print("Terminating Chrome instance...")
    chrome_process.terminate()
    print("Done.")


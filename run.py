# run.py

import sys
import subprocess
import time
import signal

def start_process(cmd):
    return subprocess.Popen(cmd, shell=False)

def main():
    procs = []
    # 1) Start FastAPI via Uvicorn
    procs.append(start_process([sys.executable, "-m", "uvicorn", "main:app", "--reload"]))
    # Give the API a second to come up before starting Streamlit
    time.sleep(1)
    # 2) Start Streamlit frontend
    procs.append(start_process([sys.executable, "-m", "streamlit", "run", "streamlit_layout_ui.py"]))

    try:
        # Wait until both exit (they won't, until you Ctrl+C)
        for p in procs:
            p.wait()
    except KeyboardInterrupt:
        # On Ctrl+C, terminate both
        for p in procs:
            p.send_signal(signal.SIGINT)

if __name__ == "__main__":
    main()

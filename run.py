# run.py

import sys
import subprocess
import time
import signal

def start_process(cmd):
    return subprocess.Popen(cmd, shell=False)

def main():
    procs = []
    # 1) Start FastAPI via Uvicorn with extended timeout settings
    # Ensure we use the correct Python executable from the virtual environment
    python_executable = sys.executable
    print(f"Using Python: {python_executable}")
    
    uvicorn_cmd = [
        python_executable, "-m", "uvicorn", "main:app", "--reload",
        "--timeout-keep-alive", "900",  # 15 minutes keep-alive
        "--timeout-graceful-shutdown", "30",  # 30 seconds for graceful shutdown
        "--host", "127.0.0.1",  # Explicit host
        "--port", "8000"  # Explicit port
    ]
    print("🚀 Starting FastAPI with extended timeouts (15 minutes)...")
    procs.append(start_process(uvicorn_cmd))
    
    # Give the API a second to come up before starting Streamlit
    time.sleep(1)
    
    # 2) Start Streamlit frontend
    streamlit_cmd = [python_executable, "-m", "streamlit", "run", "streamlit_layout_ui.py"]
    print("🎨 Starting Streamlit frontend...")
    procs.append(start_process(streamlit_cmd))

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

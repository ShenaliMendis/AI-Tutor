#!/usr/bin/env python
# File: run.py
import subprocess
import sys
import os
import time
import threading
import signal

def run_fastapi():
    print("Starting FastAPI backend...")
    subprocess.run(["python", "main.py"])

def run_flask():  
    print("Starting Flask frontend...")
    subprocess.run(["python", "app.py"])

def main():
    # Check if virtual environment is activated
    if not os.environ.get('VIRTUAL_ENV'):
        print("Warning: Virtual environment not detected.")
        if input("Continue anyway? (y/n): ").lower() != 'y':
            sys.exit(1)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("Error: .env file not found.")
        print("Please create a .env file with GOOGLE_API_KEY and FLASK_SECRET_KEY.")
        sys.exit(1)
    
    try:
        # Start FastAPI in a separate thread
        fastapi_thread = threading.Thread(target=run_fastapi)
        fastapi_thread.daemon = True
        fastapi_thread.start()
        
        # Wait for FastAPI to start
        print("Waiting for FastAPI to start...")
        time.sleep(3)
        
        # Start Flask in the main thread
        run_flask()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {str(e)}")
    
if __name__ == "__main__":
    main()

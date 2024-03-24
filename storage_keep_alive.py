# Ini dijalankan jika tidak ingin storage server ke mode sleep

from dotenv import load_dotenv
from datetime import datetime
import requests
import time
import os

load_dotenv(override=True)

StorageURL = os.environ.get("StorageURL")# "http://localhost:5500/"
DelayAwake = 1 * 60 # 1 Menit

def call_storage():
    while True:
        try:
            response = requests.get(StorageURL)
            if response.status_code:
                print(f"# Storage responded at : {datetime.now()} | msg : {response.text}")
            print(f"Waiting {DelayAwake}s ...")
            time.sleep(DelayAwake)
        except Exception as e:
            print(e)
            print("# Error trying again in 60s ... ")
            time.sleep(DelayAwake)

if __name__ == "__main__":
    print("# Keep alive storage started ... ")
    print(f"# Time between call : {DelayAwake}s")
    call_storage()
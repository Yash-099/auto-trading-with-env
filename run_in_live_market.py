import time
from datetime import datetime
print("Script started...")


def is_within_hours():
    now = datetime.now()
    start_time = now.replace(hour=9, minute=15, second=0, microsecond=0)
    end_time = now.replace(hour=15, minute=30, second=0, microsecond=0)

    return start_time <= now <= end_time

print("Script started...")
while True:
    print("Checking time...")
    if is_within_hours():
        # Place your code here
        print("Running script...")
    else:
        print("Outside working hours. Waiting...")

    time.sleep(300)  # Check every 5 minutes

import serial
import pandas as pd
from datetime import datetime
import os

# Arduino COM port
ser = serial.Serial('COM4', 9600, timeout=1)
csv_file = 'RFID_Data.csv'

columns = ['Number', 'Name', 'Classes', 'Status', 'Time In', 'Time Out']

# Create CSV if missing or empty
if not os.path.exists(csv_file) or os.path.getsize(csv_file) == 0:
    df = pd.DataFrame(columns=columns)
    df.to_csv(csv_file, index=False)

print("Waiting for RFID scans...")

while True:
    ser.reset_input_buffer()  # clear old serial data
    rfid_line = ser.readline().decode().strip()
    if rfid_line:
        try:
            name, number, status = rfid_line.split(",")
        except ValueError:
            print(f"Bad line: {rfid_line}")
            continue

        # Only log Present students
        if status == "Present":
            time_in = datetime.now().strftime("%#I:%M%p")  # 7:00AM format (Windows), use %-I:%M%p on Linux/macOS

            # Read existing CSV to update Classes
            df = pd.read_csv(csv_file)
            if number in df['Number'].astype(str).values:
                # Student exists, increment Classes
                df.loc[df['Number'] == int(number), 'Classes'] += 1
                df.loc[df['Number'] == int(number), 'Time In'] = time_in
            else:
                # New student
                new_row = pd.DataFrame([{
                    'Number': int(number),
                    'Name': name,
                    'Classes': 1,
                    'Status': status,
                    'Time In': time_in,
                    'Time Out' : ''
                }])
                df = pd.concat([df, new_row], ignore_index=True)

            # Save updated CSV
            df.to_csv(csv_file, index=False)

        # Print to console for feedback
        print(f"{name} ({number}) -> {status}")

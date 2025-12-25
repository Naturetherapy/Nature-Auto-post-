import os
import time

file_path = 'posted_videos.txt'
seconds_in_day = 86400  # 24 hours mein itne seconds hote hain

if os.path.exists(file_path):
    # File ki last modified time nikalna
    file_age_seconds = time.time() - os.path.getmtime(file_path)
    
    # Check karna ki kya 1 din (86400 seconds) beet chuke hain
    if file_age_seconds >= seconds_in_day:
        with open(file_path, 'w') as f:
            f.write('')
        print("1 din poora ho gaya hai. History reset kar di gayi hai.")
    else:
        hours_left = round((seconds_in_day - file_age_seconds) / 3600, 1)
        print(f"Reset skip kiya gaya. Abhi 1 din poora nahi hua hai. {hours_left} ghante baaki hain.")
else:
    # Agar file nahi hai toh naye sire se bana dega
    open(file_path, 'w').close()
    print("History file created.")

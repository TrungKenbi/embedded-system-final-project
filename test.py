import requests
from datetime import datetime

response = requests.get('http://45.119.212.43/api/student/1824801030053')
json = response.json()

ROOM_NAME = 'I3-105'

currentDayOfWeek = datetime.today().weekday() + 1

for t in json['timetable']:
    if t['dayOfWeek'] == currentDayOfWeek and t['roomName'] == ROOM_NAME:
        print(t)
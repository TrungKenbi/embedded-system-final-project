import tensorflow.keras
from PIL import Image, ImageOps
import numpy as np
import cv2
from time import sleep
import serial
import io
import time

import sqlite3
from sqlite3 import Error
import requests

from datetime import datetime


ROOM_NAME = 'I3-105'

HAS_HARDWARE = True
SERIAL_PORT = 'COM8'

record_id = 0
currentUser = 0
last_time_close = 0


if HAS_HARDWARE:
    arduino = serial.Serial(port=SERIAL_PORT, baudrate=115200, timeout=.1)
camera = cv2.VideoCapture(0)
np.set_printoptions(suppress=True)
model = tensorflow.keras.models.load_model('keras_model.h5')
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)


'''

CREATE TABLE "users" (
	"id"	INTEGER,
	"code"	VARCHAR(50),
	"fullname"	VARCHAR(50),
	PRIMARY KEY("id" AUTOINCREMENT)
);


CREATE TABLE "door_logs" (
	"id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
    "room" VARCHAR(10) NOT NULL,
	"opened_at"	DATETIME DEFAULT CURRENT_TIMESTAMP,
	"closed_at"	DATETIME,
	PRIMARY KEY("id" AUTOINCREMENT)
);
'''

def current_milli_time():
    return round(time.time() * 1000)
    

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def create_door_log(conn, user_id, room):
    sql = ''' INSERT INTO door_logs(user_id, room)
              VALUES(?, ?) '''
    cur = conn.cursor()
    cur.execute(sql, (user_id, room))
    conn.commit()
    return cur.lastrowid

def check_door(conn, room):
    sql = ''' SELECT COUNT(*) FROM door_logs WHERE room = ? AND closed_at IS NULL '''
    cur = conn.cursor()
    cur.execute(sql, (room,))
    return cur.fetchone()[0]
    
def update_door(conn, id):
    sql = ''' UPDATE door_logs SET closed_at = CURRENT_TIMESTAMP WHERE id = ? '''
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()
 
def get_user_by_id(conn, id):
    sql = ''' SELECT * FROM users WHERE id = ? '''
    cur = conn.cursor()
    cur.execute(sql, (id,))
    rows = cur.fetchall()
    return rows
    
def check_TDMU(student_code):
    response = requests.get('http://45.119.212.43/api/student/' + student_code)
    json = response.json()
    currentDayOfWeek = datetime.today().weekday() + 1

    for t in json['timetable']:
        if t['dayOfWeek'] == currentDayOfWeek and t['roomName'] == ROOM_NAME:
            return True
    return False


database = r"door.db"

# create a database connection
conn = create_connection(database)
with conn:
    while True:
        retval, img = camera.read()
        
        if "CLOSE" in arduino.readline().decode():
            # arduino.write(str(0).encode())
            if not record_id == 0:
                print(record_id)
                update_door(conn, record_id)
            currentUser = 0
            record_id = 0
            last_time_close = current_milli_time()
                
        # print(current_milli_time() - last_time_close + 10000)
        if currentUser == 0 and current_milli_time() > last_time_close + 10000:
            image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            
            size = (224, 224)
            image = ImageOps.fit(image, size, Image.ANTIALIAS)
            image_array = np.asarray(image)
            normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
            data[0] = normalized_image_array
            prediction = model.predict(data)

            i = 0
            bestPredict = 0
            bestPredictIndex = 0
            for f in prediction[0]:
                if f > bestPredict:
                   bestPredict = f
                   bestPredictIndex = i
                i+=1
            
            if bestPredict > 0.90:
                print(bestPredict, bestPredictIndex)
                if check_door(conn, ROOM_NAME) == 0:
                    currentUser = bestPredictIndex + 1
                    user_data = get_user_by_id(conn, currentUser)[0][1]
                    print(user_data)
                    if check_TDMU(user_data):
                        print("Insert door log to database")
                        if HAS_HARDWARE:
                            arduino.write(str(1).encode())
                        record_id = create_door_log(conn, bestPredictIndex + 1, ROOM_NAME)
                    else:
                        print('Khong co thoi khoa bieu')
        
        sleep(0.1)
        
        cv2.imshow('Nhan Dien Khuon Mat', img)
        
        key = cv2.waitKey(1)
        
        if key == ord('q'):
            break
                
camera.release
cv2.destroyAllWindows()

import tensorflow.keras
from PIL import Image, ImageOps
import numpy as np
import cv2
from time import sleep
import serial

import sqlite3
from sqlite3 import Error


ROOM_NAME = 'I3.302'


# arduino = serial.Serial(port='COM8', baudrate=115200, timeout=.1)
camera = cv2.VideoCapture(0)

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the model
model = tensorflow.keras.models.load_model('keras_model.h5')

# Create the array of the right shape to feed into the keras model
# The 'length' or number of images you can put into the array is
# determined by the first position in the shape tuple, in this case 1.
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

def check_door(conn, user_id, room):
    sql = ''' SELECT COUNT(*) FROM door_logs WHERE user_id = ? AND room = ? AND closed_at IS NULL '''
    cur = conn.cursor()
    cur.execute(sql, (user_id, room))
    return cur.fetchone()[0]


database = r"door.db"

# create a database connection
conn = create_connection(database)
with conn:
    while True:
        retval, img = camera.read()
        image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        

        # Replace this with the path to your image
        # image = Image.open('image6.jpg')

        #resize the image to a 224x224 with the same strategy as in TM2:
        #resizing the image to be at least 224x224 and then cropping from the center
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.ANTIALIAS)

        #turn the image into a numpy array
        image_array = np.asarray(image)

        # display the resized image
        # image.show()

        # Normalize the image
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

        # Load the image into the array
        data[0] = normalized_image_array

        # run the inference
        prediction = model.predict(data)
        # print(prediction)
        
        i = 0
        bestPredict = 0
        bestPredictIndex = 0
        for f in prediction[0]:
            if f > bestPredict:
               bestPredict = f
               bestPredictIndex = i
            i+=1
        
        if bestPredict > 0.95:
            print(bestPredict, bestPredictIndex)
            if check_door(conn, bestPredictIndex + 1, ROOM_NAME) == 0:
                print("Insert door log to database")
                create_door_log(conn, bestPredictIndex + 1, ROOM_NAME)
                # arduino.write(str(bestPredictIndex).encode())
        
        sleep(0.1)
        
        cv2.imshow('Nhan Dien Khuon Mat', img)
        
        key = cv2.waitKey(1)
        
        if key == ord('q'):
            break
                
camera.release
cv2.destroyAllWindows()

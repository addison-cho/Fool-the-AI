#pip install opencv-python deepface
import cv2
from deepface import DeepFace
from deepface.modules.verification import find_cosine_distance

import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk
import numpy as np
import os


cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


root = tk.Tk()
root.title = ("Can You Fool the AI?")

camera_label = Label(root)
camera_label.grid(row=0, column=0, columnspan=2)

count = 0
MAX_IMG = 3
images = []

first_label = Label(root)
first_label.grid(row=0, column=0)
second_label = Label(root)
second_label.grid(row=0, column=1)

THRESHOLD = .5


def capture_image():
    global count, images
    
    ret, frame = cap.read()
    if ret:
        camera_label.grid(row=0, column=1, columnspan=1)

        if count < MAX_IMG:
            
            cv2.imwrite('first_image.jpg', frame)
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            first_label.imgtk = imgtk
            first_label.configure(image=imgtk)

            embedding = DeepFace.represent(img_path="first_image.jpg", model_name="ArcFace")
            images.append(embedding[0]['embedding'])

            count += 1

        else:
            cv2.imwrite('second_image.jpg', frame)
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            second_label.imgtk = imgtk
            second_label.configure(image=imgtk)

            embedding = DeepFace.represent(img_path="second_image.jpg", model_name="ArcFace")
            compare_faces(embedding[0]['embedding'])
        
        return frame
    
def compare_faces(embedding):
    avg = np.average(images, axis=0)

    distance = find_cosine_distance(avg, embedding)
    print(distance)
    
    try:
        if distance < THRESHOLD:
            result_label.configure(text=f"AI recognized you! Similarity score: {distance:.2f}")
        else:
            result_label.configure(text=f"You fooled the AI! Similarity score: {distance:.2f}")
        print("ran")
    except Exception as e:
        print("Error comparing images.")

    pic_button.grid_remove()
    continue_button.grid(row=2, column=0, columnspan=2)

    
def reset():
    global count, images
    count = 0
    images = []
    first_label.configure(image='')
    second_label.configure(image='')
    result_label.configure(text='')
    camera_label.grid(row=0, column=0, columnspan=2)
    continue_button.grid_remove()
    pic_button.grid(row=2, column=0, columnspan=2)


def live_camera():
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        camera_label.imgtk = imgtk
        camera_label.configure(image=imgtk)
    camera_label.after(10, live_camera) 


result_label = Label(root, text="", font=("Helvetica", 14))
result_label.grid(row=3, column=0, columnspan=2)

live_camera()

pic_button = Button(root, text="Cheese", command=capture_image)
pic_button.grid(row=2, column=0, columnspan=2)

continue_button=Button(root, text="Click to Continue", command=reset)

root.mainloop()

if os.path.exists("first_image.jpg"):
    os.remove("first_image.jpg") 
if os.path.exists("second_image.jpg"):
    os.remove("second_image.jpg")

cap.release()
cv2.destroyAllWindows()
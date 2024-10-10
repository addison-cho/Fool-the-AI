#pip install opencv-python deepface
import cv2
from deepface import DeepFace
from deepface.modules.verification import find_cosine_distance

import tkinter as tk
from tkinter import Label, Button, Frame, ttk, messagebox
from PIL import Image, ImageTk
import numpy as np
import os

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

LABEL_WIDTH = 640
LABEL_HEIGHT = 480

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WINDOW_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WINDOW_HEIGHT)

root = tk.Tk()
root.geometry("1350x1125")
root.title = ("Can You Fool the AI?")


root.grid_rowconfigure(0, weight=1)  
root.grid_rowconfigure(1, weight=0)
root.grid_columnconfigure(0, weight=1)


s = ttk.Style()
s.configure('topFrame.TFrame')
s.configure('bottomFrame.TFrame')

topFrame = ttk.Frame(root, style='topFrame.TFrame')
topFrame.grid(row=0, column=0)

bottomFrame = ttk.Frame(root, style='bottomFrame.TFrame')
bottomFrame.grid(row=1, column=0)


topFrame.grid_rowconfigure(0, weight=1)
topFrame.grid_rowconfigure(1, weight=1)
topFrame.grid_columnconfigure(0, weight=1)
topFrame.grid_columnconfigure(1, weight=1)

bottomFrame.grid_columnconfigure(0, weight=1)
bottomFrame.grid_rowconfigure(0, weight=1)


count = 0
MAX_IMG = 3
images = []

BORDERWIDTH = 10

camera_label = tk.Label(topFrame, bd=2, borderwidth=BORDERWIDTH, padx=LABEL_WIDTH, pady=LABEL_HEIGHT, relief="groove", bg="red")
camera_label.grid(row=0, column=0, padx=5, pady=5, sticky="")

first_label = tk.Label(topFrame, bd=2, borderwidth=BORDERWIDTH, padx=LABEL_WIDTH, pady=LABEL_HEIGHT, relief="solid", bg="red")
first_label.grid(row=0, column=0, padx=5, pady=5, sticky="")

second_label = tk.Label(topFrame, bd=2, borderwidth=BORDERWIDTH, padx=LABEL_WIDTH, pady=LABEL_HEIGHT, relief="solid", bg="orange")
second_label.grid(row=0, column=1, padx=5, pady=5, sticky="")

third_label = tk.Label(topFrame, bd=2, borderwidth=BORDERWIDTH, padx=LABEL_WIDTH, pady=LABEL_HEIGHT, relief="solid", bg="yellow")
third_label.grid(row=1, column=0, padx=5, pady=5, sticky="")

final_label = tk.Label(topFrame, bd=2, borderwidth=BORDERWIDTH, padx=LABEL_WIDTH, pady=LABEL_HEIGHT, relief="solid", bg="blue")
final_label.grid(row=1, column=1, padx=5, pady=5, sticky="")

progress_label = Label(bottomFrame, text=f"Training Image 1 of {MAX_IMG}", font=("Helvetica", 14))
progress_label.grid(row=0, column=0, columnspan=2, padx=2.5, pady=2.5)

camera_label.lift()

THRESHOLD = .5  

def flash_effect():
    camera_label.after(100, lambda: root.configure(bg="white"))  # Flash for 100 milliseconds

def capture_image():
    global count, images    
    
    ret, frame = cap.read()
    if ret:
        #flash_effect()
        try:
                
            if count < MAX_IMG:
                cv2.imwrite(f'reference_image_{count+1}.jpg', frame)

                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                imgtk = ImageTk.PhotoImage(image=img)
                
                embedding = DeepFace.represent(img_path=f'reference_image_{count+1}.jpg', model_name="ArcFace")
                images.append(embedding[0]['embedding'])
                
                if count == 0:
                    first_label.imgtk = imgtk
                    first_label.configure(image=imgtk)
                    camera_label.grid(row=0, column=1)
                elif count == 1:
                    second_label.imgtk = imgtk
                    second_label.configure(image=imgtk)
                    camera_label.grid(row=1, column=0)
                elif count == 2:
                    third_label.imgtk = imgtk
                    third_label.configure(image=imgtk)
                    camera_label.grid(row=1, column=1)

                count += 1

                if count == MAX_IMG:
                    progress_label.config(text="Try to Fool the AI!")
                else:
                    progress_label.config(text=f"Training Image {count + 1} of {MAX_IMG}")

                
            else:
                cv2.imwrite('final_image.jpg', frame)
                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                imgtk = ImageTk.PhotoImage(image=img)
                final_label.imgtk = imgtk
                final_label.configure(image=imgtk)

                embedding = DeepFace.represent(img_path="final_image.jpg", model_name="ArcFace")

                compare_faces(embedding[0]['embedding'])

                camera_label.grid_remove()

            return frame

        except:
            messagebox.showwarning("showwarning", "AI couldn't recognize a face; please try again.") 
    
    
def compare_faces(embedding):
    avg = np.average(images, axis=0)

    distance = find_cosine_distance(avg, embedding)
    print(distance)
    
    try:
        if distance < THRESHOLD:
            progress_label.configure(text=f"AI recognized you!\nSimilarity score: {distance:.2f}")
        else:
            progress_label.configure(text=f"You fooled the AI!\nSimilarity score: {distance:.2f}")
        print("ran")
    except Exception as e:
        print("Error comparing images.")

    pic_button.grid_remove()
    continue_button.grid(row=1, column=0, columnspan=2, padx=2.5, pady=2.5)


def delete_pictures():
    for i in range(1, MAX_IMG + 2):
        if os.path.exists(f"reference_image_{i}.jpg"):
            os.remove(f"reference_image_{i}.jpg")
    if os.path.exists("final_image.jpg"):
        os.remove("final_image.jpg")
        

def reset():
    global count, images
    count = 0
    images = []

    first_label.configure(image='')
    second_label.configure(image='')
    third_label.configure(image='')
    final_label.configure(image='')
    camera_label.grid(row=0, column=0, padx=5, pady=5)

    progress_label.configure(text=f"Training Image 1 of {MAX_IMG}", font=("Helvetica", 14))
    continue_button.grid_remove()
    pic_button.grid(row=1, column=0, columnspan=2, padx=2.5, pady=2.5)

    delete_pictures()


def live_camera():
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        camera_label.imgtk = imgtk
        camera_label.configure(image=imgtk)
    camera_label.after(10, live_camera) 


live_camera()

pic_button = Button(bottomFrame, text="Cheese", command=capture_image)
pic_button.grid(row=1, column=0, columnspan=2, padx=2.5, pady=2.5)
pic_button.lift()

continue_button=Button(bottomFrame, text="Click to Continue", command=reset)

root.mainloop()

delete_pictures()

cap.release()
cv2.destroyAllWindows()
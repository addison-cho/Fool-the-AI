import sys
import os
import cv2
import numpy as np

from deepface import DeepFace
from deepface.modules.verification import find_cosine_distance

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

# GUI set-up
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900

# size of camera windows ()
BOX_WIDTH = 600 # 640
BOX_HEIGHT = 338 # 360
THRESHOLD = .5


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fool the AI")
        self.setGeometry(0, 0, 1600, 900)
        self.createLayout()

        # open-cv python camera feed
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, WINDOW_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WINDOW_HEIGHT)

        # thread for live camera feed
        self.Worker1 = Worker1(self.cap)
        self.Worker1.start()
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)    

        # button setup
        self.camera_button.clicked.connect(self.capture_image)
        self.retry_button.clicked.connect(self.retry)
        self.reset_button.clicked.connect(self.reset)

        # var setup (# of images & embeddings)
        self.count = 0
        self.MAX_IMG = 3
        self.images = []

        # GUI (window, error mesasge, button styling)
        self.msg = QMessageBox()
        self.msg.setWindowTitle("Uh Oh!")
        self.msg.setText("I couldn't find a face! Please try again.")
        self.msg.setIcon(QMessageBox.Critical)
        self.msg.setStandardButtons(QMessageBox.Retry)
        self.msg.setFixedSize(800, 800)

        self.setStyleSheet("""QPushButton
                        {
                            background-color : #073b4c;
                            color: #FFFFFF;
                            font-weight: bold;
                            height: 25px;
                            border: 5px solid #2e7f99;
                            padding: 2px;
                            margin: 2px;
                            font-size: 20px;
                        }
                        QPushButton::hover
                        {
                            color: #adadad;
                            background-color : #052833;
                        }
                        QPushButton::pressed
                        {
                            color: #adadad;
                            background-color : #03181f;
                        }""")

    # closing application: stop thread and delete pictures
    def closeEvent(self, event):
        print("Closing application...")

        self.Worker1.stop()
        self.delete_pictures()
        event.accept()
    
    # creating the GUI grid layout & labels/widgets/buttons
    def createLayout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # camera box
        self.camera_label = QLabel(self)
        self.camera_label.setFixedSize(BOX_WIDTH, BOX_HEIGHT)
        self.camera_label.setStyleSheet("border: 7px solid purple;")
        
        # camera, retry, and reset buttons
        self.camera_button = QPushButton("Click Here to Take A Picture", self)
        self.retry_button = QPushButton("Retry", self)
        self.reset_button = QPushButton("New Game", self)
        self.retry_button.hide()
        self.reset_button.hide()
    
        # text bar
        self.text_label = QLabel("Take A Picture to Train the AI\n(0/3)", self)
        self.text_label.setFont(QFont("Helvetica", 28))
        self.text_label.setStyleSheet("color: #FFFFFF;"
                                      "background-color: #073b4c;"
                                      "font-weight: bold;"
                                      "padding: 2px;"
                                      "margin: 2px;"
                                      "height: 30px")
        
        self.text_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        # image boxes
        self.label1 = QLabel(self)
        self.label2 = QLabel(self)
        self.label3 = QLabel(self)
        self.label4 = QLabel(self)
        
        self.label1.setFixedSize(BOX_WIDTH, BOX_HEIGHT)
        self.label2.setFixedSize(BOX_WIDTH, BOX_HEIGHT)
        self.label3.setFixedSize(BOX_WIDTH, BOX_HEIGHT)
        self.label4.setFixedSize(BOX_WIDTH, BOX_HEIGHT)

        self.label1.setStyleSheet("background-color: #ef476f;"
                                  "border: 7px solid #ef476f;")
        self.label2.setStyleSheet("background-color: #ffd166;"
                                  "border: 7px solid #ffd166;")
        self.label3.setStyleSheet("background-color: #06d6a0;"
                                  "border: 7px solid #06d6a0;")
        self.label4.setStyleSheet("background-color: #118ab2;"
                                  "border: 7px solid #118ab2;")
        

        # adding widgets to the grid
        self.grid = QGridLayout()
        self.grid.addWidget(self.camera_label, 1, 0)
        self.grid.addWidget(self.text_label, 0, 0, 1, 2)
        self.grid.addWidget(self.label1, 1, 0, alignment=Qt.AlignRight)
        self.grid.addWidget(self.label2, 1, 1, alignment=Qt.AlignLeft)
        self.grid.addWidget(self.label3, 2, 0, alignment=Qt.AlignRight)
        self.grid.addWidget(self.label4, 2, 1, alignment=Qt.AlignLeft)
        self.grid.addWidget(self.camera_button, 3, 0, 1, 2)
        self.grid.addWidget(self.retry_button, 3, 0)
        self.grid.addWidget(self.reset_button, 3, 1)

        central_widget.setLayout(self.grid)

        self.camera_label.raise_()

    # update live camera feed (camera box)
    def ImageUpdateSlot(self, img):
        self.camera_label.setPixmap(QPixmap.fromImage(img))

    # take pictures & analyze
    def capture_image(self):
        print("capture image")

        # check if frame was taken successfully
        ret, frame = self.cap.read()
        if ret:
            try:
                # save image
                path = 'reference_image_' + str(self.count+1) + '.jpg'
                cv2.imwrite(path, frame)

                # convert image to embedding (DeepFace AI Facial Recognition Model) 
                embedding = DeepFace.represent(img_path=path, model_name="ArcFace")
                self.images.append(embedding[0]['embedding'])
                # if no face is detected, throws an error
                
                # convert to proper color, orientation
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                flipped_frame = cv2.flip(frame, 1)
                convert_frame = QImage(flipped_frame.data, flipped_frame.shape[1], flipped_frame.shape[0], QImage.Format_RGB888)
                pic = convert_frame.scaled(BOX_WIDTH, BOX_HEIGHT, Qt.KeepAspectRatio)

                # convert to PyQt5 compatible image                
                pixmap = QPixmap(pic)
                self.grid.removeWidget(self.camera_label)

                self.text_label.setText(f"Take A Picture to Train the AI\n({self.count + 1}/3)")

                # save image to corresponding image box & change camera box location
                if self.count < self.MAX_IMG:
                    if self.count == 0:
                        self.label1.setPixmap(pixmap)
                        self.grid.addWidget(self.camera_label, 1, 1)
                    elif self.count == 1:
                        self.label2.setPixmap(pixmap)
                        self.grid.addWidget(self.camera_label, 2, 0)
                    elif self.count == 2:
                        self.label3.setPixmap(pixmap)
                        self.grid.addWidget(self.camera_label, 2, 1)
                        self.text_label.setText("Final Picture! Fool the AI!\n(3/3)")
                    
                    self.count += 1
                    
                else:
                    # if final, then compare faces
                    self.label4.setPixmap(pixmap)
                    self.compare_faces(True) # True -> face is found
                
                print("Worker1 ThreadActive:", self.Worker1.ThreadActive)
                    
            # face not found
            except Exception as e:
                print("Error:", e)

                if self.count < self.MAX_IMG:
                    self.msg.exec_() # error msg box thrown
                else:
                    # save image to fourth image box
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    flipped_frame = cv2.flip(frame, 1)
                    convert_frame = QImage(flipped_frame.data, flipped_frame.shape[1], flipped_frame.shape[0], QImage.Format_RGB888)
                    pic = convert_frame.scaled(BOX_WIDTH, BOX_HEIGHT, Qt.KeepAspectRatio)
                    pixmap = QPixmap(pic)
                    
                    self.label4.setPixmap(pixmap)
                    self.compare_faces(False) # False -> face was not found

    # comparing embeddings
    def compare_faces(self, face): 
        self.camera_label.hide()
        self.camera_button.hide()
        self.retry_button.show()
        self.reset_button.show()

        if face: # average training embeddings and compare distance (compare to threshold value)
            avg = np.average(self.images, axis=0)
            distance = find_cosine_distance(avg, self.images.pop(-1))
            print("Distance:", distance)

            print(len(self.images))

            if distance < THRESHOLD:
                self.text_label.setText(f"I recognize you!\nSimilarity score: {distance:.2f}")
            else:
                self.text_label.setText(f"You fooled me! I can't recognize you!\nSimilarity score: {distance:.2f}")
        else: # face wasn't found
            self.text_label.setText("You fooled me!\nI couldn't find a face. :(")

    # reset game (need new training photos)
    def reset(self):
        self.retry_button.hide()
        self.reset_button.hide()

        self.count = 0
        self.images = []

        self.label1.clear()
        self.label2.clear()
        self.label3.clear()
        self.label4.clear()

        self.delete_pictures()

        self.grid.removeWidget(self.camera_label)
        self.grid.addWidget(self.camera_label, 1, 0)

        self.camera_label.show()
        self.camera_button.show()

        self.text_label.setText("Take A Picture to Train the AI\n(0/3)")

    # retry game (keep training photos, retake last photo)
    def retry(self):
        self.retry_button.hide()
        self.reset_button.hide()

        self.label4.clear()
        self.grid.removeWidget(self.camera_label)
        self.grid.addWidget(self.camera_label, 2, 1)
        
        self.camera_label.show()
        self.camera_button.show()

        self.text_label.setText("Final Picture! Fool the AI!\n(3/3)")

    # delete pictures
    def delete_pictures(self):
        for i in range(1, self.MAX_IMG + 2):
            if os.path.exists(f"reference_image_{i}.jpg"):
                os.remove(f"reference_image_{i}.jpg")

# thread for live camera feed
class Worker1(QThread):
    ImageUpdate = pyqtSignal(QImage)

    def __init__(self, cap):
        super().__init__()
        self.cap = cap
    
    def run(self):
        print("Worker1 thread started.")
        self.ThreadActive = True

        while self.ThreadActive:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                flipped_frame = cv2.flip(frame, 1)
                convert_frame = QImage(flipped_frame.data, flipped_frame.shape[1], flipped_frame.shape[0], QImage.Format_RGB888)
                pic = convert_frame.scaled(BOX_WIDTH, BOX_HEIGHT, Qt.KeepAspectRatio)

                self.ImageUpdate.emit(pic)

    def stop(self):
        self.ThreadActive = False
        self.cap.release()
        print("Worker1 thread ended.")


def main():
    print("Starting application...")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
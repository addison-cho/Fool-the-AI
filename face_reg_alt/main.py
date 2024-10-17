"""
TO-DO:
- padding
- fix scaling
"""

import sys
import os
import cv2
import numpy as np

from deepface import DeepFace
from deepface.modules.verification import find_cosine_distance

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
THRESHOLD = .5

def exception_hook(exc_type, exc_value, exc_traceback):
    print("aksdfj", exc_type, exc_value)
    traceback.print_tb(exc_traceback, limit=None, file=sys.stdout)

sys.excepthook = exception_hook

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fool the AI")
        self.setGeometry(0, 0, 1600, 900)
        self.createLayout()

        self.Worker1 = Worker1()
        self.Worker1.start()
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)    

        self.camera_button.clicked.connect(self.capture_image)
        self.retry_button.clicked.connect(self.retry)
        self.reset_button.clicked.connect(self.reset)

        self.count = 0
        self.MAX_IMG = 3
        self.images = []

        self.msg = QMessageBox()
        self.msg.setWindowTitle("Uh Oh!")
        self.msg.setText("I couldn't find a face! Please try again.")
        self.msg.setIcon(QMessageBox.Critical)
        self.msg.setStandardButtons(QMessageBox.Retry)

        self.setStyleSheet("""QPushButton
                        {
                            background-color : #073b4c;
                            color: #FFFFFF;
                            font-weight: bold;
                            height: 30px;
                            border: 5px solid #2e7f99;
                            padding: 2px;
                            margin: 10px;
                            font-size: 25px;
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


    def closeEvent(self, event):
        self.Worker1.stop()
        self.delete_pictures()
        event.accept()
        
    def createLayout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self.camera_label = QLabel(self)
        self.camera_label.setFixedSize(320, 240)
        self.camera_label.setStyleSheet("border: 10px solid purple;")
        
        self.camera_button = QPushButton("Click Here to Take A Picture", self)
        self.retry_button = QPushButton("Retry", self)
        self.reset_button = QPushButton("New Game", self)
        self.retry_button.hide()
        self.reset_button.hide()
    
        self.text_label = QLabel("Take A Picture to Train the AI\n(0/3)", self)
        self.text_label.setFont(QFont("Helvetica", 40))
        self.text_label.setStyleSheet("color: #FFFFFF;"
                                      "background-color: #073b4c;"
                                      "font-weight: bold;"
                                      "padding: 2px;"
                                      "margin: 5px;"
                                      "height: 45px")
        
        self.text_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.label1 = QLabel(self)
        self.label2 = QLabel(self)
        self.label3 = QLabel(self)
        self.label4 = QLabel(self)
        
        self.label1.setFixedSize(320, 240)
        self.label2.setFixedSize(320, 240)
        self.label3.setFixedSize(320, 240)
        self.label4.setFixedSize(320, 240)

        self.label1.setStyleSheet("background-color: #ef476f;"
                                  "border: 10px solid #ef476f;")
        self.label2.setStyleSheet("background-color: #ffd166;"
                                  "border: 10px solid #ffd166;")
        self.label3.setStyleSheet("background-color: #06d6a0;"
                                  "border: 10px solid #06d6a0;")
        self.label4.setStyleSheet("background-color: #118ab2;"
                                  "border: 10px solid #118ab2;")
        

        self.grid = QGridLayout()
        self.grid.addWidget(self.camera_label, 1, 0)
        self.grid.addWidget(self.text_label, 0, 0, 1, 2)
        self.grid.addWidget(self.label1, 1, 0)
        self.grid.addWidget(self.label2, 1, 1)
        self.grid.addWidget(self.label3, 2, 0)
        self.grid.addWidget(self.label4, 2, 1)
        self.grid.addWidget(self.camera_button, 3, 0, 1, 2)
        self.grid.addWidget(self.retry_button, 3, 0)
        self.grid.addWidget(self.reset_button, 3, 1)

        central_widget.setLayout(self.grid)

        self.camera_label.raise_()

    def ImageUpdateSlot(self, img):
        pixmap = QPixmap.fromImage(img).scaled(self.camera_label.size(), Qt.KeepAspectRatio)
        self.camera_label.setPixmap(pixmap)

    def capture_image(self):
        print("capture image")
        global cap 

        ret, frame = cap.read()
        if ret:
            try:
                path = 'reference_image_' + str(self.count+1) + '.jpg'
                cv2.imwrite(path, frame) 
                embedding = DeepFace.represent(img_path=path, model_name="ArcFace")
                self.images.append(embedding[0]['embedding'])
                
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frameFlip = cv2.flip(frame, 1)
                frameConvert = QImage(frameFlip.data, frameFlip.shape[1], frameFlip.shape[0], QImage.Format_RGB888)
                #pic = frameConvert.scaled(640, 480, Qt.KeepAspectRatio)
                
                pixmap = QPixmap(path)
                self.grid.removeWidget(self.camera_label)

                self.text_label.setText(f"Take A Picture to Train the AI\n({self.count + 1}/3)")

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
                    self.label4.setPixmap(pixmap)
                    self.compare_faces(True)
                    
            except:
                print("error")
                # face not found
                if self.count < self.MAX_IMG:
                    self.msg.exec_()  
                else:
                    pixmap = QPixmap(path)
                    self.label4.setPixmap(pixmap)
                    self.compare_faces(False)

    def compare_faces(self, face): 
        self.camera_label.hide()
        self.camera_button.hide()
        self.retry_button.show()
        self.reset_button.show()

        if face:
            avg = np.average(self.images, axis=0)
            distance = find_cosine_distance(avg, self.images.pop(-1))
            print("Distance:", distance)

            print(len(self.images))

            if distance < THRESHOLD:
                self.text_label.setText(f"I recognize you!\nSimilarity score: {distance:.2f}")
            else:
                self.text_label.setText(f"You fooled me! I can't recognize you!\nSimilarity score: {distance:.2f}")
        else:
            self.text_label.setText("You fooled me!\nI couldn't find a face. :(")

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

    def retry(self):
        self.retry_button.hide()
        self.reset_button.hide()

        self.label4.clear()
        self.grid.removeWidget(self.camera_label)
        self.grid.addWidget(self.camera_label, 2, 1)
        
        self.camera_label.show()
        self.camera_button.show()

        self.text_label.setText("Final Picture! Fool the AI!\n(3/3)")

    def delete_pictures(self):
        for i in range(1, self.MAX_IMG + 2):
            if os.path.exists(f"reference_image_{i}.jpg"):
                os.remove(f"reference_image_{i}.jpg")


class Worker1(QThread):
    ImageUpdate = pyqtSignal(QImage)
    def run(self):
        self.ThreadActive = True
        
        global cap
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, WINDOW_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WINDOW_HEIGHT)

        while self.ThreadActive:
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frameFlip = cv2.flip(frame, 1)
                frameConvert = QImage(frameFlip.data, frameFlip.shape[1], frameFlip.shape[0], QImage.Format_RGB888)
                self.ImageUpdate.emit(frameConvert)

    def stop(self):
        self.ThreadActive = False
        cap.release()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
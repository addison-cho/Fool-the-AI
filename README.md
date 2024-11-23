(README WIP)

**Fool the AI**  
Fool the AI is an interactive AI-powered game. Built using Python and DeepFace, a facial recognition framework, the game challenges participants to outsmart the AI by altering their appearance or expressions. It demonstrates the capabilities and limitations of facial recognition.  

**How It Works**  
The game prompts the user to take four photos: three for training, and on the last, the AI will try to recognize your face. The AI evaluates this based on a similarity score (0 to 1). The greater the score, the larger the differences between faces. The current threshold for this project is set at 0.5. Anything above is considered a different face by the AI.  

**Components**  
Programming Language: Python  
Libraries: DeepFace, OpenCV, PyQt5.  
(Tensorflow is a requirement, and included in requirements.txt. Later versions of Tensorflow work fine; you will just need to install tf-keras as well. Tensorflow (and consequently Keras) is currently downgraded to 2.12 due to conflicts when converting the py file to an executable.)

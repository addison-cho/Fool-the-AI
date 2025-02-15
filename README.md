See web_ver folder. face_reg folder is not updated.

**Fool the AI**  
Fool the AI is an interactive AI-powered game. Built using models built through Tensorflow (thanks face-api.js) the game challenges participants to outsmart the AI by altering their appearance or expressions. It demonstrates the capabilities and limitations of facial recognition.  

**How It Works**    
The game prompts the user to take four photos: three to use as reference, and on the last, the AI will try to recognize your face. The AI evaluates this based by calculating the distance between embeddings (vectors that represent the inputted faces). Since we're using Euclidean distances with normalized vectors (magnitude of one), our range is from 0 to 2. The greater the score, the larger the differences between faces. The current threshold for this project is set at 0.5. Anything above is considered a different face by the AI.  

**File Breakdown**__
In the web_ver folder, main.js holds the actual code logic, and index.html constructs the interface. website.html is the exact code used in the Vision 1948 website, though unpublished and inaccessible at the moment.

**Components**  
Programming Language: Javascript  

**Good Resources I Used for this Project**
Face API Documentation: https://justadudewhohacks.github.io/face-api.js/docs/index.html 
Face API Starter Guide: https://itnext.io/face-api-js-javascript-api-for-face-recognition-in-the-browser-with-tensorflow-js-bcc2a6c4cf07
Article on HTML Live Video Feed: https://srivastavayushmaan1347.medium.com/how-to-access-and-live-stream-camera-using-javascript-210e1b9a739d

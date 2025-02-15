let referenceDescriptors = []; 
let referenceImageURLs = []; 

const THRESHOLD = 0.5;

const video = document.getElementById('live-stream');
const captureBtn = document.getElementById('captureBtn');
const messageEl = document.getElementById('message');
const referenceBoxes = [
    document.getElementById('referenceBox1'),
    document.getElementById('referenceBox2'),
    document.getElementById('referenceBox3')
];
const testBox = document.getElementById('testBox');
const title = document.getElementById('title');

/*
// Math for normalizing a vector
function normalizeDescriptor(descriptor) {
    const norm = Math.sqrt(descriptor.reduce((sum, val) => sum + val * val, 0));
    return Float32Array.from(descriptor, val => val / norm);
}
*/

//face-api.js
async function loadModels() {
    // Face Detection. Locates faces in an image. Returns a bounding box w/ probability of there being a face.
    await faceapi.nets.ssdMobilenetv1.loadFromUri('./models/ssd_mobilenetv1')

    // Alternate Face Detection. Lightweight, less accurate. Not used in this project.
    // await faceapi.nets.tinyFaceDetector.loadFromUri('./models/tiny_face_detector');

    // Face Landmarks. Returns 68 point face landmarks of a given face.
    await faceapi.nets.faceLandmark68Net.loadFromUri('./models/face_landmark_68');

    // Face Recognition. Maps characteristics of a human face to a face descriptor (a feature vector with 128 values) (face embeddings)
    // Uses euclidean distance to judge distance (similarity) between vectors. 
    await faceapi.nets.faceRecognitionNet.loadFromUri('./models/face_recognition');

    console.log("Models loaded");
}

// Live video feed
async function startVideo() {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        // Requests access to camera
        // Returns a MediaStream object (represents the camera feed)
        navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
            // Sets the video (element) source to the camera stream
            video.srcObject = stream;
        })
        .catch((error) => {
            console.error("Error accessing the camera: ", error);
        });
    } else {
        console.log("Could not access the webcam. Please check your browser permissions.");
    }
}

// Captures an image with the same dimensions as the camera. Draws it onto the canvas.
async function captureImage() {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas;
}

// Button Clicked Event: Taking a Picture
captureBtn.addEventListener('click', async () => {
    const canvas = await captureImage();
    const detection = await faceapi
    // Detects the face in the bounding box w/ the highest probability of containing a face
    // Uses canvas img as input and Tiny Face Detector for face detection.
    .detectSingleFace(canvas, new faceapi.SsdMobilenetv1Options())
    .withFaceLandmarks()
    .withFaceDescriptor();

    // Alert for when no face is found
    if (!detection) {
        alert("No face detected! Please try again.");
        return;
    } else {
        console.log("Detection:", detection);

        console.log("Descriptor length:", detection.descriptor.length);
        console.log("Descriptor sample:", detection.descriptor.slice(0, 5));

        foo = Math.sqrt(detection.descriptor.reduce((sum, val) => sum + val * val, 0));
        console.log(foo);
    }


    // Normalize the face descriptor for consistent comparisons (able to scale).
    //const normalizedDescriptor = normalizeDescriptor(detection.descriptor);
    const normalizedDescriptor = detection.descriptor;
    const dataURL = canvas.toDataURL('image/jpeg');

    // Math Break! Normalizing vectors scales the vector to have a magnitude of one, while preserving its direction.
    // A magnitude of one means easy scaling, which means easy comparisons.

    if (referenceDescriptors.length < 3) {
        // Add normalized reference descriptor to the list for future use.
        referenceDescriptors.push(normalizedDescriptor);
        referenceImageURLs.push(dataURL);

        // Update HTML
        referenceBoxes[referenceDescriptors.length - 1].innerHTML =
        `<img src="${canvas.toDataURL('image/jpeg')}" width="100%" height="100%">`;
        if (referenceDescriptors.length < 3) {
            messageEl.innerText = `Reference image captured. Please capture ${3 - referenceDescriptors.length} more reference image${3 - referenceDescriptors.length > 1 ? 's' : ''}.`;
        } else {
            messageEl.innerText = "All reference images captured. Now try to fool the AI!";
        }

    } else {
        testBox.innerHTML = `<img src="${canvas.toDataURL('image/jpeg')}" width="100%" height="100%">`;

        // Run Test Image against all Reference Images. Majority must match (2/3 at least).
        // Distance is scale of 0 to 2 since our vectors are normalized (magnitude = 1)
        let matchCount = 0;
        const distances = [];
        referenceDescriptors.forEach(desc => {
            const distance = faceapi.euclideanDistance(desc, normalizedDescriptor);
            distances.push(distance);
            if (distance < THRESHOLD) {
                matchCount++;
            }
        });

        referenceBoxes.forEach((box, idx) => {
            box.innerHTML = `
              <img src="${referenceImageURLs[idx]}" width="100%" height="100%">
              <div class="distance">Distance: ${distances[idx].toFixed(2)}</div>
            `;
          });

        if (matchCount >= 2) {
            messageEl.innerText = `I recognize you! Match count: ${matchCount} out of 3.`;
        } else {
            messageEl.innerText = `You fooled me! Not enough matches (${matchCount} out of 3).`;
            launchConfetti();
        }        
        
        showFinalButtons();
        
    }
});

function launchConfetti() {
    const duration = 3 * 1000; // 5 seconds
    const animationEnd = Date.now() + duration;
    const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 1000, scalar: 5};
  
    function randomInRange(min, max) {
      return Math.random() * (max - min) + min;
    }
  
    const interval = setInterval(function() {
      const timeLeft = animationEnd - Date.now();
  
      if (timeLeft <= 0) {
        return clearInterval(interval);
      }
      const particleCount = 50 * (timeLeft / duration);
      confetti(Object.assign({}, defaults, { 
        particleCount,
        origin: { x: randomInRange(0.1, 0.9), y: Math.random() - 0.2 }
      }));
    }, 250);
  }

window.addEventListener('load', async () => {
    await loadModels();

    startVideo();
    await warmUpModel();

});

// When game is over, offer retry and restart buttons. 
function showFinalButtons() {
    document.getElementById('controls').innerHTML = `
        <button id="retryBtn">Retry</button>
        <button id="restartBtn">Start a New Game</button>
    `;

    document.getElementById('retryBtn').addEventListener('click', () => {
        testBox.innerHTML = "Test Image";
        messageEl.innerText = "Take a new test image!";
        document.getElementById('controls').innerHTML = '<button id="captureBtn">Take a Picture!</button>';
        document.getElementById('captureBtn').addEventListener('click', async () => captureBtn.click());
    });

    document.getElementById('restartBtn').addEventListener('click', () => {
        referenceDescriptors = [];
        referenceImageURLs = [];
        referenceBoxes.forEach(box => box.innerHTML = "Reference Image");
        testBox.innerHTML = "Test Image";
        messageEl.innerText = "Please take a reference image.";
        document.getElementById('controls').innerHTML = '<button id="captureBtn">Take a Picture!</button>';
        document.getElementById('captureBtn').addEventListener('click', async () => captureBtn.click());
    });
}

async function warmUpModel() {
  // Wait a short moment to allow the camera to adjust (e.g., 1-2 seconds)
  await new Promise(resolve => setTimeout(resolve, 2000));
  // Capture a frame from the video feed
  const canvas = await captureImage();

  // Perform a dummy detection; if no face is detected, that's okay
  await faceapi
    .detectSingleFace(canvas, new faceapi.SsdMobilenetv1Options())
    .withFaceLandmarks()
    .withFaceDescriptor();
  
  console.log("Model warmed up with a real frame");
}
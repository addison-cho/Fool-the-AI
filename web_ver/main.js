let trainingDescriptors = []; // Array to store up to 3 training descriptors
let trainingImageURLs = [];

const THRESHOLD = 0.6;

const video = document.getElementById('live-stream');
const captureBtn = document.getElementById('captureBtn');
const messageEl = document.getElementById('message');
const trainingBoxes = [
    document.getElementById('trainingBox1'),
    document.getElementById('trainingBox2'),
    document.getElementById('trainingBox3')
];
const testBox = document.getElementById('testBox');
const title = document.getElementById('title');

// Math for normalizing a vector
function normalizeDescriptor(descriptor) {
    const norm = Math.sqrt(descriptor.reduce((sum, val) => sum + val * val, 0));
    return Float32Array.from(descriptor, val => val / norm);
}

//face-api.js
async function loadModels() {
    // Face Detection. Locates faces in an image. Returns a bounding box w/ probability of there being a face.
    await faceapi.nets.ssdMobilenetv1.loadFromUri('./models/ssd_mobilenetv1')

    // Alternate Face Detection. Lightweight, less accurate. Not used in this project.
    await faceapi.nets.tinyFaceDetector.loadFromUri('./models/tiny_face_detector');

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
    } else; {
        console.log("Descriptor length:", detection.descriptor.length);
        console.log("Descriptor sample:", detection.descriptor.slice(0, 5));
    }

    // Normalize the face descriptor for consistent comparisons (able to scale).
    const normalizedDescriptor = normalizeDescriptor(detection.descriptor);
    const dataURL = canvas.toDataURL('image/jpeg');

    // Math Break! Normalizing vectors scales the vector to have a magnitude of one, while preserving its direction.
    // A magnitude of one means easy scaling, which means easy comparisons.

    if (trainingDescriptors.length < 3) {
        // Add normalized training descriptor to the list for future use.
        trainingDescriptors.push(normalizedDescriptor);
        trainingImageURLs.push(dataURL);

        // Update HTML
        trainingBoxes[trainingDescriptors.length - 1].innerHTML =
        `<img src="${canvas.toDataURL('image/jpeg')}" width="100%" height="100%">`;
        if (trainingDescriptors.length < 3) {
            messageEl.innerText = `Training image captured. Please capture ${3 - trainingDescriptors.length} more training image${3 - trainingDescriptors.length > 1 ? 's' : ''}.`;
        } else {
            messageEl.innerText = "All training images captured. Now try to fool the AI!";
        }

    } else {
        testBox.innerHTML = `<img src="${canvas.toDataURL('image/jpeg')}" width="100%" height="100%">`;

        // Create a labeled descriptor using the list of normalized training descriptor.
        const labeledDescriptor = new faceapi.LabeledFaceDescriptors("User", trainingDescriptors);
        const faceMatcher = new faceapi.FaceMatcher([labeledDescriptor], THRESHOLD);
        const bestMatch = faceMatcher.findBestMatch(normalizedDescriptor);

        // Run Test Image against all Training Images. Majority must match (2/3 at least).
        // Distance is scale of 0 to 2 since our vectors are normalized (magnitude = 1)
        let matchCount = 0;
        const distances = [];
        trainingDescriptors.forEach(desc => {
            const distance = faceapi.euclideanDistance(desc, normalizedDescriptor);
            distances.push(distance);
            if (distance < THRESHOLD) {
                matchCount++;
            }
        });

        trainingBoxes.forEach((box, idx) => {
            box.innerHTML = `
              <img src="${trainingImageURLs[idx]}" width="100%" height="100%">
              <div class="distance">Distance: ${distances[idx].toFixed(2)}</div>
            `;
          });

        if (matchCount >= 2) {
            messageEl.innerText = `I recognize you! Majority match count: ${matchCount} out of 3.`;
        } else {
            messageEl.innerText = `You fooled me! Not enough matches (only ${matchCount} out of 3).`;
        }
        
        showFinalButtons();
        }
});

// When game is over, offer retry and restart buttons. 
function showFinalButtons() {
    document.getElementById('controls').innerHTML = `
        <button id="retryBtn">Retry</button>
        <button id="restartBtn">Restart</button>
    `;

    document.getElementById('retryBtn').addEventListener('click', () => {
        testBox.innerHTML = "Test Image";
        messageEl.innerText = "Take a new test image!";
        document.getElementById('controls').innerHTML = '<button id="captureBtn">Take a Picture!</button>';
        document.getElementById('captureBtn').addEventListener('click', async () => captureBtn.click());
    });

    document.getElementById('restartBtn').addEventListener('click', () => {
        trainingDescriptors = [];
        trainingImageURLs = [];
        trainingBoxes.forEach(box => box.innerHTML = "Training Image");
        testBox.innerHTML = "Test Image";
        messageEl.innerText = "Please take a training image.";
        document.getElementById('controls').innerHTML = '<button id="captureBtn">Take a Picture!</button>';
        document.getElementById('captureBtn').addEventListener('click', async () => captureBtn.click());
    });
}

window.addEventListener('load', async () => {
    await loadModels();
    startVideo();
});
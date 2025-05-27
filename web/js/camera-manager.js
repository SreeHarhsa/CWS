/**
 * Camera Manager for Chroma Wave Studios
 * Handles camera access, face detection, and image capture
 */
class CameraManager {
    constructor() {
        // Camera elements
        this.video = document.getElementById('camera-preview');
        this.captureButton = document.getElementById('capture-btn');
        this.switchButton = document.getElementById('switch-camera-btn');
        
        // Camera state
        this.stream = null;
        this.facingMode = CONFIG.camera.facingMode || 'user';
        this.faceLandmarksDetector = null;
        
        // Bind methods
        this.startCamera = this.startCamera.bind(this);
        this.stopCamera = this.stopCamera.bind(this);
        this.switchCamera = this.switchCamera.bind(this);
        this.captureImage = this.captureImage.bind(this);
        
        // Initialize camera functionality when these elements exist
        if (this.video && this.captureButton && this.switchButton) {
            this.init();
        }
    }
    
    /**
     * Initialize camera manager
     */
    async init() {
        // Add event listeners
        this.captureButton.addEventListener('click', this.captureImage);
        this.switchButton.addEventListener('click', this.switchCamera);
        
        // Load face detection model
        try {
            // Load the MediaPipe FaceMesh model
            this.faceLandmarksDetector = await faceLandmarksDetection.createDetector(
                faceLandmarksDetection.SupportedModels.MediaPipeFaceMesh,
                {
                    runtime: 'mediapipe',
                    solutionPath: 'https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh',
                    maxFaces: CONFIG.faceDetection.maxNumFaces,
                    refineLandmarks: true
                }
            );
            
            console.log('Face detection model loaded');
        } catch (error) {
            console.error('Error loading face detection model:', error);
        }
    }
    
    /**
     * Start the camera with specified settings
     */
    async startCamera() {
        try {
            // Stop any existing stream
            if (this.stream) {
                this.stopCamera();
            }
            
            // Get user media with constraints
            const constraints = {
                video: {
                    facingMode: this.facingMode,
                    width: { ideal: CONFIG.camera.width },
                    height: { ideal: CONFIG.camera.height },
                    frameRate: { ideal: CONFIG.camera.fps }
                },
                audio: false
            };
            
            // Request camera stream
            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
            
            // Connect stream to video element
            if (this.video) {
                this.video.srcObject = this.stream;
                
                // Wait for video to be ready
                await new Promise(resolve => {
                    this.video.onloadedmetadata = () => {
                        resolve();
                    };
                });
                
                // Start playing the video
                await this.video.play();
                
                // Start face detection
                this.startFaceDetection();
            }
            
            return true;
        } catch (error) {
            console.error('Error starting camera:', error);
            
            // Show a user-friendly error message
            if (error.name === 'NotAllowedError') {
                alert('Camera access denied. Please allow camera access to create an avatar.');
            } else if (error.name === 'NotFoundError') {
                alert('No camera found. Please connect a camera to continue.');
            } else {
                alert('Error accessing camera: ' + error.message);
            }
            
            return false;
        }
    }
    
    /**
     * Stop the camera and release resources
     */
    stopCamera() {
        if (this.stream) {
            // Stop all tracks
            const tracks = this.stream.getTracks();
            tracks.forEach(track => track.stop());
            this.stream = null;
            
            // Clear video source
            if (this.video) {
                this.video.srcObject = null;
            }
        }
    }
    
    /**
     * Switch between front and back cameras
     */
    async switchCamera() {
        // Toggle facing mode
        this.facingMode = this.facingMode === 'user' ? 'environment' : 'user';
        
        // Restart camera with new facing mode
        await this.startCamera();
    }
    
    /**
     * Start continuous face detection
     */
    async startFaceDetection() {
        if (!this.faceLandmarksDetector || !this.video) return;
        
        const detectFace = async () => {
            // Check if video is playing
            if (this.video.paused || this.video.ended || !this.stream) {
                return;
            }
            
            try {
                // Detect faces
                const faces = await this.faceLandmarksDetector.estimateFaces(this.video);
                
                // If faces detected, update UI
                this.updateFaceGuide(faces);
                
                // Enable/disable capture button based on face detection
                if (this.captureButton) {
                    this.captureButton.disabled = faces.length === 0;
                }
            } catch (error) {
                console.error('Error detecting face:', error);
            }
            
            // Continue detection loop
            requestAnimationFrame(detectFace);
        };
        
        // Start the detection loop
        detectFace();
    }
    
    /**
     * Update face guide overlay based on detected faces
     * @param {Array} faces - Detected face data
     */
    updateFaceGuide(faces) {
        const faceGuide = document.querySelector('.face-guide');
        if (!faceGuide) return;
        
        if (faces && faces.length > 0) {
            // A face is detected
            faceGuide.classList.add('face-detected');
            
            // Get the first face
            const face = faces[0];
            
            // In a real implementation, you might adjust the guide position/size
            // based on the face landmarks
        } else {
            // No face detected
            faceGuide.classList.remove('face-detected');
        }
    }
    
    /**
     * Capture an image from the camera
     */
    captureImage() {
        if (!this.video || !this.stream) {
            console.error('Camera not initialized');
            return null;
        }
        
        try {
            // Create a canvas to capture the frame
            const canvas = document.createElement('canvas');
            canvas.width = this.video.videoWidth;
            canvas.height = this.video.videoHeight;
            
            // Draw the video frame to the canvas
            const context = canvas.getContext('2d');
            context.drawImage(this.video, 0, 0, canvas.width, canvas.height);
            
            // Convert to data URL
            const imageDataURL = canvas.toDataURL('image/png', CONFIG.avatarGeneration.imageQuality);
            
            // Send the image to the UI manager
            if (window.uiManager) {
                // This would be used to enable the generate button
                const generateBtn = document.getElementById('generate-avatar-btn');
                if (generateBtn) {
                    generateBtn.disabled = false;
                }
                
                // Display the captured image in the preview
                const previewImg = document.createElement('img');
                previewImg.src = imageDataURL;
                previewImg.onload = () => {
                    // In a real app, this would display in a preview area
                    console.log('Image captured successfully');
                };
                
                return imageDataURL;
            }
        } catch (error) {
            console.error('Error capturing image:', error);
            return null;
        }
    }
    
    /**
     * Check if device has camera
     * @returns {Promise<boolean>} - True if camera is available
     */
    static async hasCamera() {
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            return devices.some(device => device.kind === 'videoinput');
        } catch (error) {
            console.error('Error checking for camera:', error);
            return false;
        }
    }
}

// Initialize Camera Manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Create instance and expose to window for debugging
    window.cameraManager = new CameraManager();
    
    // Auto-start camera when the camera tab is shown
    const cameraTab = document.getElementById('camera-tab');
    if (cameraTab) {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && 
                    mutation.attributeName === 'class' && 
                    cameraTab.classList.contains('active')) {
                    // Camera tab is active, start the camera
                    window.cameraManager.startCamera();
                }
            });
        });
        
        observer.observe(cameraTab, { attributes: true });
    }
});
# Chroma Wave Studios (CWS) - Virtual Avatar System

CWS is a comprehensive virtual avatar system that creates photorealistic digital twins from webcam captures or uploaded images, allowing users to try on various accessories like clothing, jewelry, watches, and shoes.

![CWS Logo](web/assets/images/cws-logo.svg)

## 🌟 Features
  - Live camera capture (OpenCV/YOLO)
- **Avatar Creation**
  - Live camera capture with OpenCV and YOLO
  - Face detection and feature extraction
  - Realistic avatar generation
  - Jewelry
- **Virtual Try-On**
  - Multiple accessory categories: clothing, jewelry, shoes, watches
  - Intelligently positions accessories based on body keypoints
  - Realistic rendering and blending
- **Realistic Rendering**: The system ensures avatars look 100% like the person, not cartoonish or animated
- **Dual Interface**
  - Modern JavaScript web interface with real-time processing
  - Streamlit-based Python interface
  - Responsive design with dark/light mode
- **Frontend**: Streamlit UI
## 🛠️ Technical Stack
- **3D Modeling**: Various libraries for realistic avatar creation
### Backend
- **Python 3.8+**
- **OpenCV** for image processing
- **YOLO** for detection
- **MediaPipe** for face and body keypoints
- **NumPy** for numerical operations
- **Streamlit** for Python UI
4. System renders the avatar wearing the selected items
### Frontend
- **Vanilla JavaScript (ES6+)**
- **TensorFlow.js** for client-side face detection
- **MediaPipe.js** for pose estimation
- **HTML5/CSS3** with a responsive design
git clone https://github.com/SreeHarhsa/CWS.git
## 🚀 Installation

### Prerequisites
- Python 3.8+
- pip
- Webcam (for live mode)
# Install dependencies
### Step 1: Clone the Repository
```bash
git clone https://github.com/SreeHarhsa/CWS.git
cd CWS
```

### Step 2: Install Dependencies

```
CWS/
├── app.py                  # Main Streamlit application
### Step 3: Run the Application
├── src/
# Run the combined server (Flask + Streamlit)
python server.py

```
│   │   └── generator.py    # Avatar generation algorithms
The application will open automatically in your default browser:
- Web Interface: http://localhost:5000
- Streamlit Interface: http://localhost:8501
│   │   ├── accessories.py  # Accessory management
## 📂 Project Structure
│   │   └── renderer.py     # Final rendering
│   │
│   └── utils/              # Utility functions
├── app.py                  # Main Streamlit application
├── server.py               # Combined Flask + Streamlit server
├── requirements.txt        # Project dependencies
│
├── web/                    # JavaScript Web UI
│   ├── index.html          # Main HTML
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   └── assets/             # Images and static assets
│
├── src/                    # Python backend modules
│   ├── avatar_generator/   # Avatar creation components
│   │   ├── capture.py      # Camera capture
│   │   ├── processor.py    # Image processing
│   │   └── generator.py    # Avatar generation
│   │
│   ├── virtual_tryon/      # Try-on functionality
│   │   ├── accessories.py  # Accessory management
│   │   ├── fitting.py      # Virtual fitting
│   │   └── renderer.py     # Final rendering
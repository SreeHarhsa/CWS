# Chroma Wave Studios (CWS) - Virtual Avatar System

CWS is a comprehensive virtual avatar system that creates photorealistic digital twins from webcam captures or uploaded images, allowing users to try on various accessories like clothing, jewelry, watches, and shoes.

![CWS Logo](web/assets/images/cws-logo.svg)

## 🌟 Features

- **Avatar Creation**
  - Live camera capture with OpenCV and YOLO
  - Face detection and feature extraction
  - Realistic avatar generation

- **Virtual Try-On**
  - Multiple accessory categories: clothing, jewelry, shoes, watches
  - Intelligently positions accessories based on body keypoints
  - Realistic rendering and blending

- **Dual Interface**
  - Modern JavaScript web interface with real-time processing
  - Streamlit-based Python interface
  - Responsive design with dark/light mode

## 🛠️ Technical Stack

### Backend
- **Python 3.8+**
- **OpenCV** for image processing
- **YOLO** for detection
- **MediaPipe** for face and body keypoints
- **NumPy** for numerical operations
- **Streamlit** for Python UI

### Frontend
- **Vanilla JavaScript (ES6+)**
- **TensorFlow.js** for client-side face detection
- **MediaPipe.js** for pose estimation
- **HTML5/CSS3** with a responsive design

## 🚀 Installation

### Prerequisites
- Python 3.8+
- pip
- Webcam (for live mode)

### Step 1: Clone the Repository
```bash
git clone https://github.com/SreeHarhsa/CWS.git
cd CWS
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
# Run the combined server (Flask + Streamlit)
python server.py
```

The application will open automatically in your default browser:
- Web Interface: http://localhost:5000
- Streamlit Interface: http://localhost:8501

## 📂 Project Structure

```
CWS/
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
│   │
│   └── utils/              # Utility functions
│       ├── image_utils.py  # Image manipulation utilities
│       └── ui_helpers.py   # UI helper functions
│
└── data/                   # Data assets
    ├── models/             # AI models
    ├── accessories/        # Accessory images
    └── samples/            # Sample images
```

## 🔍 Usage

1. **Create Your Avatar**
   - Use your webcam to capture a photo, or upload an image
   - Ensure clear lighting and a neutral facial expression
   - Generate your digital twin

2. **Try On Accessories**
   - Switch between different accessory categories
   - Select items to try on
   - Mix and match to create your perfect look

3. **Save and Share**
   - Save your favorite looks to your gallery
   - Download as images to share
   - Compare different styles

## 🧩 Customization

### Adding New Accessories

1. Add accessory images to the appropriate category folder in `data/accessories/`
2. Update the accessory metadata in `src/virtual_tryon/accessories.py`

### Modifying Avatar Styles

Advanced users can adjust avatar generation parameters in `src/avatar_generator/generator.py`

## 🔗 Integration with Other Systems

CWS is designed to be easily integrated with other applications through its API endpoints:
- `/api/avatar/generate` - Generate an avatar from an image
- `/api/accessories/<category>` - Retrieve accessories by category
- `/api/avatar/<id>/try-on` - Apply an accessory to an avatar

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👏 Acknowledgments

- Face detection and landmark models from MediaPipe
- Icons from Font Awesome
- Sample accessories created for demonstration purposes

---

© 2025 Chroma Wave Studios. Created by Sree Harsha.
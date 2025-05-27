# Chroma Wave Studios (CWS)

An AI-powered virtual avatar system that creates realistic digital twins from photos or webcam and allows users to try on various accessories.

## Features

- **Avatar Creation**: Generate photorealistic digital avatars using:
  - Live camera capture (OpenCV/YOLO)
  - Uploaded images
  
- **Virtual Try-On**: Test various accessories on your digital twin:
  - Clothing
  - Jewelry
  - Shoes
  - Watches
  - And more

- **Realistic Rendering**: The system ensures avatars look 100% like the person, not cartoonish or animated

## Technical Stack

- **Backend**: Python
- **Frontend**: Streamlit UI
- **Computer Vision**: OpenCV, YOLO for detection
- **3D Modeling**: Various libraries for realistic avatar creation
- **Virtual Try-On**: AI-powered fitting algorithms

## Usage Flow

1. User provides input (webcam capture or image upload)
2. System generates a photorealistic avatar
3. User selects accessories to try on
4. System renders the avatar wearing the selected items

## Installation

```bash
# Clone the repository
git clone https://github.com/SreeHarhsa/CWS.git
cd CWS

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## Project Structure

```
CWS/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Project dependencies
├── src/
│   ├── avatar_generator/   # Avatar generation modules
│   │   ├── __init__.py
│   │   ├── capture.py      # Camera capture functionality
│   │   ├── processor.py    # Image processing utilities
│   │   └── generator.py    # Avatar generation algorithms
│   │
│   ├── virtual_tryon/      # Virtual try-on functionality
│   │   ├── __init__.py
│   │   ├── accessories.py  # Accessory management
│   │   ├── fitting.py      # Try-on algorithms
│   │   └── renderer.py     # Final rendering
│   │
│   └── utils/              # Utility functions
│       ├── __init__.py
│       ├── image_utils.py  # Image manipulation utilities
│       └── ui_helpers.py   # UI helper functions
│
├── data/
│   ├── accessories/        # Accessory models and images
│   ├── models/             # Pre-trained models
│   └── samples/            # Sample images for testing
│
└── tests/                  # Unit and integration tests
    └── __init__.py
```

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
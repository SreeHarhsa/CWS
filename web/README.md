# Chroma Wave Studios (CWS) - Web Interface

This directory contains the JavaScript-based web interface for the Chroma Wave Studios avatar system.

## Features

- Interactive 3D avatar creation from webcam or uploaded images
- Real-time virtual try-on of accessories, clothing, jewelry, and more
- Modern, responsive UI with dark/light mode support
- Gallery of saved looks
- Client-side processing with TensorFlow.js and face landmark detection

## Structure

- `index.html` - Main HTML file
- `css/` - Stylesheet files
  - `styles.css` - Main styles
  - `animations.css` - Animation effects
- `js/` - JavaScript modules
  - `app.js` - Main application script
  - `ui-manager.js` - UI interaction handling
  - `camera-manager.js` - Webcam access and capture
  - `avatar-generator.js` - Avatar generation and manipulation
  - `accessory-manager.js` - Accessory handling and fitting
  - `looks-manager.js` - Saved looks management
  - `config.js` - Application configuration
- `assets/` - Static assets
  - `images/` - Images including logo and placeholders
  - `accessories/` - Accessory images organized by category

## Usage

You can run this web interface in two ways:

### 1. Local Development Server

```bash
# Using Python's built-in HTTP server
cd web
python -m http.server

# Open http://localhost:8000 in your browser
```

### 2. Integration with Python Backend

For full functionality including advanced avatar generation:

```bash
# From the root directory
python server.py

# Open http://localhost:8501 in your browser
```

## Browser Support

- Chrome (recommended)
- Firefox
- Safari (limited WebGL support)
- Edge

## Technology Stack

- HTML5
- CSS3 with CSS Variables for theming
- Vanilla JavaScript (ES6+)
- TensorFlow.js for face detection and landmark tracking
- MediaPipe for pose estimation
  
## Connecting with the Python Backend

The web interface can communicate with the Python backend through a REST API. The connection settings can be configured in `js/config.js`.

```javascript
// Example configuration
const CONFIG = {
    apiBaseUrl: '/api',  // Path to API endpoints
    // other settings...
}
```

## License

This code is part of the Chroma Wave Studios project and is governed by the project's license.
import os
import sys
import json
import base64
import logging
import numpy as np
import cv2
from flask import Flask, request, jsonify, send_from_directory
import streamlit as st
import threading
import webbrowser
from PIL import Image
from io import BytesIO
import time

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import project modules
try:
    from src.avatar_generator.processor import ImageProcessor
    from src.avatar_generator.generator import AvatarGenerator
    from src.virtual_tryon.accessories import AccessoryManager
    from src.virtual_tryon.fitting import VirtualFitter
    from src.virtual_tryon.renderer import AvatarRenderer
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you've installed all requirements from requirements.txt")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='web')

# Initialize Streamlit config
if not os.path.exists('.streamlit'):
    os.makedirs('.streamlit')
    
with open('.streamlit/config.toml', 'w') as f:
    f.write("""
[theme]
primaryColor = "#6A4DFF"
backgroundColor = "#f8f9fd"
secondaryBackgroundColor = "#ffffff"
textColor = "#293241"

[server]
port = 8501
headless = true
enableCORS = true
enableXsrfProtection = true
    """)

# Initialize Managers
image_processor = ImageProcessor()
avatar_generator = AvatarGenerator()
accessory_manager = AccessoryManager()
virtual_fitter = VirtualFitter()
avatar_renderer = AvatarRenderer()

# Cache for avatars and generated content
avatar_cache = {}

# Flask routes for API
@app.route('/api/avatar/generate', methods=['POST'])
def generate_avatar():
    """Generate an avatar from an uploaded image"""
    try:
        # Check if the post has the file part
        if 'image' not in request.files and 'image_data' not in request.json:
            return jsonify({'error': 'No image provided'}), 400
        
        if 'image' in request.files:
            # Get the image file
            image_file = request.files['image']
            # Read the image
            img = cv2.imdecode(np.frombuffer(image_file.read(), np.uint8), cv2.IMREAD_COLOR)
        else:
            # Get the base64 image data
            image_data = request.json['image_data']
            # Remove the data URL prefix if present
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            # Decode the base64 image
            img_bytes = base64.b64decode(image_data)
            # Convert to numpy array
            img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
        
        # Process the image
        processed_image = image_processor.process(img)
        
        # Generate the avatar
        avatar_model, avatar_image = avatar_generator.generate(processed_image)
        
        # Generate a unique ID for the avatar
        avatar_id = f"avatar_{int(time.time() * 1000)}"
        
        # Cache the avatar model and image
        avatar_cache[avatar_id] = {
            'model': avatar_model,
            'image': avatar_image,
            'accessories': {}
        }
        
        # Convert the avatar image to base64
        _, buffer = cv2.imencode('.png', avatar_image)
        avatar_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'avatar_id': avatar_id,
            'avatar_image': f"data:image/png;base64,{avatar_base64}"
        })
        
    except Exception as e:
        logger.error(f"Error generating avatar: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/accessories/<category>', methods=['GET'])
def get_accessories(category):
    """Get accessories by category"""
    try:
        accessories = accessory_manager.get_accessories(category)
        
        return jsonify({
            'success': True,
            'category': category,
            'accessories': [
                {
                    'id': acc.get('id', f"{category}_{i}"),
                    'name': acc.get('name', 'Unnamed Accessory'),
                    'thumbnail': acc.get('thumbnail', '')
                }
                for i, acc in enumerate(accessories)
            ]
        })
        
    except Exception as e:
        logger.error(f"Error getting accessories: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/avatar/<avatar_id>/try-on', methods=['POST'])
def try_on_accessory(avatar_id):
    """Try on an accessory on the avatar"""
    try:
        if avatar_id not in avatar_cache:
            return jsonify({'error': 'Avatar not found'}), 404
        
        # Get the request data
        data = request.json
        category = data.get('category')
        accessory_id = data.get('accessory_id')
        
        if not category or not accessory_id:
            return jsonify({'error': 'Category and accessory_id are required'}), 400
        
        # Get the accessory
        accessory = accessory_manager.get_accessory(category, accessory_id)
        
        if not accessory:
            return jsonify({'error': f'Accessory {accessory_id} not found in category {category}'}), 404
        
        # Get the avatar
        avatar = avatar_cache[avatar_id]
        
        # Store the accessory in the avatar's accessories
        avatar['accessories'][category] = accessory
        
        # Apply the accessory
        result = virtual_fitter.fit_accessory(avatar['image'].copy(), accessory)
        
        # Store the result
        avatar_cache[avatar_id]['current_image'] = result
        
        # Convert the result to base64
        _, buffer = cv2.imencode('.png', result)
        result_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'avatar_id': avatar_id,
            'category': category,
            'accessory_id': accessory_id,
            'result_image': f"data:image/png;base64,{result_base64}"
        })
        
    except Exception as e:
        logger.error(f"Error applying accessory: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/avatar/<avatar_id>/render', methods=['GET'])
def render_avatar(avatar_id):
    """Render the avatar with all accessories"""
    try:
        if avatar_id not in avatar_cache:
            return jsonify({'error': 'Avatar not found'}), 404
        
        # Get the avatar
        avatar = avatar_cache[avatar_id]
        
        # Render the avatar with all accessories
        result = avatar_renderer.render(avatar['model'], list(avatar['accessories'].values()))
        
        # Convert the result to base64
        _, buffer = cv2.imencode('.png', result)
        result_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'avatar_id': avatar_id,
            'result_image': f"data:image/png;base64,{result_base64}"
        })
        
    except Exception as e:
        logger.error(f"Error rendering avatar: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/avatar/<avatar_id>/clear', methods=['POST'])
def clear_accessories(avatar_id):
    """Clear all accessories from the avatar"""
    try:
        if avatar_id not in avatar_cache:
            return jsonify({'error': 'Avatar not found'}), 404
        
        # Get the avatar
        avatar = avatar_cache[avatar_id]
        
        # Clear accessories
        avatar['accessories'] = {}
        
        # Reset to the original image
        avatar_cache[avatar_id]['current_image'] = avatar['image'].copy()
        
        # Convert the result to base64
        _, buffer = cv2.imencode('.png', avatar['image'])
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'avatar_id': avatar_id,
            'result_image': f"data:image/png;base64,{image_base64}"
        })
        
    except Exception as e:
        logger.error(f"Error clearing accessories: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve the web files"""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# Streamlit app
def streamlit_app():
    st.set_page_config(
        page_title="Chroma Wave Studios",
        page_icon="👤",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    st.title("Chroma Wave Studios")
    st.subheader("Create your digital twin and try on accessories")
    st.markdown("---")
    
    # Display tabs
    tab1, tab2 = st.tabs(["Web Interface", "Streamlit Interface"])
    
    with tab1:
        st.header("JavaScript Web Interface")
        st.write("The web interface is available at http://localhost:5000")
        st.write("This provides a more interactive experience with client-side processing.")
        
        if st.button("Open Web Interface", key="open_web"):
            webbrowser.open("http://localhost:5000")
    
    with tab2:
        st.header("Streamlit Interface")
        st.write("This is the Streamlit-based interface with server-side processing.")
        
        avatar_creator_tab, accessory_tab = st.tabs(["Create Avatar", "Try On Accessories"])
        
        with avatar_creator_tab:
            st.write("Create your avatar from an uploaded image or webcam capture")
            
            source_option = st.radio("Select Input Source:", ["Upload Image", "Capture from Webcam"])
            
            if source_option == "Upload Image":
                uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
                
                if uploaded_file is not None:
                    try:
                        # Convert the uploaded file to an image
                        image = Image.open(uploaded_file)
                        image_array = np.array(image)
                        
                        # Display the uploaded image
                        st.image(image_array, caption="Uploaded Image", use_column_width=True)
                        
                        # Process button
                        if st.button("Generate Avatar"):
                            with st.spinner('Generating your avatar...'):
                                # Process the image
                                processed_image = image_processor.process(image_array)
                                
                                # Generate the avatar
                                avatar_model, avatar_image = avatar_generator.generate(processed_image)
                                
                                # Display the result
                                st.session_state.avatar_model = avatar_model
                                st.session_state.avatar_image = avatar_image
                                
                                # Show the avatar
                                st.image(avatar_image, caption="Your Avatar", use_column_width=True)
                                st.success("Avatar created successfully! Go to the 'Try On Accessories' tab to customize your look.")
                    
                    except Exception as e:
                        st.error(f"Error processing image: {str(e)}")
            
            else:  # Webcam option
                st.write("Webcam capture is not supported in this demo interface.")
                st.write("Please use the Web Interface for webcam support.")
        
        with accessory_tab:
            st.write("Try on different accessories on your avatar")
            
            if not hasattr(st.session_state, 'avatar_image') or st.session_state.avatar_image is None:
                st.warning("Please create an avatar first in the 'Create Avatar' tab.")
            else:
                # Display avatar and accessories side by side
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("Your Avatar")
                    
                    # Current state of the avatar
                    if hasattr(st.session_state, 'current_avatar') and st.session_state.current_avatar is not None:
                        st.image(st.session_state.current_avatar, caption="Current Look", use_column_width=True)
                    else:
                        st.image(st.session_state.avatar_image, caption="Original Avatar", use_column_width=True)
                    
                    # Reset button
                    if st.button("Reset to Original"):
                        st.session_state.current_avatar = st.session_state.avatar_image.copy()
                        st.session_state.current_accessories = []
                        st.experimental_rerun()
                
                with col2:
                    st.subheader("Select Accessories")
                    
                    # Category selection
                    category = st.selectbox("Select Category:", 
                                           ["clothing", "jewelry", "shoes", "watches"],
                                           format_func=lambda x: x.capitalize())
                    
                    # Initialize current accessories list if not exists
                    if not hasattr(st.session_state, 'current_accessories'):
                        st.session_state.current_accessories = []
                    
                    # Get accessories for the selected category
                    accessories = accessory_manager.get_accessories(category)
                    
                    # Display accessories
                    accessory_names = [acc['name'] for acc in accessories]
                    selected_accessory = st.selectbox(f"Select {category.capitalize()}:", 
                                                    options=accessory_names,
                                                    format_func=lambda x: x)
                    
                    # Apply button
                    if st.button("Apply Accessory"):
                        with st.spinner('Applying accessory...'):
                            # Get the selected accessory
                            accessory = next((acc for acc in accessories if acc['name'] == selected_accessory), None)
                            
                            if accessory:
                                # Create current avatar if not exists
                                if not hasattr(st.session_state, 'current_avatar'):
                                    st.session_state.current_avatar = st.session_state.avatar_image.copy()
                                
                                # Apply the accessory
                                result = virtual_fitter.fit_accessory(st.session_state.current_avatar, accessory)
                                
                                # Update the current avatar
                                st.session_state.current_avatar = result
                                
                                # Add to current accessories
                                # Remove any existing accessory of the same category
                                st.session_state.current_accessories = [
                                    acc for acc in st.session_state.current_accessories 
                                    if acc['category'] != category
                                ]
                                
                                # Add the new accessory
                                st.session_state.current_accessories.append({
                                    'category': category,
                                    'name': accessory['name'],
                                    'data': accessory
                                })
                                
                                st.success(f"Applied {selected_accessory} successfully!")
                                st.experimental_rerun()
                    
                    # Current outfit
                    st.subheader("Current Outfit")
                    
                    if st.session_state.current_accessories:
                        for acc in st.session_state.current_accessories:
                            st.write(f"• {acc['category'].title()}: {acc['name']}")
                    else:
                        st.write("No accessories applied yet.")
                    
                    # Download button
                    if hasattr(st.session_state, 'current_avatar') and st.session_state.current_avatar is not None:
                        # Convert to PIL for download
                        pil_img = Image.fromarray(st.session_state.current_avatar)
                        buffered = BytesIO()
                        pil_img.save(buffered, format="PNG")
                        
                        st.download_button(
                            label="Download Look",
                            data=buffered.getvalue(),
                            file_name="my_avatar_look.png",
                            mime="image/png"
                        )
    
    # Footer
    st.markdown("---")
    st.caption("© 2025 Chroma Wave Studios. Created by Sree Harsha.")
    st.caption("This demonstration combines Streamlit and JavaScript interfaces.")

# Function to run the Flask server
def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)

# Main entry point
if __name__ == "__main__":
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Open the web interface automatically
    webbrowser.open("http://localhost:5000")
    
    # Run the Streamlit app
    streamlit_app()
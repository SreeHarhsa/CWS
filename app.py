import streamlit as st
import os
import sys
import cv2
import numpy as np
from PIL import Image
import tempfile

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import project modules
from src.avatar_generator.capture import CameraCapture
from src.avatar_generator.processor import ImageProcessor
from src.avatar_generator.generator import AvatarGenerator
from src.virtual_tryon.accessories import AccessoryManager
from src.virtual_tryon.fitting import VirtualFitter
from src.virtual_tryon.renderer import AvatarRenderer
from src.utils.ui_helpers import create_sidebar, display_avatar, show_loading

# Set page configuration
st.set_page_config(
    page_title="Chroma Wave Studios",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Application title and description
st.title("Chroma Wave Studios")
st.subheader("Create your digital twin and try on accessories")
st.markdown("---")

# Initialize session state variables if they don't exist
if 'avatar_created' not in st.session_state:
    st.session_state.avatar_created = False
if 'avatar_image' not in st.session_state:
    st.session_state.avatar_image = None
if 'avatar_model' not in st.session_state:
    st.session_state.avatar_model = None
if 'current_accessories' not in st.session_state:
    st.session_state.current_accessories = []

# Create the sidebar with options
create_sidebar()

# Main application flow
def main():
    # STEP 1: Avatar Creation Section
    if not st.session_state.avatar_created:
        st.header("Create Your Avatar")
        
        # Option tabs for avatar creation
        tab1, tab2 = st.tabs(["Camera Capture", "Upload Image"])
        
        with tab1:
            st.write("Capture your photo using your webcam")
            if st.button("Open Camera"):
                with st.spinner("Initializing camera..."):
                    try:
                        camera = CameraCapture()
                        camera_image = camera.capture_image()
                        if camera_image is not None:
                            process_input_image(camera_image, "camera")
                    except Exception as e:
                        st.error(f"Error accessing camera: {str(e)}")
        
        with tab2:
            st.write("Upload a clear photo of yourself (front-facing)")
            uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                try:
                    # Convert the uploaded file to an image
                    image = Image.open(uploaded_file)
                    image_array = np.array(image)
                    process_input_image(image_array, "upload")
                except Exception as e:
                    st.error(f"Error processing uploaded image: {str(e)}")
    
    # STEP 2: Accessory Selection and Try-On (only shown after avatar creation)
    else:
        st.header("Virtual Try-On")
        
        # Display the current avatar
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Your Avatar")
            display_avatar(st.session_state.avatar_image)
            
            if st.button("Create New Avatar"):
                st.session_state.avatar_created = False
                st.session_state.avatar_image = None
                st.session_state.avatar_model = None
                st.session_state.current_accessories = []
                st.experimental_rerun()
        
        with col2:
            st.subheader("Select Accessories")
            
            # Create tabs for different accessory categories
            acc_tab1, acc_tab2, acc_tab3, acc_tab4 = st.tabs(["Clothing", "Jewelry", "Shoes", "Watches"])
            
            # Initialize accessory manager
            accessory_manager = AccessoryManager()
            
            # Clothing section
            with acc_tab1:
                clothing_items = accessory_manager.get_accessories("clothing")
                selected_clothing = st.selectbox(
                    "Select Clothing", 
                    options=[item['name'] for item in clothing_items],
                    placeholder="Choose clothing..."
                )
                
                if selected_clothing and st.button("Try Clothing"):
                    try_on_accessory("clothing", selected_clothing)
            
            # Jewelry section
            with acc_tab2:
                jewelry_items = accessory_manager.get_accessories("jewelry")
                selected_jewelry = st.selectbox(
                    "Select Jewelry", 
                    options=[item['name'] for item in jewelry_items],
                    placeholder="Choose jewelry..."
                )
                
                if selected_jewelry and st.button("Try Jewelry"):
                    try_on_accessory("jewelry", selected_jewelry)
            
            # Shoes section
            with acc_tab3:
                shoe_items = accessory_manager.get_accessories("shoes")
                selected_shoes = st.selectbox(
                    "Select Shoes", 
                    options=[item['name'] for item in shoe_items],
                    placeholder="Choose shoes..."
                )
                
                if selected_shoes and st.button("Try Shoes"):
                    try_on_accessory("shoes", selected_shoes)
            
            # Watches section
            with acc_tab4:
                watch_items = accessory_manager.get_accessories("watches")
                selected_watch = st.selectbox(
                    "Select Watch", 
                    options=[item['name'] for item in watch_items],
                    placeholder="Choose watch..."
                )
                
                if selected_watch and st.button("Try Watch"):
                    try_on_accessory("watches", selected_watch)
            
            # Display current outfit
            if st.session_state.current_accessories:
                st.subheader("Current Outfit")
                for item in st.session_state.current_accessories:
                    st.write(f"• {item['category'].title()}: {item['name']}")
                
                if st.button("Remove All Accessories"):
                    st.session_state.current_accessories = []
                    render_avatar_with_accessories([])

        # Display the final avatar with accessories
        st.subheader("Your Personalized Look")
        if hasattr(st.session_state, 'final_render') and st.session_state.final_render is not None:
            st.image(st.session_state.final_render, use_column_width=True)
            st.download_button(
                label="Download Your Look",
                data=Image.fromarray(st.session_state.final_render).tobytes(),
                file_name="my_virtual_look.png",
                mime="image/png"
            )
        else:
            st.write("Try on some accessories to see your personalized look!")

def process_input_image(image, source_type):
    """Process the input image and generate the avatar"""
    with st.spinner("Generating your avatar..."):
        try:
            # Process the image
            processor = ImageProcessor()
            processed_image = processor.process(image)
            
            # Generate the avatar
            generator = AvatarGenerator()
            avatar_model, avatar_image = generator.generate(processed_image)
            
            # Store results in session state
            st.session_state.avatar_created = True
            st.session_state.avatar_image = avatar_image
            st.session_state.avatar_model = avatar_model
            
            # Display success message
            st.success("Avatar created successfully!")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error creating avatar: {str(e)}")

def try_on_accessory(category, item_name):
    """Try on a selected accessory"""
    with st.spinner(f"Trying on {item_name}..."):
        try:
            # Initialize components
            accessory_manager = AccessoryManager()
            fitter = VirtualFitter()
            renderer = AvatarRenderer()
            
            # Get the accessory item
            accessory_item = accessory_manager.get_accessory(category, item_name)
            
            # Update the current accessories list
            # Remove any existing item in the same category
            st.session_state.current_accessories = [
                acc for acc in st.session_state.current_accessories 
                if acc['category'] != category
            ]
            
            # Add the new accessory
            st.session_state.current_accessories.append({
                'category': category, 
                'name': item_name, 
                'data': accessory_item
            })
            
            # Render the avatar with all current accessories
            render_avatar_with_accessories(st.session_state.current_accessories)
            
        except Exception as e:
            st.error(f"Error trying on accessory: {str(e)}")

def render_avatar_with_accessories(accessories):
    """Render the avatar with all the current accessories"""
    try:
        # Initialize the renderer
        renderer = AvatarRenderer()
        
        # Render the avatar with accessories
        final_render = renderer.render(
            st.session_state.avatar_model,
            accessories
        )
        
        # Store the final render in session state
        st.session_state.final_render = final_render
        
    except Exception as e:
        st.error(f"Error rendering avatar: {str(e)}")

# Run the main application
if __name__ == "__main__":
    main()
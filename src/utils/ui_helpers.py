import os
import cv2
import numpy as np
import streamlit as st
from PIL import Image

def create_sidebar():
    """Create and configure the sidebar with app options"""
    with st.sidebar:
        st.title("Chroma Wave Studios")
        st.image("https://via.placeholder.com/150x150.png?text=CWS", width=150)
        
        st.markdown("---")
        st.subheader("Settings")
        
        # Image quality setting
        image_quality = st.slider(
            "Output Image Quality",
            min_value=1,
            max_value=10,
            value=7,
            help="Higher quality means more detailed images but slower processing"
        )
        
        # Realism vs Speed setting
        realism_speed = st.select_slider(
            "Realism vs Speed",
            options=["Fastest", "Balanced", "Most Realistic"],
            value="Balanced",
            help="Choose between faster processing or more realistic results"
        )
        
        # Save settings to session state
        if 'image_quality' not in st.session_state:
            st.session_state.image_quality = image_quality
        if 'realism_speed' not in st.session_state:
            st.session_state.realism_speed = realism_speed
        
        st.markdown("---")
        
        # Information section
        st.subheader("About")
        st.markdown("""
        **Chroma Wave Studios** is an AI-powered virtual avatar system
        that creates realistic digital twins and allows trying on various accessories.
        
        - Create your avatar from webcam or photo
        - Try on different clothing, jewelry, etc.
        - Share your personalized looks
        """)
        
        st.markdown("---")
        
        # Feedback button
        if st.button("Share Feedback"):
            st.info("Feedback form would open in a real app")

def display_avatar(avatar_image, caption="Your Avatar"):
    """Display the avatar image with proper formatting"""
    if avatar_image is None:
        st.info("No avatar image available")
        return
    
    # Convert the image if it's not in the right format
    if isinstance(avatar_image, np.ndarray):
        if avatar_image.shape[2] == 4:  # Has alpha channel
            # Convert RGBA to RGB
            rgb_image = cv2.cvtColor(avatar_image, cv2.COLOR_RGBA2RGB)
        else:
            rgb_image = avatar_image.copy()
            
        # Display the image
        st.image(rgb_image, caption=caption, use_column_width=True)
    else:
        # If it's already a PIL image or something else streamlit can handle
        st.image(avatar_image, caption=caption, use_column_width=True)

def show_loading(text="Processing..."):
    """Show a loading animation with custom text"""
    with st.spinner(text):
        # This will show a spinner until the context is exited
        pass
        
def show_progress(progress_steps):
    """
    Show progress for a multi-step process
    
    Args:
        progress_steps: List of step descriptions
    
    Returns:
        progress_bar: Progress bar object to update
        status_text: Text element to update with current step
    """
    # Create progress bar
    progress_bar = st.progress(0)
    
    # Create text element for status updates
    status_text = st.empty()
    
    return progress_bar, status_text

def update_progress(progress_bar, status_text, step_index, total_steps, step_description):
    """Update progress for a multi-step process"""
    if progress_bar is not None:
        progress_bar.progress(step_index / total_steps)
    
    if status_text is not None:
        status_text.text(step_description)

def clear_progress(progress_bar, status_text):
    """Clear progress indicators"""
    if progress_bar is not None:
        progress_bar.empty()
    
    if status_text is not None:
        status_text.empty()

def display_error(title, message, suggestion=None):
    """Display an error message with a title and optional suggestion"""
    error_container = st.error(f"**{title}**")
    with error_container:
        st.write(message)
        if suggestion:
            st.write(f"**Suggestion:** {suggestion}")

def display_tips(title="Tips", tips=None):
    """Display helpful tips to the user"""
    if tips is None:
        tips = [
            "Make sure your face is clearly visible and well-lit",
            "For best results, use a front-facing image",
            "Try different accessories to create your perfect look",
            "You can create multiple avatars to compare different styles"
        ]
    
    with st.expander(title):
        for tip in tips:
            st.write(f"• {tip}")

def save_image_to_file(image, filename, directory="downloads"):
    """
    Save an image to a file
    
    Args:
        image: Image to save (numpy array or PIL Image)
        filename: Name of the file
        directory: Directory to save the file in
    
    Returns:
        str: Path to the saved file or None if failed
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Full path for the file
        file_path = os.path.join(directory, filename)
        
        # Convert image if needed
        if isinstance(image, np.ndarray):
            # Convert to PIL Image
            if image.shape[2] == 4:  # RGBA
                pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA))
            else:  # RGB
                pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        else:
            pil_image = image
        
        # Save the image
        pil_image.save(file_path)
        
        return file_path
    
    except Exception as e:
        st.error(f"Error saving image: {str(e)}")
        return None
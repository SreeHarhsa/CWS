import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import streamlit as st

def resize_image(image, target_size=(512, 512)):
    """
    Resize an image to the target size
    
    Args:
        image: Input image (numpy array or PIL Image)
        target_size: Tuple of (width, height) for the output image
        
    Returns:
        Resized image in the same format as input
    """
    # Check input type
    is_numpy = isinstance(image, np.ndarray)
    
    # Convert to PIL if needed
    if is_numpy:
        if image.shape[2] == 4:  # RGBA
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA))
        else:  # RGB or BGR
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    else:
        pil_image = image
    
    # Resize the image
    resized = pil_image.resize(target_size, Image.Resampling.LANCZOS)
    
    # Convert back to numpy if input was numpy
    if is_numpy:
        if image.shape[2] == 4:  # RGBA
            result = cv2.cvtColor(np.array(resized), cv2.COLOR_BGRA2RGBA)
        else:  # RGB or BGR
            result = cv2.cvtColor(np.array(resized), cv2.COLOR_RGB2BGR)
        return result
    
    return resized

def crop_to_face(image, face_bbox, margin=0.2):
    """
    Crop an image to focus on a detected face
    
    Args:
        image: Input image
        face_bbox: Face bounding box [x, y, w, h]
        margin: Margin around the face as a fraction of face size
        
    Returns:
        Cropped image focusing on the face
    """
    if image is None or face_bbox is None:
        return image
    
    # Get image dimensions
    h, w = image.shape[:2]
    
    # Extract face bounding box
    x, y, fw, fh = face_bbox
    
    # Calculate margins
    x_margin = int(fw * margin)
    y_margin = int(fh * margin)
    
    # Calculate crop coordinates with margins
    x1 = max(0, x - x_margin)
    y1 = max(0, y - y_margin)
    x2 = min(w, x + fw + x_margin)
    y2 = min(h, y + fh + y_margin)
    
    # Crop the image
    cropped = image[y1:y2, x1:x2]
    
    return cropped

def enhance_portrait(image, enhancement_level=1.0):
    """
    Enhance a portrait image with subtle improvements
    
    Args:
        image: Input image (numpy array or PIL Image)
        enhancement_level: Level of enhancement (0.0 to 2.0)
        
    Returns:
        Enhanced image in the same format as input
    """
    # Check input type
    is_numpy = isinstance(image, np.ndarray)
    
    # Convert to PIL if needed
    if is_numpy:
        if len(image.shape) == 3 and image.shape[2] == 4:  # RGBA
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA))
        else:  # RGB or BGR
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    else:
        pil_image = image
    
    # Apply enhancements
    # 1. Subtle sharpening
    sharpened = pil_image.filter(ImageFilter.UnsharpMask(radius=1.5, percent=50*enhancement_level, threshold=3))
    
    # 2. Slight color enhancement
    color_enhancer = ImageEnhance.Color(sharpened)
    color_enhanced = color_enhancer.enhance(1.0 + 0.2*enhancement_level)
    
    # 3. Contrast enhancement
    contrast_enhancer = ImageEnhance.Contrast(color_enhanced)
    contrast_enhanced = contrast_enhancer.enhance(1.0 + 0.15*enhancement_level)
    
    # Convert back to numpy if input was numpy
    if is_numpy:
        if len(image.shape) == 3 and image.shape[2] == 4:  # RGBA
            result = cv2.cvtColor(np.array(contrast_enhanced), cv2.COLOR_BGRA2RGBA)
        else:  # RGB or BGR
            result = cv2.cvtColor(np.array(contrast_enhanced), cv2.COLOR_RGB2BGR)
        return result
    
    return contrast_enhanced

def create_avatar_mask(image, face_bbox=None):
    """
    Create a smooth oval mask for the avatar
    
    Args:
        image: Input image
        face_bbox: Optional face bounding box to focus the mask
        
    Returns:
        Mask image (numpy array)
    """
    h, w = image.shape[:2]
    
    # Create an empty mask
    mask = np.zeros((h, w), dtype=np.uint8)
    
    # Determine center and axes of the oval
    if face_bbox is not None:
        x, y, fw, fh = face_bbox
        center = (x + fw//2, y + fh//2)
        
        # Extend oval beyond face, but keep within image
        axes_x = min(int(fw * 1.5), w//2)
        axes_y = min(int(fh * 2.0), h//2)
    else:
        center = (w//2, h//2)
        axes_x = w//2 - 20
        axes_y = h//2 - 10
    
    # Draw the elliptical mask
    cv2.ellipse(mask, center, (axes_x, axes_y), 0, 0, 360, (255, 255, 255), -1)
    
    # Blur the mask edges for smooth transition
    mask = cv2.GaussianBlur(mask, (51, 51), 0)
    
    return mask

def apply_image_mask(image, mask):
    """
    Apply a mask to an image
    
    Args:
        image: Input image (numpy array)
        mask: Mask image (numpy array)
        
    Returns:
        Masked image with transparent background
    """
    # Ensure image has an alpha channel
    if image.shape[2] == 3:
        rgba = np.zeros((image.shape[0], image.shape[1], 4), dtype=np.uint8)
        rgba[:, :, :3] = image
        rgba[:, :, 3] = 255
        image = rgba
    
    # Apply mask to the alpha channel
    image[:, :, 3] = cv2.multiply(image[:, :, 3], mask) // 255
    
    return image

def remove_background(image, segmentation_model=None):
    """
    Remove background from an image
    
    Args:
        image: Input image
        segmentation_model: Optional pre-loaded segmentation model
        
    Returns:
        Image with transparent background
    """
    # If no segmentation model is available, use a simpler approach
    if segmentation_model is None:
        # Create a simple mask
        mask = create_avatar_mask(image)
        return apply_image_mask(image, mask)
    
    # Implement more advanced background removal if a model is provided
    # This would use the segmentation model to create a more accurate mask
    
    # For now, just use the simple mask approach
    mask = create_avatar_mask(image)
    return apply_image_mask(image, mask)

def normalize_lighting(image):
    """
    Normalize lighting in an image for consistent processing
    
    Args:
        image: Input image
        
    Returns:
        Image with normalized lighting
    """
    # Convert to LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    
    # Split channels
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE to the L channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    
    # Merge channels
    merged = cv2.merge((cl, a, b))
    
    # Convert back to BGR
    normalized = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
    
    return normalized

def blend_images(foreground, background, mask=None, alpha=1.0):
    """
    Blend two images using a mask or alpha value
    
    Args:
        foreground: Foreground image
        background: Background image
        mask: Optional mask for blending
        alpha: Opacity of foreground if no mask is provided
        
    Returns:
        Blended image
    """
    # Ensure images are the same size
    if foreground.shape[:2] != background.shape[:2]:
        foreground = cv2.resize(foreground, (background.shape[1], background.shape[0]))
    
    # If mask is provided, use it for blending
    if mask is not None:
        # Ensure mask is the right size
        if mask.shape[:2] != foreground.shape[:2]:
            mask = cv2.resize(mask, (foreground.shape[1], foreground.shape[0]))
        
        # Normalize mask to range 0-1
        normalized_mask = mask.astype(float) / 255
        
        # Expand dimensions for broadcasting
        alpha_mask = np.expand_dims(normalized_mask, axis=2)
        
        # Blend using the mask
        blended = cv2.convertScaleAbs(background * (1 - alpha_mask) + foreground * alpha_mask)
    else:
        # Blend using a constant alpha
        blended = cv2.addWeighted(background, 1 - alpha, foreground, alpha, 0)
    
    return blended

def create_composite_image(images, titles=None, grid_size=None):
    """
    Create a composite grid of images
    
    Args:
        images: List of images
        titles: Optional list of titles
        grid_size: Optional tuple (rows, cols) for grid layout
        
    Returns:
        Composite image
    """
    n_images = len(images)
    
    # Determine grid size if not provided
    if grid_size is None:
        cols = min(4, n_images)
        rows = (n_images + cols - 1) // cols  # Ceiling division
    else:
        rows, cols = grid_size
    
    # Get maximum dimensions
    max_h = max([img.shape[0] for img in images])
    max_w = max([img.shape[1] for img in images])
    
    # Create empty composite image
    if images[0].shape[2] == 4:  # RGBA
        composite = np.zeros((rows * max_h, cols * max_w, 4), dtype=np.uint8)
    else:  # RGB/BGR
        composite = np.ones((rows * max_h, cols * max_w, 3), dtype=np.uint8) * 255
    
    # Place images in the grid
    for i, img in enumerate(images):
        if i >= rows * cols:
            break
            
        row = i // cols
        col = i % cols
        
        # Calculate position
        y = row * max_h
        x = col * max_w
        
        # Create resized image with right dimensions
        if img.shape[:2] != (max_h, max_w):
            # Center the image in the allocated space
            offset_y = (max_h - img.shape[0]) // 2
            offset_x = (max_w - img.shape[1]) // 2
            
            if img.shape[2] == 4:  # RGBA
                # For RGBA, create a transparent tile
                tile = np.zeros((max_h, max_w, 4), dtype=np.uint8)
                tile[offset_y:offset_y+img.shape[0], offset_x:offset_x+img.shape[1]] = img
            else:  # RGB/BGR
                # For RGB, create a white tile
                tile = np.ones((max_h, max_w, 3), dtype=np.uint8) * 255
                tile[offset_y:offset_y+img.shape[0], offset_x:offset_x+img.shape[1]] = img
            
            # Add title if provided
            if titles is not None and i < len(titles):
                title = titles[i]
                cv2.putText(tile, title, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                            1, (0, 0, 0), 2, cv2.LINE_AA)
            
            composite[y:y+max_h, x:x+max_w] = tile
        else:
            # If the image already has the right dimensions
            composite[y:y+max_h, x:x+max_w] = img
            
            # Add title if provided
            if titles is not None and i < len(titles):
                title = titles[i]
                cv2.putText(composite[y:y+max_h, x:x+max_w], title, 
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                            1, (0, 0, 0), 2, cv2.LINE_AA)
    
    return composite
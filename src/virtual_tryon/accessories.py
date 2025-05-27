import os
import json
import numpy as np
import cv2
from PIL import Image
import streamlit as st

class AccessoryManager:
    """Manage accessories for virtual try-on"""
    
    def __init__(self, data_dir=None):
        """
        Initialize the accessory manager
        
        Args:
            data_dir: Path to directory containing accessory data. If None,
                    use default data directory.
        """
        # Set default data directory if not provided
        if data_dir is None:
            # Get the project root directory
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_dir = os.path.join(root_dir, 'data', 'accessories')
        
        self.data_dir = data_dir
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Create default category subdirectories if they don't exist
        self.categories = ['clothing', 'jewelry', 'shoes', 'watches']
        for category in self.categories:
            category_dir = os.path.join(data_dir, category)
            os.makedirs(category_dir, exist_ok=True)
        
        # Load accessories data
        self.accessories = self._load_accessories()
    
    def get_accessories(self, category=None):
        """
        Get list of accessories, optionally filtered by category
        
        Args:
            category: Optional category filter (clothing, jewelry, etc.)
            
        Returns:
            List of accessory items
        """
        if category is not None:
            if category in self.accessories:
                return self.accessories[category]
            else:
                return []
        
        # If no category specified, return all accessories
        all_accessories = []
        for cat in self.accessories:
            all_accessories.extend(self.accessories[cat])
        
        return all_accessories
    
    def get_accessory(self, category, name):
        """
        Get a specific accessory by category and name
        
        Args:
            category: Accessory category (clothing, jewelry, etc.)
            name: Name of the accessory
            
        Returns:
            Accessory data or None if not found
        """
        if category in self.accessories:
            for item in self.accessories[category]:
                if item['name'] == name:
                    # Load the accessory mask if it's not already loaded
                    if 'mask' not in item and 'mask_path' in item:
                        try:
                            mask_path = os.path.join(self.data_dir, category, item['mask_path'])
                            if os.path.exists(mask_path):
                                item['mask'] = cv2.imread(mask_path, cv2.IMREAD_UNCHANGED)
                        except Exception as e:
                            st.warning(f"Failed to load accessory mask: {e}")
                    
                    # Load the accessory image if it's not already loaded
                    if 'image' not in item and 'image_path' in item:
                        try:
                            image_path = os.path.join(self.data_dir, category, item['image_path'])
                            if os.path.exists(image_path):
                                item['image'] = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
                        except Exception as e:
                            st.warning(f"Failed to load accessory image: {e}")
                    
                    return item
        
        # If not found, create a placeholder accessory
        return self._create_placeholder_accessory(category, name)
    
    def _load_accessories(self):
        """
        Load accessories from the data directory
        
        Returns:
            Dictionary of accessories by category
        """
        accessories_by_category = {}
        
        # For demonstration purposes, create placeholder accessories
        for category in self.categories:
            accessories_by_category[category] = self._create_placeholder_accessories(category)
        
        return accessories_by_category
    
    def _create_placeholder_accessories(self, category):
        """Create placeholder accessories for demonstration purposes"""
        placeholders = []
        
        if category == 'clothing':
            items = [
                {'name': 'Casual T-Shirt', 'color': 'blue'},
                {'name': 'Formal Shirt', 'color': 'white'},
                {'name': 'Dress', 'color': 'red'},
                {'name': 'Suit', 'color': 'black'},
                {'name': 'Sweater', 'color': 'gray'},
                {'name': 'Hoodie', 'color': 'navy'}
            ]
        elif category == 'jewelry':
            items = [
                {'name': 'Gold Necklace', 'color': 'gold'},
                {'name': 'Silver Earrings', 'color': 'silver'},
                {'name': 'Diamond Ring', 'color': 'diamond'},
                {'name': 'Pearl Bracelet', 'color': 'pearl'},
                {'name': 'Ruby Pendant', 'color': 'ruby'}
            ]
        elif category == 'shoes':
            items = [
                {'name': 'Sneakers', 'color': 'white'},
                {'name': 'Dress Shoes', 'color': 'black'},
                {'name': 'Boots', 'color': 'brown'},
                {'name': 'Sandals', 'color': 'beige'},
                {'name': 'High Heels', 'color': 'red'}
            ]
        elif category == 'watches':
            items = [
                {'name': 'Smart Watch', 'color': 'black'},
                {'name': 'Luxury Watch', 'color': 'gold'},
                {'name': 'Sport Watch', 'color': 'orange'},
                {'name': 'Classic Watch', 'color': 'brown'}
            ]
        else:
            items = [{'name': f'Placeholder {i}', 'color': 'gray'} for i in range(3)]
        
        for item in items:
            placeholder = {
                'name': item['name'],
                'category': category,
                'description': f"A placeholder {item['name']} for demonstration",
                'color': item['color'],
                'image_placeholder_color': self._name_to_color(item['name']),
                'type': 'placeholder'
            }
            placeholders.append(placeholder)
        
        return placeholders
    
    def _create_placeholder_accessory(self, category, name):
        """
        Create a placeholder accessory with the given category and name
        
        Args:
            category: Accessory category
            name: Accessory name
            
        Returns:
            Placeholder accessory dictionary
        """
        color = self._name_to_color(name)
        
        placeholder = {
            'name': name,
            'category': category,
            'description': f"A placeholder {name} for demonstration",
            'color': color,
            'type': 'placeholder'
        }
        
        # Generate a placeholder image for the accessory
        if category == 'clothing':
            placeholder['image'] = self._create_clothing_image(color)
            placeholder['mask'] = self._create_clothing_mask()
            placeholder['position'] = 'body'
        elif category == 'jewelry':
            placeholder['image'] = self._create_jewelry_image(color)
            placeholder['mask'] = self._create_jewelry_mask()
            placeholder['position'] = 'neck'
        elif category == 'shoes':
            placeholder['image'] = self._create_shoes_image(color)
            placeholder['mask'] = self._create_shoes_mask()
            placeholder['position'] = 'feet'
        elif category == 'watches':
            placeholder['image'] = self._create_watch_image(color)
            placeholder['mask'] = self._create_watch_mask()
            placeholder['position'] = 'wrist'
        
        return placeholder
    
    def _name_to_color(self, name):
        """
        Convert a name to a color for visualization
        
        Args:
            name: Name to convert to color
            
        Returns:
            RGB color tuple
        """
        # Use a hash of the name to generate a color
        hash_value = hash(name)
        r = (hash_value & 0xFF0000) >> 16
        g = (hash_value & 0x00FF00) >> 8
        b = hash_value & 0x0000FF
        
        return (r, g, b)
    
    def _create_clothing_image(self, color):
        """Create a placeholder clothing image"""
        # Generate a basic T-shirt shape
        image = np.zeros((300, 200, 4), dtype=np.uint8)
        
        # Draw a simplified t-shirt shape
        pts = np.array([[50, 50], [150, 50], [170, 100], [170, 250], [30, 250], [30, 100]], np.int32)
        pts = pts.reshape((-1, 1, 2))
        
        # Fill with the specified color
        r, g, b = color
        # Draw filled polygon
        cv2.fillPoly(image, [pts], (r, g, b, 255))
        
        return image
    
    def _create_clothing_mask(self):
        """Create a placeholder clothing mask"""
        # Generate a basic T-shirt mask
        mask = np.zeros((300, 200), dtype=np.uint8)
        
        # Draw a simplified t-shirt shape
        pts = np.array([[50, 50], [150, 50], [170, 100], [170, 250], [30, 250], [30, 100]], np.int32)
        pts = pts.reshape((-1, 1, 2))
        
        # Fill with white (255)
        cv2.fillPoly(mask, [pts], 255)
        
        return mask
    
    def _create_jewelry_image(self, color):
        """Create a placeholder jewelry image"""
        # Generate a simple necklace shape
        image = np.zeros((100, 200, 4), dtype=np.uint8)
        
        # Draw a circular pendant
        r, g, b = color
        cv2.circle(image, (100, 60), 20, (r, g, b, 255), -1)
        
        # Draw a chain
        cv2.ellipse(image, (100, 30), (80, 30), 0, 0, 180, (r, g, b, 255), 2)
        
        return image
    
    def _create_jewelry_mask(self):
        """Create a placeholder jewelry mask"""
        # Generate a simple necklace mask
        mask = np.zeros((100, 200), dtype=np.uint8)
        
        # Draw a circular pendant
        cv2.circle(mask, (100, 60), 20, 255, -1)
        
        # Draw a chain
        cv2.ellipse(mask, (100, 30), (80, 30), 0, 0, 180, 255, 2)
        
        return mask
    
    def _create_shoes_image(self, color):
        """Create a placeholder shoes image"""
        # Generate a simple shoe shape
        image = np.zeros((100, 200, 4), dtype=np.uint8)
        
        # Draw a simplified shoe shape
        pts = np.array([[50, 50], [150, 50], [180, 70], [180, 90], [30, 90], [30, 70]], np.int32)
        pts = pts.reshape((-1, 1, 2))
        
        # Fill with the specified color
        r, g, b = color
        cv2.fillPoly(image, [pts], (r, g, b, 255))
        
        return image
    
    def _create_shoes_mask(self):
        """Create a placeholder shoes mask"""
        # Generate a simple shoe mask
        mask = np.zeros((100, 200), dtype=np.uint8)
        
        # Draw a simplified shoe shape
        pts = np.array([[50, 50], [150, 50], [180, 70], [180, 90], [30, 90], [30, 70]], np.int32)
        pts = pts.reshape((-1, 1, 2))
        
        # Fill with white (255)
        cv2.fillPoly(mask, [pts], 255)
        
        return mask
    
    def _create_watch_image(self, color):
        """Create a placeholder watch image"""
        # Generate a simple watch shape
        image = np.zeros((100, 100, 4), dtype=np.uint8)
        
        # Draw watch face
        r, g, b = color
        cv2.circle(image, (50, 50), 30, (r, g, b, 255), -1)
        cv2.circle(image, (50, 50), 30, (r//2, g//2, b//2, 255), 2)
        
        # Draw watch band
        cv2.rectangle(image, (40, 20), (60, 10), (r, g, b, 255), -1)
        cv2.rectangle(image, (40, 80), (60, 90), (r, g, b, 255), -1)
        
        return image
    
    def _create_watch_mask(self):
        """Create a placeholder watch mask"""
        # Generate a simple watch mask
        mask = np.zeros((100, 100), dtype=np.uint8)
        
        # Draw watch face
        cv2.circle(mask, (50, 50), 30, 255, -1)
        
        # Draw watch band
        cv2.rectangle(mask, (40, 20), (60, 10), 255, -1)
        cv2.rectangle(mask, (40, 80), (60, 90), 255, -1)
        
        return mask
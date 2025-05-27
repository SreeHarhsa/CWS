/**
 * Accessory Manager for Chroma Wave Studios
 * Handles accessory loading, management, and fitting
 */
class AccessoryManager {
    constructor() {
        // Accessory state
        this.categories = CONFIG.accessoryCategories || [];
        this.accessories = {};
        this.selectedAccessories = {};
        this.stylePresets = [];
        
        // Initialize
        this.init();
    }
    
    /**
     * Initialize the accessory manager
     */
    async init() {
        try {
            // Load accessory data
            await this.loadAccessories();
            
            console.log('Accessory manager initialized');
        } catch (error) {
            console.error('Error initializing accessory manager:', error);
        }
    }
    
    /**
     * Load all accessories from the server
     */
    async loadAccessories() {
        // In a real app, this would fetch from an API
        // For the demo, we'll use the sample data from config
        if (CONFIG.demoMode.enabled && CONFIG.demoMode.sampleAccessories) {
            // Convert sample data to our internal format
            for (const categoryId in CONFIG.demoMode.sampleAccessories) {
                this.accessories[categoryId] = CONFIG.demoMode.sampleAccessories[categoryId].map(item => ({
                    id: item.id,
                    name: item.name,
                    category: categoryId,
                    image: item.image,
                    thumbnail: item.thumbnail,
                    // Add additional properties
                    price: item.price || 'Free',
                    description: item.description || `Sample ${item.name}`,
                    position: this.getCategoryPosition(categoryId),
                    type: 'demo'
                }));
            }
        }
    }
    
    /**
     * Get all accessories for a specific category
     * @param {string} categoryId - Category ID
     * @returns {Array} - Accessories in the category
     */
    getAccessoriesByCategory(categoryId) {
        return this.accessories[categoryId] || [];
    }
    
    /**
     * Get a specific accessory by ID
     * @param {string} accessoryId - Accessory ID
     * @returns {Object|null} - Accessory object or null if not found
     */
    getAccessoryById(accessoryId) {
        for (const categoryId in this.accessories) {
            const found = this.accessories[categoryId].find(acc => acc.id === accessoryId);
            if (found) return found;
        }
        return null;
    }
    
    /**
     * Get accessories by category and set the context for the avatar
     * @param {string} categoryId - Category ID
     * @param {HTMLElement} container - Container element to populate
     * @param {Function} onSelect - Callback when an accessory is selected
     */
    populateAccessoryGallery(categoryId, container, onSelect) {
        if (!container) return;
        
        // Clear the container
        container.innerHTML = '';
        
        // Get accessories for the category
        const accessories = this.getAccessoriesByCategory(categoryId);
        
        if (accessories.length === 0) {
            // No accessories found
            container.innerHTML = `
                <div class="empty-gallery">
                    <i class="fas fa-search"></i>
                    <p>No accessories available for this category</p>
                </div>
            `;
            return;
        }
        
        // Create gallery items
        accessories.forEach(accessory => {
            const item = document.createElement('div');
            item.className = 'gallery-item';
            item.dataset.id = accessory.id;
            
            // Check if this accessory is currently selected
            if (this.selectedAccessories[categoryId] === accessory.id) {
                item.classList.add('active');
            }
            
            // Create accessory content
            item.innerHTML = `
                <img src="${accessory.thumbnail || 'assets/images/placeholder-accessory.png'}" alt="${accessory.name}">
                <div class="gallery-item-info">
                    <span>${accessory.name}</span>
                </div>
            `;
            
            // Add click event
            item.addEventListener('click', () => {
                // Update selection
                this.selectAccessory(categoryId, accessory.id);
                
                // Update UI
                document.querySelectorAll(`.gallery-item`).forEach(el => {
                    if (el.dataset.id === accessory.id) {
                        el.classList.add('active');
                    } else if (el.closest('.gallery-items') === container) {
                        el.classList.remove('active');
                    }
                });
                
                // Call selection callback
                if (typeof onSelect === 'function') {
                    onSelect(categoryId, accessory);
                }
            });
            
            // Add to gallery
            container.appendChild(item);
        });
    }
    
    /**
     * Select an accessory for a category
     * @param {string} categoryId - Category ID
     * @param {string} accessoryId - Accessory ID
     */
    selectAccessory(categoryId, accessoryId) {
        // Update selection state
        this.selectedAccessories[categoryId] = accessoryId;
        
        // In a real app, this would apply the accessory to the avatar
        // through the avatar generator
        const accessory = this.getAccessoryById(accessoryId);
        
        if (accessory && window.avatarGenerator) {
            window.avatarGenerator.applyAccessory(categoryId, accessory)
                .then(updatedImageUrl => {
                    // Update avatar display
                    const avatarImg = document.getElementById('accessorized-avatar');
                    if (avatarImg) {
                        avatarImg.src = updatedImageUrl;
                    }
                });
        }
    }
    
    /**
     * Remove an accessory from the selected set
     * @param {string} categoryId - Category ID
     */
    removeAccessory(categoryId) {
        // Remove from selected accessories
        delete this.selectedAccessories[categoryId];
        
        // Update UI
        document.querySelectorAll(`.gallery-item`).forEach(item => {
            if (document.querySelector(`.category-btn[data-category="${categoryId}"]`) && 
                document.querySelector(`.category-btn[data-category="${categoryId}"]`).classList.contains('active')) {
                item.classList.remove('active');
            }
        });
        
        // Remove accessory from avatar
        if (window.avatarGenerator) {
            window.avatarGenerator.removeAccessory(categoryId)
                .then(updatedImageUrl => {
                    // Update avatar display
                    const avatarImg = document.getElementById('accessorized-avatar');
                    if (avatarImg) {
                        avatarImg.src = updatedImageUrl;
                    }
                });
        }
    }
    
    /**
     * Clear all selected accessories
     */
    clearAllAccessories() {
        // Clear selected accessories
        this.selectedAccessories = {};
        
        // Remove active state from all gallery items
        document.querySelectorAll('.gallery-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Clear accessories from avatar
        if (window.avatarGenerator) {
            window.avatarGenerator.clearAllAccessories()
                .then(originalImageUrl => {
                    // Update avatar display
                    const avatarImg = document.getElementById('accessorized-avatar');
                    if (avatarImg) {
                        avatarImg.src = originalImageUrl;
                    }
                });
        }
    }
    
    /**
     * Get all currently selected accessories
     * @returns {Object} - Map of category IDs to accessory IDs
     */
    getSelectedAccessories() {
        return { ...this.selectedAccessories };
    }
    
    /**
     * Get a list of selected accessory objects
     * @returns {Array} - Array of selected accessory objects
     */
    getSelectedAccessoryObjects() {
        const result = [];
        
        for (const categoryId in this.selectedAccessories) {
            const accessoryId = this.selectedAccessories[categoryId];
            const accessory = this.getAccessoryById(accessoryId);
            if (accessory) {
                result.push(accessory);
            }
        }
        
        return result;
    }
    
    /**
     * Update outfit list in the UI
     */
    updateOutfitList() {
        const outfitList = document.getElementById('outfit-list');
        if (!outfitList) return;
        
        // Clear existing list
        outfitList.innerHTML = '';
        
        // Check if any accessories are selected
        const hasAccessories = Object.keys(this.selectedAccessories).length > 0;
        
        if (hasAccessories) {
            // Create list items for each selected accessory
            Object.entries(this.selectedAccessories).forEach(([categoryId, accessoryId]) => {
                const category = this.categories.find(cat => cat.id === categoryId);
                const accessory = this.getAccessoryById(accessoryId);
                
                if (category && accessory) {
                    const listItem = document.createElement('li');
                    listItem.innerHTML = `
                        <span><i class="fas ${category.icon}"></i> ${accessory.name}</span>
                        <button class="remove-accessory-btn" data-category="${categoryId}">
                            <i class="fas fa-times"></i>
                        </button>
                    `;
                    
                    // Add event listener to remove button
                    listItem.querySelector('.remove-accessory-btn').addEventListener('click', () => {
                        this.removeAccessory(categoryId);
                        this.updateOutfitList();
                    });
                    
                    outfitList.appendChild(listItem);
                }
            });
        } else {
            // Show empty state
            outfitList.innerHTML = `
                <li class="empty-outfit">No accessories selected yet</li>
            `;
        }
    }
    
    /**
     * Apply a predefined style preset with multiple accessories
     * @param {string} presetId - Style preset ID
     */
    applyStylePreset(presetId) {
        const preset = this.stylePresets.find(p => p.id === presetId);
        
        if (!preset) return;
        
        // Clear current accessories
        this.clearAllAccessories();
        
        // Apply each accessory in the preset
        for (const categoryId in preset.accessories) {
            const accessoryId = preset.accessories[categoryId];
            this.selectAccessory(categoryId, accessoryId);
        }
        
        // Update UI
        this.updateOutfitList();
    }
    
    /**
     * Get the appropriate position for an accessory category
     * @param {string} categoryId - Category ID
     * @returns {string} - Position identifier
     */
    getCategoryPosition(categoryId) {
        // Map categories to positions
        const positionMap = {
            'clothing': 'body',
            'jewelry': 'neck',
            'shoes': 'feet',
            'watches': 'wrist'
        };
        
        return positionMap[categoryId] || 'body';
    }
}

// Initialize Accessory Manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Create instance and expose to window for debugging
    window.accessoryManager = new AccessoryManager();
});
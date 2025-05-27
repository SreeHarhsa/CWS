/**
 * Looks Manager for Chroma Wave Studios
 * Handles managing, saving, and loading custom looks
 */
class LooksManager {
    constructor() {
        // Saved looks
        this.looks = [];
        
        // Load saved looks
        this.loadSavedLooks();
        
        // Bind methods
        this.saveLook = this.saveLook.bind(this);
        this.deleteLook = this.deleteLook.bind(this);
        this.loadLook = this.loadLook.bind(this);
        
        // Initialize event listeners
        this.initEventListeners();
    }
    
    /**
     * Initialize event listeners
     */
    initEventListeners() {
        // Confirm save look button
        const confirmSaveButton = document.getElementById('confirm-save-look-btn');
        if (confirmSaveButton) {
            confirmSaveButton.addEventListener('click', () => {
                this.saveLook();
            });
        }
        
        // Search and sort functionality for the looks grid
        const searchInput = document.getElementById('search-looks');
        if (searchInput) {
            searchInput.addEventListener('input', () => this.filterLooks(searchInput.value));
        }
        
        const sortSelect = document.getElementById('sort-looks');
        if (sortSelect) {
            sortSelect.addEventListener('change', () => this.sortLooks(sortSelect.value));
        }
    }
    
    /**
     * Load saved looks from local storage
     */
    loadSavedLooks() {
        try {
            // Get from local storage
            const savedLooks = localStorage.getItem(CONFIG.storageKeys.savedLooks);
            
            if (savedLooks) {
                this.looks = JSON.parse(savedLooks);
            } else {
                this.looks = [];
            }
            
            // Update the UI
            this.updateLooksGrid();
        } catch (error) {
            console.error('Error loading saved looks:', error);
            this.looks = [];
        }
    }
    
    /**
     * Update the looks grid in the UI
     */
    updateLooksGrid() {
        const looksGrid = document.getElementById('looks-grid');
        const noLooksMessage = document.getElementById('no-looks-message');
        
        if (!looksGrid) return;
        
        // Clear existing content
        looksGrid.innerHTML = '';
        
        if (this.looks.length > 0) {
            // Hide no looks message
            if (noLooksMessage) {
                noLooksMessage.style.display = 'none';
            }
            
            // Create look cards
            this.looks.forEach(look => {
                const dateObj = new Date(look.date);
                const formattedDate = dateObj.toLocaleDateString(undefined, {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                });
                
                const card = document.createElement('div');
                card.className = 'look-card';
                card.dataset.id = look.id;
                
                card.innerHTML = `
                    <img src="${look.image || 'assets/images/placeholder-look.png'}" alt="${look.name}" class="look-image">
                    <div class="look-info">
                        <h4>${look.name}</h4>
                        <div class="look-date">${formattedDate}</div>
                        <p>${look.notes || ''}</p>
                        <div class="look-actions">
                            <button class="secondary-btn view-look-btn">View</button>
                            <button class="secondary-btn delete-look-btn">Delete</button>
                        </div>
                    </div>
                `;
                
                // Add event listeners
                card.querySelector('.view-look-btn').addEventListener('click', () => {
                    this.loadLook(look.id);
                });
                
                card.querySelector('.delete-look-btn').addEventListener('click', () => {
                    this.deleteLook(look.id);
                });
                
                looksGrid.appendChild(card);
            });
        } else {
            // Show no looks message
            if (noLooksMessage) {
                noLooksMessage.style.display = 'flex';
            }
        }
    }
    
    /**
     * Save a new look
     */
    saveLook() {
        const nameInput = document.getElementById('look-name');
        const notesInput = document.getElementById('look-notes');
        
        if (!nameInput || !nameInput.value.trim()) {
            alert('Please enter a name for your look');
            return;
        }
        
        // Get the current accessorized avatar
        const avatarImage = document.getElementById('accessorized-avatar');
        if (!avatarImage || !avatarImage.src) {
            alert('Please create an avatar first');
            return;
        }
        
        // Get the selected accessories
        const selectedAccessories = window.accessoryManager ? 
            window.accessoryManager.getSelectedAccessories() : 
            {};
        
        // Create look object
        const look = {
            id: Date.now().toString(),
            name: nameInput.value.trim(),
            notes: notesInput ? notesInput.value.trim() : '',
            date: new Date().toISOString(),
            image: avatarImage.src,
            accessories: selectedAccessories
        };
        
        // Add to the list
        this.looks.push(look);
        
        // Save to local storage
        this.saveLooksToStorage();
        
        // Update UI
        this.updateLooksGrid();
        
        // Close the modal
        const modal = document.getElementById('save-look-modal');
        if (modal) {
            modal.classList.remove('active');
        }
        
        // Reset form
        nameInput.value = '';
        if (notesInput) {
            notesInput.value = '';
        }
        
        // Navigate to My Looks section
        if (window.uiManager) {
            window.uiManager.navigateToSection('my-looks');
        }
    }
    
    /**
     * Load a saved look
     * @param {string} lookId - ID of the look to load
     */
    loadLook(lookId) {
        // Find the look
        const look = this.looks.find(l => l.id === lookId);
        
        if (!look) return;
        
        // Set the avatar image
        const avatarImage = document.getElementById('accessorized-avatar');
        if (avatarImage && look.image) {
            avatarImage.src = look.image;
        }
        
        // Set the selected accessories
        if (window.accessoryManager) {
            // First clear all accessories
            window.accessoryManager.clearAllAccessories();
            
            // Then apply each one
            for (const categoryId in look.accessories) {
                window.accessoryManager.selectAccessory(categoryId, look.accessories[categoryId]);
            }
            
            // Update the outfit list
            window.accessoryManager.updateOutfitList();
        }
        
        // Save as current avatar
        localStorage.setItem(CONFIG.storageKeys.currentAvatar, look.image);
        
        // Navigate to accessory gallery
        if (window.uiManager) {
            window.uiManager.navigateToSection('accessory-gallery');
        }
    }
    
    /**
     * Delete a saved look
     * @param {string} lookId - ID of the look to delete
     */
    deleteLook(lookId) {
        // Confirm deletion
        if (confirm('Are you sure you want to delete this look?')) {
            // Remove the look
            this.looks = this.looks.filter(look => look.id !== lookId);
            
            // Save to local storage
            this.saveLooksToStorage();
            
            // Update UI
            this.updateLooksGrid();
        }
    }
    
    /**
     * Search and filter looks
     * @param {string} query - Search query
     */
    filterLooks(query) {
        if (!query) {
            // No filter
            this.updateLooksGrid();
            return;
        }
        
        query = query.toLowerCase();
        
        // Filter the looks that match the query
        const filteredLooks = this.looks.filter(look => {
            return (
                look.name.toLowerCase().includes(query) ||
                (look.notes && look.notes.toLowerCase().includes(query))
            );
        });
        
        // Update the grid with filtered looks
        const looksGrid = document.getElementById('looks-grid');
        const noLooksMessage = document.getElementById('no-looks-message');
        
        if (!looksGrid) return;
        
        // Clear existing content
        looksGrid.innerHTML = '';
        
        if (filteredLooks.length > 0) {
            // Hide no looks message
            if (noLooksMessage) {
                noLooksMessage.style.display = 'none';
            }
            
            // Create look cards for filtered results
            filteredLooks.forEach(look => {
                // Same card creation logic as updateLooksGrid
                const dateObj = new Date(look.date);
                const formattedDate = dateObj.toLocaleDateString(undefined, {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                });
                
                const card = document.createElement('div');
                card.className = 'look-card';
                card.dataset.id = look.id;
                
                card.innerHTML = `
                    <img src="${look.image || 'assets/images/placeholder-look.png'}" alt="${look.name}" class="look-image">
                    <div class="look-info">
                        <h4>${look.name}</h4>
                        <div class="look-date">${formattedDate}</div>
                        <p>${look.notes || ''}</p>
                        <div class="look-actions">
                            <button class="secondary-btn view-look-btn">View</button>
                            <button class="secondary-btn delete-look-btn">Delete</button>
                        </div>
                    </div>
                `;
                
                // Add event listeners
                card.querySelector('.view-look-btn').addEventListener('click', () => {
                    this.loadLook(look.id);
                });
                
                card.querySelector('.delete-look-btn').addEventListener('click', () => {
                    this.deleteLook(look.id);
                });
                
                looksGrid.appendChild(card);
            });
        } else {
            // Show no results message
            looksGrid.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-search"></i>
                    <p>No looks matching "${query}" found</p>
                </div>
            `;
        }
    }
    
    /**
     * Sort looks by criteria
     * @param {string} sortBy - Sort criteria
     */
    sortLooks(sortBy) {
        // Sort the looks array
        switch (sortBy) {
            case 'newest':
                this.looks.sort((a, b) => new Date(b.date) - new Date(a.date));
                break;
            case 'oldest':
                this.looks.sort((a, b) => new Date(a.date) - new Date(b.date));
                break;
            case 'name':
                this.looks.sort((a, b) => a.name.localeCompare(b.name));
                break;
            default:
                // Default to newest
                this.looks.sort((a, b) => new Date(b.date) - new Date(a.date));
        }
        
        // Update the UI
        this.updateLooksGrid();
    }
    
    /**
     * Save the looks array to local storage
     */
    saveLooksToStorage() {
        try {
            localStorage.setItem(CONFIG.storageKeys.savedLooks, JSON.stringify(this.looks));
        } catch (error) {
            console.error('Error saving looks to local storage:', error);
            
            // If localStorage is full, clean up some space
            if (error.name === 'QuotaExceededError') {
                alert('Storage is full. Please delete some looks to make space for new ones.');
            }
        }
    }
    
    /**
     * Export looks as a JSON file
     */
    exportLooks() {
        try {
            const data = JSON.stringify(this.looks, null, 2);
            const blob = new Blob([data], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `cws-looks-${Date.now()}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Error exporting looks:', error);
            alert('Error exporting looks: ' + error.message);
        }
    }
    
    /**
     * Import looks from a JSON file
     * @param {File} file - The JSON file to import
     */
    importLooks(file) {
        if (!file) return;
        
        const reader = new FileReader();
        
        reader.onload = (e) => {
            try {
                const importedLooks = JSON.parse(e.target.result);
                
                // Validate the imported data
                if (!Array.isArray(importedLooks)) {
                    throw new Error('Invalid format: Expected an array of looks');
                }
                
                // Check if each look has required properties
                for (const look of importedLooks) {
                    if (!look.id || !look.name || !look.date) {
                        throw new Error('Invalid look data: Missing required properties');
                    }
                }
                
                // Ask user if they want to replace or merge
                const confirmImport = confirm(
                    `Import ${importedLooks.length} looks? This will ${this.looks.length > 0 ? 'merge them with' : 'add them to'} your existing collection.`
                );
                
                if (confirmImport) {
                    // Merge with existing looks
                    // Use a Map to ensure unique IDs
                    const looksMap = new Map();
                    
                    // Add existing looks to map
                    this.looks.forEach(look => {
                        looksMap.set(look.id, look);
                    });
                    
                    // Add imported looks (will override if ID already exists)
                    importedLooks.forEach(look => {
                        looksMap.set(look.id, look);
                    });
                    
                    // Convert map back to array
                    this.looks = Array.from(looksMap.values());
                    
                    // Save to storage
                    this.saveLooksToStorage();
                    
                    // Update UI
                    this.updateLooksGrid();
                    
                    alert(`Successfully imported ${importedLooks.length} looks.`);
                }
            } catch (error) {
                console.error('Error importing looks:', error);
                alert('Error importing looks: ' + error.message);
            }
        };
        
        reader.onerror = () => {
            alert('Error reading file');
        };
        
        reader.readAsText(file);
    }
}

// Initialize Looks Manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Create instance and expose to window for debugging
    window.looksManager = new LooksManager();
});
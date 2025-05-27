/**
 * UI Manager for Chroma Wave Studios
 * Handles UI interactions, navigation, and state management
 */
class UIManager {
    constructor() {
        // Initialize UI state
        this.currentSection = 'avatar-creator';
        this.activeTab = 'camera-tab';
        this.activeCategory = 'clothing';
        this.selectedAccessories = {};
        this.themePreference = localStorage.getItem(CONFIG.storageKeys.theme) || 'light';
        
        // Apply saved theme
        this.applyTheme(this.themePreference);
        
        // Bind event handlers
        this.bindEvents();
        
        // Initialize UI components
        this.initializeTabs();
        this.initializeThemeToggle();
    }
    
    /**
     * Bind all event listeners
     */
    bindEvents() {
        // Navigation menu links
        document.querySelectorAll('.header-nav a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const sectionId = link.getAttribute('data-section');
                this.navigateToSection(sectionId);
            });
        });
        
        // Tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const tabId = btn.getAttribute('data-tab');
                this.switchTab(tabId);
            });
        });
        
        // Category buttons
        document.querySelectorAll('.category-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const categoryId = btn.getAttribute('data-category');
                this.switchCategory(categoryId);
            });
        });
        
        // File upload handling
        const uploadArea = document.getElementById('upload-area');
        const fileInput = document.getElementById('file-upload');
        
        if (uploadArea && fileInput) {
            // Drag and drop events
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('drag-over');
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('drag-over');
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('drag-over');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.handleFileUpload(files[0]);
                }
            });
            
            // Click to upload
            uploadArea.addEventListener('click', () => {
                fileInput.click();
            });
            
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    this.handleFileUpload(e.target.files[0]);
                }
            });
        }
        
        // Change image button
        const changeImageBtn = document.getElementById('change-image-btn');
        if (changeImageBtn) {
            changeImageBtn.addEventListener('click', () => {
                // Reset the upload area
                document.getElementById('uploaded-image-preview').style.display = 'none';
                document.getElementById('upload-area').style.display = 'flex';
                document.getElementById('file-upload').value = '';
                
                // Disable generate button if it's enabled
                const generateBtn = document.getElementById('generate-avatar-btn');
                if (generateBtn) {
                    generateBtn.disabled = true;
                }
            });
        }
        
        // Avatar generation button
        const generateAvatarBtn = document.getElementById('generate-avatar-btn');
        if (generateAvatarBtn) {
            generateAvatarBtn.addEventListener('click', () => {
                // Simulate avatar generation
                this.showProcessingModal();
                
                // In a real app, this would call the avatar generation service
                setTimeout(() => {
                    this.hideProcessingModal();
                    this.displayAvatar('assets/images/sample-avatar.png');
                }, 10000);
            });
        }
        
        // Continue to accessories button
        const continueBtn = document.getElementById('continue-to-accessories-btn');
        if (continueBtn) {
            continueBtn.addEventListener('click', () => {
                // Navigate to accessories section
                this.navigateToSection('accessory-gallery');
            });
        }
        
        // Clear accessories button
        const clearAccessoriesBtn = document.getElementById('clear-accessories-btn');
        if (clearAccessoriesBtn) {
            clearAccessoriesBtn.addEventListener('click', () => {
                this.clearAccessories();
            });
        }
        
        // Save look button
        const saveLookBtn = document.getElementById('save-look-btn');
        if (saveLookBtn) {
            saveLookBtn.addEventListener('click', () => {
                this.showSaveLookModal();
            });
        }
        
        // Confirm save look button
        const confirmSaveLookBtn = document.getElementById('confirm-save-look-btn');
        if (confirmSaveLookBtn) {
            confirmSaveLookBtn.addEventListener('click', () => {
                this.saveLook();
            });
        }
        
        // Close modal buttons
        document.querySelectorAll('.close-modal').forEach(btn => {
            btn.addEventListener('click', () => {
                this.closeAllModals();
            });
        });
        
        // Download image button
        const downloadImageBtn = document.getElementById('download-image-btn');
        if (downloadImageBtn) {
            downloadImageBtn.addEventListener('click', () => {
                this.downloadCurrentLook();
            });
        }
    }
    
    /**
     * Initialize tab functionality
     */
    initializeTabs() {
        // Set the initial active tab
        this.switchTab(this.activeTab);
    }
    
    /**
     * Initialize theme toggle functionality
     */
    initializeThemeToggle() {
        const themeToggle = document.getElementById('theme-toggle');
        
        // Set initial state based on saved preference
        if (themeToggle) {
            themeToggle.checked = this.themePreference === 'dark';
            
            // Theme toggle event
            themeToggle.addEventListener('change', () => {
                const newTheme = themeToggle.checked ? 'dark' : 'light';
                this.applyTheme(newTheme);
                localStorage.setItem(CONFIG.storageKeys.theme, newTheme);
            });
        }
    }
    
    /**
     * Navigate to a different section
     * @param {string} sectionId - The ID of the section to navigate to
     */
    navigateToSection(sectionId) {
        // Hide all sections
        document.querySelectorAll('.app-section').forEach(section => {
            section.classList.remove('active');
        });
        
        // Show the target section
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.add('active');
            
            // Update navigation links
            document.querySelectorAll('.header-nav a').forEach(link => {
                if (link.getAttribute('data-section') === sectionId) {
                    link.classList.add('active');
                } else {
                    link.classList.remove('active');
                }
            });
            
            // Update current section
            this.currentSection = sectionId;
            
            // Perform any section-specific initialization
            if (sectionId === 'accessory-gallery') {
                this.initializeAccessoryGallery();
            } else if (sectionId === 'my-looks') {
                this.loadSavedLooks();
            }
        }
    }
    
    /**
     * Switch between tabs in the avatar creator
     * @param {string} tabId - The ID of the tab to switch to
     */
    switchTab(tabId) {
        // Hide all tab content
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // Show the target tab content
        const targetTab = document.getElementById(tabId);
        if (targetTab) {
            targetTab.classList.add('active');
        }
        
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            if (btn.getAttribute('data-tab') === tabId) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        
        // Update active tab
        this.activeTab = tabId;
        
        // Special handling for camera tab
        if (tabId === 'camera-tab') {
            // Initialize camera in real implementation
            // This would call cameraManager.startCamera()
        }
    }
    
    /**
     * Switch between accessory categories
     * @param {string} categoryId - The ID of the category to switch to
     */
    switchCategory(categoryId) {
        // Update category buttons
        document.querySelectorAll('.category-btn').forEach(btn => {
            if (btn.getAttribute('data-category') === categoryId) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        
        // Update active category
        this.activeCategory = categoryId;
        
        // Load accessories for the selected category
        this.loadAccessories(categoryId);
    }
    
    /**
     * Handle file upload for avatar creation
     * @param {File} file - The uploaded file
     */
    handleFileUpload(file) {
        // Check file type
        if (!file.type.match('image.*')) {
            alert('Please upload an image file.');
            return;
        }
        
        // Check file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            alert('File size must be less than 10MB.');
            return;
        }
        
        // Create a FileReader to read the file
        const reader = new FileReader();
        
        reader.onload = (e) => {
            // Display the uploaded image
            const previewImg = document.getElementById('preview-img');
            const uploadedPreview = document.getElementById('uploaded-image-preview');
            const uploadArea = document.getElementById('upload-area');
            
            if (previewImg && uploadedPreview && uploadArea) {
                previewImg.src = e.target.result;
                uploadArea.style.display = 'none';
                uploadedPreview.style.display = 'block';
                
                // Enable generate button
                const generateBtn = document.getElementById('generate-avatar-btn');
                if (generateBtn) {
                    generateBtn.disabled = false;
                }
            }
        };
        
        // Read the file as a data URL
        reader.readAsDataURL(file);
    }
    
    /**
     * Show the processing modal with animated progress
     */
    showProcessingModal() {
        const modal = document.getElementById('processing-modal');
        if (modal) {
            modal.classList.add('active');
            
            // Simulate processing stages
            this.simulateProcessingStages();
        }
    }
    
    /**
     * Hide the processing modal
     */
    hideProcessingModal() {
        const modal = document.getElementById('processing-modal');
        if (modal) {
            modal.classList.remove('active');
        }
    }
    
    /**
     * Simulate processing stages with progress updates
     */
    simulateProcessingStages() {
        const stages = CONFIG.avatarGeneration.processingStages;
        const progressBar = document.getElementById('processing-progress');
        const stageText = document.getElementById('processing-stage');
        
        if (!progressBar || !stageText) return;
        
        // Reset progress
        progressBar.style.width = '0%';
        
        // Calculate total duration
        const totalDuration = stages.reduce((sum, stage) => sum + stage.duration, 0);
        let elapsedTime = 0;
        
        // Process each stage sequentially
        stages.forEach((stage, index) => {
            setTimeout(() => {
                // Update stage text
                stageText.textContent = stage.name;
                
                // Calculate progress percentage
                elapsedTime += stage.duration;
                const progress = Math.min((elapsedTime / totalDuration) * 100, 100);
                
                // Update progress bar
                progressBar.style.width = `${progress}%`;
            }, elapsedTime);
        });
    }
    
    /**
     * Display the generated avatar
     * @param {string} avatarUrl - URL of the avatar image
     */
    displayAvatar(avatarUrl) {
        const avatarResult = document.getElementById('avatar-result');
        const avatarPlaceholder = document.getElementById('avatar-placeholder');
        
        if (avatarResult && avatarPlaceholder) {
            // Display the avatar
            avatarResult.src = avatarUrl;
            avatarResult.style.display = 'block';
            avatarPlaceholder.style.display = 'none';
            
            // Save the current avatar
            if (avatarUrl) {
                localStorage.setItem(CONFIG.storageKeys.currentAvatar, avatarUrl);
            }
            
            // Enable the continue button
            const continueBtn = document.getElementById('continue-to-accessories-btn');
            if (continueBtn) {
                continueBtn.disabled = false;
            }
            
            // Also update the accessorized avatar
            const accessorizedAvatar = document.getElementById('accessorized-avatar');
            if (accessorizedAvatar) {
                accessorizedAvatar.src = avatarUrl;
            }
        }
    }
    
    /**
     * Initialize the accessory gallery with items
     */
    initializeAccessoryGallery() {
        // Load accessories for the active category
        this.loadAccessories(this.activeCategory);
        
        // Load the current avatar
        const avatarUrl = localStorage.getItem(CONFIG.storageKeys.currentAvatar);
        if (avatarUrl) {
            const accessorizedAvatar = document.getElementById('accessorized-avatar');
            if (accessorizedAvatar) {
                accessorizedAvatar.src = avatarUrl;
            }
        }
        
        // Clear the current outfit display
        this.updateOutfitList();
    }
    
    /**
     * Load accessories for a given category
     * @param {string} categoryId - Category ID to load accessories for
     */
    loadAccessories(categoryId) {
        const galleryItems = document.getElementById('gallery-items');
        if (!galleryItems) return;
        
        // Clear existing items
        galleryItems.innerHTML = '';
        
        // In a real app, this would fetch from API
        // Using demo data for this example
        if (CONFIG.demoMode.enabled && CONFIG.demoMode.sampleAccessories[categoryId]) {
            const accessories = CONFIG.demoMode.sampleAccessories[categoryId];
            
            accessories.forEach(accessory => {
                // Create accessory item element
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
                    this.selectAccessory(categoryId, accessory);
                });
                
                // Add to gallery
                galleryItems.appendChild(item);
            });
        } else {
            // Display placeholder or empty state
            galleryItems.innerHTML = `
                <div class="empty-gallery">
                    <i class="fas fa-search"></i>
                    <p>No accessories available for this category</p>
                </div>
            `;
        }
    }
    
    /**
     * Select an accessory from the gallery
     * @param {string} categoryId - Category of the accessory
     * @param {Object} accessory - The accessory object
     */
    selectAccessory(categoryId, accessory) {
        // Update selection state
        this.selectedAccessories[categoryId] = accessory.id;
        
        // Update UI to reflect selection
        document.querySelectorAll('.gallery-item').forEach(item => {
            if (item.dataset.id === accessory.id) {
                item.classList.add('active');
            } else if (item.closest('.gallery-items').contains(item) && 
                      document.querySelector(`.category-btn[data-category="${categoryId}"]`).classList.contains('active')) {
                item.classList.remove('active');
            }
        });
        
        // Apply accessory to avatar (in a real app, this would use virtual try-on)
        this.applyAccessoryToAvatar(accessory);
        
        // Update outfit list
        this.updateOutfitList();
    }
    
    /**
     * Apply an accessory to the avatar
     * @param {Object} accessory - The accessory to apply
     */
    applyAccessoryToAvatar(accessory) {
        // In a real app, this would use the avatar-generator.js to apply the accessory
        // For this demo, we'll simulate by showing a message
        console.log(`Applied ${accessory.name} to avatar`);
        
        // Save current look state
        this.saveCurrentLookState();
    }
    
    /**
     * Update the outfit list display
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
                const category = CONFIG.accessoryCategories.find(cat => cat.id === categoryId);
                const accessories = CONFIG.demoMode.sampleAccessories[categoryId] || [];
                const accessory = accessories.find(acc => acc.id === accessoryId);
                
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
     * Remove an accessory from the current outfit
     * @param {string} categoryId - Category of the accessory to remove
     */
    removeAccessory(categoryId) {
        // Remove from selected accessories
        delete this.selectedAccessories[categoryId];
        
        // Update UI
        document.querySelectorAll(`.gallery-item`).forEach(item => {
            if (document.querySelector(`.category-btn[data-category="${categoryId}"]`).classList.contains('active')) {
                item.classList.remove('active');
            }
        });
        
        // Update outfit list
        this.updateOutfitList();
        
        // Save current look state
        this.saveCurrentLookState();
    }
    
    /**
     * Clear all accessories from the current outfit
     */
    clearAccessories() {
        // Clear selected accessories
        this.selectedAccessories = {};
        
        // Remove active state from all gallery items
        document.querySelectorAll('.gallery-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Update outfit list
        this.updateOutfitList();
        
        // Reset the avatar to the original (without accessories)
        const avatarUrl = localStorage.getItem(CONFIG.storageKeys.currentAvatar);
        if (avatarUrl) {
            const accessorizedAvatar = document.getElementById('accessorized-avatar');
            if (accessorizedAvatar) {
                accessorizedAvatar.src = avatarUrl;
            }
        }
        
        // Save current look state
        this.saveCurrentLookState();
    }
    
    /**
     * Save the current look state
     */
    saveCurrentLookState() {
        // In a real app, this would save the composite image and accessories list
        const lookState = {
            avatar: localStorage.getItem(CONFIG.storageKeys.currentAvatar),
            accessories: { ...this.selectedAccessories }
        };
        
        localStorage.setItem(CONFIG.storageKeys.currentLook, JSON.stringify(lookState));
    }
    
    /**
     * Show the save look modal
     */
    showSaveLookModal() {
        const modal = document.getElementById('save-look-modal');
        const previewImg = document.getElementById('look-preview-img');
        
        if (modal && previewImg) {
            // Set the preview image
            const avatarImage = document.getElementById('accessorized-avatar');
            if (avatarImage && avatarImage.src) {
                previewImg.src = avatarImage.src;
            }
            
            // Show the modal
            modal.classList.add('active');
            
            // Focus the input
            setTimeout(() => {
                const nameInput = document.getElementById('look-name');
                if (nameInput) {
                    nameInput.focus();
                }
            }, 100);
        }
    }
    
    /**
     * Save the current look to local storage
     */
    saveLook() {
        const nameInput = document.getElementById('look-name');
        const notesInput = document.getElementById('look-notes');
        
        if (!nameInput || !nameInput.value.trim()) {
            alert('Please enter a name for your look');
            return;
        }
        
        // Create look object
        const look = {
            id: Date.now().toString(),
            name: nameInput.value.trim(),
            notes: notesInput ? notesInput.value.trim() : '',
            date: new Date().toISOString(),
            image: document.getElementById('accessorized-avatar').src,
            accessories: { ...this.selectedAccessories }
        };
        
        // Get existing looks
        let savedLooks = JSON.parse(localStorage.getItem(CONFIG.storageKeys.savedLooks) || '[]');
        
        // Add new look
        savedLooks.push(look);
        
        // Save to local storage
        localStorage.setItem(CONFIG.storageKeys.savedLooks, JSON.stringify(savedLooks));
        
        // Close modal
        this.closeAllModals();
        
        // Navigate to My Looks section
        this.navigateToSection('my-looks');
        
        // Reset the form
        nameInput.value = '';
        if (notesInput) {
            notesInput.value = '';
        }
    }
    
    /**
     * Load saved looks from local storage
     */
    loadSavedLooks() {
        const looksGrid = document.getElementById('looks-grid');
        const noLooksMessage = document.getElementById('no-looks-message');
        
        if (!looksGrid) return;
        
        // Get saved looks
        const savedLooks = JSON.parse(localStorage.getItem(CONFIG.storageKeys.savedLooks) || '[]');
        
        // Clear existing content
        looksGrid.innerHTML = '';
        
        if (savedLooks.length > 0) {
            // Hide no looks message
            if (noLooksMessage) {
                noLooksMessage.style.display = 'none';
            }
            
            // Create look cards
            savedLooks.forEach(look => {
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
                    this.viewSavedLook(look.id);
                });
                
                card.querySelector('.delete-look-btn').addEventListener('click', () => {
                    this.deleteSavedLook(look.id);
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
     * View a saved look
     * @param {string} lookId - ID of the look to view
     */
    viewSavedLook(lookId) {
        // Get saved looks
        const savedLooks = JSON.parse(localStorage.getItem(CONFIG.storageKeys.savedLooks) || '[]');
        
        // Find the look
        const look = savedLooks.find(l => l.id === lookId);
        
        if (look) {
            // Load the look
            if (look.image) {
                localStorage.setItem(CONFIG.storageKeys.currentAvatar, look.image);
            }
            
            // Set selected accessories
            this.selectedAccessories = { ...look.accessories };
            
            // Navigate to accessory gallery
            this.navigateToSection('accessory-gallery');
        }
    }
    
    /**
     * Delete a saved look
     * @param {string} lookId - ID of the look to delete
     */
    deleteSavedLook(lookId) {
        // Confirm deletion
        if (confirm('Are you sure you want to delete this look?')) {
            // Get saved looks
            let savedLooks = JSON.parse(localStorage.getItem(CONFIG.storageKeys.savedLooks) || '[]');
            
            // Filter out the look to delete
            savedLooks = savedLooks.filter(look => look.id !== lookId);
            
            // Save updated looks
            localStorage.setItem(CONFIG.storageKeys.savedLooks, JSON.stringify(savedLooks));
            
            // Reload looks
            this.loadSavedLooks();
        }
    }
    
    /**
     * Download the current look as an image
     */
    downloadCurrentLook() {
        const avatar = document.getElementById('accessorized-avatar');
        
        if (avatar && avatar.src) {
            // Create a download link
            const link = document.createElement('a');
            link.download = `cws-look-${Date.now()}.png`;
            link.href = avatar.src;
            
            // Append to document, click, and remove
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }
    
    /**
     * Close all modals
     */
    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('active');
        });
    }
    
    /**
     * Apply theme to the application
     * @param {string} theme - 'light' or 'dark'
     */
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.themePreference = theme;
        
        // Update theme toggle if it exists
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.checked = theme === 'dark';
        }
    }
}

// Initialize UI Manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Create instance and expose to window for debugging
    window.uiManager = new UIManager();
});
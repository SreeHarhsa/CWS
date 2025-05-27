/**
 * Main application script for Chroma Wave Studios
 * Coordinates all managers and initializes the application
 */
class CWSApp {
    constructor() {
        // Application state
        this.isInitialized = false;
        this.isProcessing = false;
        this.currentSection = null;
        
        // Check browser support
        this.checkBrowserSupport();
        
        // Initialize the application
        this.init();
    }
    
    /**
     * Initialize the application
     */
    async init() {
        try {
            console.log('Initializing Chroma Wave Studios application...');
            
            // Wait for DOM content to be loaded
            if (document.readyState === 'loading') {
                await new Promise(resolve => {
                    document.addEventListener('DOMContentLoaded', resolve);
                });
            }
            
            // Initialize debug console for development
            this.initDebugConsole();
            
            // Initialize each manager
            // These are loaded via separate script files and create their own instances
            // We're just making sure they're properly connected
            
            // Check if UI manager is available
            if (!window.uiManager) {
                throw new Error('UI Manager not initialized');
            }
            
            // Connect managers to each other with event listeners
            this.connectManagers();
            
            // Load previous avatar if available
            this.loadPreviousAvatar();
            
            // Add global event listeners
            this.addGlobalEventListeners();
            
            // Mark as initialized
            this.isInitialized = true;
            
            console.log('Application initialized successfully');
        } catch (error) {
            console.error('Error initializing application:', error);
            this.showErrorMessage('Initialization Error', error.message);
        }
    }
    
    /**
     * Check browser support for required features
     */
    checkBrowserSupport() {
        // Check for Web APIs that are required
        const requiredAPIs = [
            { name: 'localStorage', api: window.localStorage },
            { name: 'FileReader', api: window.FileReader },
            { name: 'Canvas', api: document.createElement('canvas').getContext },
            { name: 'Fetch', api: window.fetch }
        ];
        
        const missingAPIs = requiredAPIs.filter(item => !item.api);
        
        if (missingAPIs.length > 0) {
            const apiList = missingAPIs.map(item => item.name).join(', ');
            const message = `Your browser doesn't support: ${apiList}. Please use a modern browser.`;
            
            // Show an error message
            alert(message);
            
            // Also log to console
            console.error('Browser support issue:', message);
        }
        
        // Check for camera support (optional)
        CameraManager.hasCamera().then(hasCamera => {
            if (!hasCamera) {
                console.warn('No camera detected. Upload functionality will still be available.');
            }
        });
    }
    
    /**
     * Initialize debug console for development
     */
    initDebugConsole() {
        // Add a debug method to window for development
        window.debug = {
            app: this,
            
            // Print app status
            status: () => {
                console.log('Application Status:');
                console.log('- Initialized:', this.isInitialized);
                console.log('- Processing:', this.isProcessing);
                console.log('- Current Section:', this.currentSection);
                console.log('- Camera Available:', window.cameraManager ? 'Yes' : 'No');
                console.log('- Avatar Generated:', window.avatarGenerator && window.avatarGenerator.avatarImage ? 'Yes' : 'No');
            },
            
            // Reset application state
            reset: () => {
                localStorage.clear();
                window.location.reload();
            },
            
            // Load sample data
            loadSampleData: () => {
                this.loadSampleAvatar();
            }
        };
    }
    
    /**
     * Connect managers with event listeners
     */
    connectManagers() {
        // Ensure all managers communicate with each other
        
        // Example: When an accessory is selected in accessoryManager,
        // inform avatarGenerator to apply it
        
        // These connections are mostly established in the individual manager classes
        // through direct calls to the other managers' methods
    }
    
    /**
     * Add global event listeners
     */
    addGlobalEventListeners() {
        // Handle window online/offline events
        window.addEventListener('online', () => {
            console.log('Application is online');
            // Re-enable network-dependent features
        });
        
        window.addEventListener('offline', () => {
            console.log('Application is offline');
            this.showErrorMessage('Network Error', 'You are currently offline. Some features may not work properly.');
        });
        
        // Handle visibility change (tab switching)
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'hidden') {
                // App is hidden, pause processing-heavy operations
                if (window.cameraManager) {
                    // Don't stop the camera as it would need to be reinitialized
                    // Just pause processing
                }
            } else {
                // App is visible again, resume operations
            }
        });
        
        // Handle beforeunload to save state
        window.addEventListener('beforeunload', () => {
            // Save any unsaved state
            // Most state is already saved immediately when changed
        });
    }
    
    /**
     * Load the previous avatar if available
     */
    loadPreviousAvatar() {
        const avatarUrl = localStorage.getItem(CONFIG.storageKeys.currentAvatar);
        
        if (avatarUrl) {
            // Display in avatar preview
            const avatarResult = document.getElementById('avatar-result');
            const avatarPlaceholder = document.getElementById('avatar-placeholder');
            
            if (avatarResult && avatarPlaceholder) {
                avatarResult.src = avatarUrl;
                avatarResult.style.display = 'block';
                avatarPlaceholder.style.display = 'none';
                
                // Enable continue button
                const continueBtn = document.getElementById('continue-to-accessories-btn');
                if (continueBtn) {
                    continueBtn.disabled = false;
                }
            }
            
            // Set in accessorized avatar view
            const accessorizedAvatar = document.getElementById('accessorized-avatar');
            if (accessorizedAvatar) {
                accessorizedAvatar.src = avatarUrl;
            }
            
            // If avatar generator is available, initialize with this image
            if (window.avatarGenerator) {
                window.avatarGenerator.avatarImage = avatarUrl;
            }
        }
    }
    
    /**
     * Load a sample avatar for testing
     */
    loadSampleAvatar() {
        const sampleUrl = 'assets/images/sample-avatar.png';
        
        // Save to storage
        localStorage.setItem(CONFIG.storageKeys.currentAvatar, sampleUrl);
        
        // Reload avatar
        this.loadPreviousAvatar();
        
        // Navigate to accessories
        if (window.uiManager) {
            window.uiManager.navigateToSection('accessory-gallery');
        }
    }
    
    /**
     * Show an error message to the user
     * @param {string} title - Error title
     * @param {string} message - Error message
     */
    showErrorMessage(title, message) {
        // In a production app, this would show a proper error modal
        // For now, we'll use alert
        alert(`${title}: ${message}`);
    }
}

// Initialize the application when the page loads
window.addEventListener('load', () => {
    window.cwsApp = new CWSApp();
});
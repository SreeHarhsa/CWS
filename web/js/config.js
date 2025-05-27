/**
 * Configuration settings for Chroma Wave Studios web application
 */
const CONFIG = {
    // API endpoint for connecting to the Python backend
    apiBaseUrl: '/api',
    
    // Camera settings
    camera: {
        facingMode: 'user', // 'user' for front camera, 'environment' for back camera
        width: 640,
        height: 480,
        fps: 30
    },
    
    // Face detection settings
    faceDetection: {
        minDetectionConfidence: 0.5,
        modelComplexity: 1, // 0=Lite, 1=Full
        maxNumFaces: 1
    },
    
    // Avatar generation settings
    avatarGeneration: {
        imageQuality: 0.9,
        processingStages: [
            { name: "Analyzing facial features...", duration: 1500 },
            { name: "Extracting key points...", duration: 2000 },
            { name: "Generating 3D model...", duration: 3000 },
            { name: "Applying textures...", duration: 2000 },
            { name: "Finalizing avatar...", duration: 1500 }
        ]
    },
    
    // Accessory categories with their icons
    accessoryCategories: [
        { id: 'clothing', name: 'Clothing', icon: 'fa-tshirt' },
        { id: 'jewelry', name: 'Jewelry', icon: 'fa-gem' },
        { id: 'shoes', name: 'Shoes', icon: 'fa-shoe-prints' },
        { id: 'watches', name: 'Watches', icon: 'fa-clock' }
    ],
    
    // Demo mode settings
    demoMode: {
        enabled: true,
        sampleAccessories: {
            clothing: [
                { id: 'c1', name: 'Casual T-Shirt', image: 'assets/accessories/clothing/tshirt.png', thumbnail: 'assets/accessories/clothing/tshirt_thumb.png' },
                { id: 'c2', name: 'Formal Shirt', image: 'assets/accessories/clothing/formal-shirt.png', thumbnail: 'assets/accessories/clothing/formal-shirt_thumb.png' },
                { id: 'c3', name: 'Dress', image: 'assets/accessories/clothing/dress.png', thumbnail: 'assets/accessories/clothing/dress_thumb.png' },
                { id: 'c4', name: 'Hoodie', image: 'assets/accessories/clothing/hoodie.png', thumbnail: 'assets/accessories/clothing/hoodie_thumb.png' },
                { id: 'c5', name: 'Suit Jacket', image: 'assets/accessories/clothing/suit.png', thumbnail: 'assets/accessories/clothing/suit_thumb.png' }
            ],
            jewelry: [
                { id: 'j1', name: 'Gold Necklace', image: 'assets/accessories/jewelry/gold-necklace.png', thumbnail: 'assets/accessories/jewelry/gold-necklace_thumb.png' },
                { id: 'j2', name: 'Silver Earrings', image: 'assets/accessories/jewelry/silver-earrings.png', thumbnail: 'assets/accessories/jewelry/silver-earrings_thumb.png' },
                { id: 'j3', name: 'Diamond Ring', image: 'assets/accessories/jewelry/diamond-ring.png', thumbnail: 'assets/accessories/jewelry/diamond-ring_thumb.png' }
            ],
            shoes: [
                { id: 's1', name: 'Sneakers', image: 'assets/accessories/shoes/sneakers.png', thumbnail: 'assets/accessories/shoes/sneakers_thumb.png' },
                { id: 's2', name: 'Dress Shoes', image: 'assets/accessories/shoes/dress-shoes.png', thumbnail: 'assets/accessories/shoes/dress-shoes_thumb.png' },
                { id: 's3', name: 'High Heels', image: 'assets/accessories/shoes/heels.png', thumbnail: 'assets/accessories/shoes/heels_thumb.png' }
            ],
            watches: [
                { id: 'w1', name: 'Smart Watch', image: 'assets/accessories/watches/smart-watch.png', thumbnail: 'assets/accessories/watches/smart-watch_thumb.png' },
                { id: 'w2', name: 'Luxury Watch', image: 'assets/accessories/watches/luxury-watch.png', thumbnail: 'assets/accessories/watches/luxury-watch_thumb.png' }
            ]
        }
    },
    
    // Storage keys for local storage
    storageKeys: {
        theme: 'cws-theme',
        savedLooks: 'cws-saved-looks',
        currentAvatar: 'cws-current-avatar',
        currentLook: 'cws-current-look'
    }
};
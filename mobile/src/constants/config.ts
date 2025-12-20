// API Configuration
// For development, update this to your machine's IP address
// For production, replace with actual backend URL

export const API_CONFIG = {
  // Use 10.0.2.2 for Android emulator, localhost for iOS simulator
  // For physical device, use your computer's IP address (e.g., 192.168.1.x)
  baseURL: __DEV__ 
    ? 'http://10.0.2.2:8001' // Android emulator default
    : 'https://your-production-api.com',
  
  timeout: 60000, // 60 seconds for LLM responses
};

// Helper to get platform-specific API URL
export const getApiUrl = (platform: 'android' | 'ios' | 'web') => {
  if (!__DEV__) {
    return API_CONFIG.baseURL;
  }
  
  switch (platform) {
    case 'android':
      return 'http://10.0.2.2:8001';
    case 'ios':
      return 'http://localhost:8001';
    default:
      return 'http://localhost:8001';
  }
};

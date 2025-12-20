# LLM Council Mobile

React Native mobile application for the LLM Council deliberation system.

## Setup

### Prerequisites
- Node.js 18+ installed
- Backend server running on port 8001
- For Android: Android Studio with emulator or physical device
- For iOS: Xcode (macOS only) or Expo Go app

### Installation

```bash
cd mobile
npm install
```

### Configuration

**Important**: Update the API base URL for your device.

Edit `src/constants/config.ts`:

- **Android Emulator**: Uses `http://10.0.2.2:8001` (default)
- **iOS Simulator**: Uses `http://localhost:8001`
- **Physical Device**: Replace with your computer's IP address (e.g., `http://192.168.1.x:8001`)

To find your computer's IP:
- Windows: `ipconfig`
- macOS/Linux: `ifconfig` or `ip addr`

### Running the App

1. **Start the backend server** (from root directory):
```bash
cd ..
uv run python -m backend.main
```

2. **Start Expo** (from mobile directory):
```bash
npx expo start
```

3. **Run on device**:
   - **Android Emulator**: Press `a` in the Expo terminal
   - **iOS Simulator**: Press `i` in the Expo terminal (macOS only)
   - **Physical Device**: 
     - Install Expo Go from App Store/Play Store
     - Scan the QR code shown in terminal
     - Ensure phone and computer are on same WiFi network

## Project Structure

```
mobile/
├── src/
│   ├── components/      # Reusable UI components
│   │   ├── MessageBubble.tsx   # Chat message display
│   │   └── ErrorBanner.tsx     # Error notification
│   ├── screens/         # App screens
│   │   └── ChatScreen.tsx      # Main chat interface
│   ├── services/        # API and external services
│   │   └── api.ts              # Backend API client
│   ├── context/         # React Context for state
│   │   └── ConversationContext.tsx
│   ├── constants/       # Theme and configuration
│   │   ├── theme.ts            # Colors, typography, spacing
│   │   └── config.ts           # API configuration
│   ├── types/           # TypeScript type definitions
│   │   └── index.ts
│   ├── hooks/           # Custom React hooks (future)
│   └── utils/           # Utility functions (future)
├── App.tsx              # Root component
└── package.json
```

## Features Implemented

### Phase 1 ✅
- [x] Project setup with TypeScript
- [x] Folder structure
- [x] Theme constants (Industrial Metallic)
- [x] API service layer with Axios
- [x] Conversation context for state management
- [x] Chat screen with message input
- [x] Message bubble component with 3-stage display
- [x] Error handling and loading states
- [x] Markdown rendering for AI responses
- [x] Expandable stage views

### Phase 2 (Next Steps)
- [ ] Conversation history screen
- [ ] Camera integration for image uploads
- [ ] Offline detection
- [ ] AsyncStorage for caching
- [ ] Navigation between screens
- [ ] Pull to refresh
- [ ] Deep linking

## Development Notes

### Color Theme
The app uses the Industrial Metallic theme from the web app:
- Charcoal background (#1F262A)
- Steel gray cards (#4A5C68)
- Slate blue primary (#546E7A)

OKLCH colors were converted to hex for React Native compatibility.

### API Integration
- Axios with interceptors for logging
- 60-second timeout for LLM responses
- Automatic retry handled by context
- Platform-specific base URLs

### Known Issues
- Warning about `react-native-screens` version mismatch (non-critical)
- Camera feature not yet implemented

## Troubleshooting

**Can't connect to backend:**
1. Ensure backend is running on port 8001
2. Check firewall settings
3. Update API URL in `config.ts` with correct IP
4. For Android emulator, use `10.0.2.2` not `localhost`

**App won't load:**
1. Clear Metro bundler cache: `npx expo start -c`
2. Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

**TypeScript errors:**
1. Restart TypeScript server in VS Code
2. Run: `npx tsc --noEmit`

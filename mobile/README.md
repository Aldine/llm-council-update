# LLM Council Mobile

React Native mobile application for the LLM Council deliberation system with JWT authentication and EAS Update support.

## Features

- 🔒 **JWT Authentication**: Secure login with access/refresh tokens
- 💾 **Encrypted Storage**: Tokens stored in device secure storage
- 🔄 **Automatic Token Refresh**: Seamless session management
- 📱 **Cross-Platform**: iOS and Android support
- 🚀 **OTA Updates**: Over-the-air updates via EAS Update
- 🎨 **Industrial Metallic Theme**: Consistent with web app

## Setup

### Prerequisites
- Node.js 18+ installed
- Backend server running on port 8001
- Expo CLI: `npm install -g expo-cli`
- EAS CLI: `npm install -g eas-cli`
- For Android: Android Studio with emulator or physical device
- For iOS: Xcode (macOS only) or Expo Go app

### Installation

```bash
cd mobile
npm install
```

### Configuration

#### API Base URL

Edit `src/constants/config.ts`:

- **Android Emulator**: Uses `http://10.0.2.2:8001` (default)
- **iOS Simulator**: Uses `http://localhost:8001`
- **Physical Device**: Replace with your computer's IP address (e.g., `http://192.168.1.x:8001`)

To find your computer's IP:
- Windows: `ipconfig` (look for IPv4 Address)
- macOS/Linux: `ifconfig` or `ip addr`

#### EAS Project Setup

1. **Login to Expo**:
```bash
eas login
```

2. **Initialize EAS project**:
```bash
eas init
```

3. **Configure secrets** (production only):
```bash
eas secret:create --scope project --name JWT_SECRET_KEY --value <your-secret>
```

### Running the App

#### Development Mode (Expo Go)

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

#### Production Build (EAS Build)

1. **Build preview app** (internal testing):
```bash
./scripts/release-preview.ps1
```
Or manually:
```bash
eas build --profile preview --platform all
```

2. **Install preview build** on test devices (download from EAS dashboard)

3. **Publish OTA update** to preview channel:
```powershell
./scripts/publish-update.ps1 -Channel preview -Message "Fix login bug"
```

4. **Promote to production** after testing:
```powershell
./scripts/promote-production.ps1 -GroupId <preview-group-id>
```

5. **Rollback if needed**:
```powershell
./scripts/rollback.ps1 -Channel production -GroupId <previous-group-id>
```

## Authentication

### Demo Credentials

For development/testing, use these credentials:
- **Email**: `demo@llmcouncil.com`
- **Password**: `demo123`

### Token Lifecycle

- **Access Token**: 60 minute expiry, automatically refreshed on 401
- **Refresh Token**: 7 day expiry, used to obtain new access tokens
- **Storage**: Encrypted via expo-secure-store (iOS Keychain/Android Keystore)

### Session Behavior

- **Auto-restore**: App checks for valid session on launch
- **Auto-refresh**: 401 responses trigger automatic token refresh
- **Logout**: Clears all tokens from secure storage

See `SECURITY.md` for detailed authentication flow and security considerations.

## Project Structure

```
mobile/
├── src/
│   ├── components/      # Reusable UI components
│   │   ├── MessageBubble.tsx   # Chat message display
│   │   ├── ErrorBanner.tsx     # Error notification
│   │   ├── Stage1.tsx          # Initial responses view
│   │   ├── Stage2.tsx          # Rankings view
│   │   └── Stage3.tsx          # Final synthesis view
│   ├── screens/         # App screens
│   │   ├── ChatScreen.tsx      # Main chat interface
│   │   └── LoginScreen.tsx     # Authentication screen
│   ├── services/        # API and external services
│   │   ├── api.ts              # Backend API client
│   │   ├── auth.ts             # Authentication service
│   │   └── secureStore.ts      # Encrypted token storage
│   ├── context/         # React Context for state
│   │   ├── ConversationContext.tsx
│   │   └── AuthContext.tsx     # Auth state machine
│   ├── constants/       # Theme and configuration
│   │   ├── theme.ts            # Colors, typography, spacing
│   │   └── config.ts           # API configuration
│   ├── types/           # TypeScript type definitions
│   │   └── index.ts
│   ├── hooks/           # Custom React hooks (future)
│   └── utils/           # Utility functions (future)
├── scripts/             # Release automation
│   ├── release-preview.ps1     # Build preview shell
│   ├── publish-update.ps1      # Publish OTA update
│   ├── promote-production.ps1  # Promote to production
│   └── rollback.ps1            # Rollback update
├── App.tsx              # Root component with update check
├── app.json             # Expo configuration
├── eas.json             # EAS Build/Update configuration
├── package.json
├── SECURITY.md          # Security documentation
└── README.md
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

### Phase 2 ✅
- [x] JWT authentication (access + refresh tokens)
- [x] Encrypted token storage (expo-secure-store)
- [x] Login screen with form validation
- [x] Auth state machine (5 states)
- [x] Automatic token refresh on 401
- [x] Session restore on app launch
- [x] Logout functionality
- [x] Protected API routes
- [x] EAS Build configuration
- [x] EAS Update OTA support
- [x] Update check on app launch
- [x] Release automation scripts

### Phase 3 (Future)
- [ ] Biometric authentication (Face ID/Touch ID)
- [ ] Conversation history screen
- [ ] Navigation between screens
- [ ] Offline detection and caching
- [ ] Camera integration for image uploads
- [ ] Pull to refresh
- [ ] Deep linking
- [ ] Push notifications
- [ ] Certificate pinning
- [ ] Error boundary component
- [ ] Unit and E2E tests

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

import React, { useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { View, ActivityIndicator, StyleSheet, Alert, Platform } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import * as Updates from 'expo-updates';
import { AuthProvider, useAuth } from './src/context/AuthContext';
import { ConversationProvider } from './src/context/ConversationContext';
import ChatScreen from './src/screens/ChatScreen';
import LoginScreen from './src/screens/LoginScreen';
import { Colors } from './src/constants/theme';

function AppContent() {
  const { state } = useAuth();

  if (state === 'INITIALIZING') {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={Colors.primary} />
      </View>
    );
  }

  if (state === 'UNAUTHENTICATED' || state === 'AUTHENTICATING' || state === 'ERROR') {
    return <LoginScreen />;
  }

  return (
    <ConversationProvider>
      <ChatScreen />
    </ConversationProvider>
  );
}

export default function App() {
  useEffect(() => {
    // Check for updates on mount
    checkForUpdates();
  }, []);

  const checkForUpdates = async () => {
    // Skip in development mode
    if (__DEV__) {
      console.log('[Updates] Skipping update check in development mode');
      return;
    }

    try {
      const update = await Updates.checkForUpdateAsync();
      if (update.isAvailable) {
        console.log('[Updates] Update available, downloading...');
        await Updates.fetchUpdateAsync();
        
        // Show alert to user
        Alert.alert(
          'Update Available',
          'A new version has been downloaded. Restart to apply?',
          [
            { text: 'Later', style: 'cancel' },
            { 
              text: 'Restart Now', 
              onPress: () => Updates.reloadAsync() 
            },
          ]
        );
      } else {
        console.log('[Updates] App is up to date');
      }
    } catch (error) {
      // Silently fail - don't block app usage
      console.error('[Updates] Error checking for updates:', error);
    }
  };

  return (
    <SafeAreaProvider>
      <AuthProvider>
        <AppContent />
        <StatusBar style="light" />
      </AuthProvider>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    backgroundColor: Colors.background,
    alignItems: 'center',
    justifyContent: 'center',
  },
});

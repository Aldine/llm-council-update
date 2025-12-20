import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { ConversationProvider } from './src/context/ConversationContext';
import ChatScreen from './src/screens/ChatScreen';

export default function App() {
  return (
    <SafeAreaProvider>
      <ConversationProvider>
        <ChatScreen />
        <StatusBar style="light" />
      </ConversationProvider>
    </SafeAreaProvider>
  );
}

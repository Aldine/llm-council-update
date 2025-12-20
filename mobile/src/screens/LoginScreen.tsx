import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuth } from '../context/AuthContext';
import { Colors, Spacing, Typography, BorderRadius } from '../constants/theme';

export default function LoginScreen() {
  const [email, setEmail] = useState('demo@llmcouncil.com');
  const [password, setPassword] = useState('demo123');
  const { login, state, error, clearError } = useAuth();

  const handleLogin = async () => {
    if (!email.trim() || !password.trim()) {
      Alert.alert('Error', 'Please enter email and password');
      return;
    }

    await login(email, password);
  };

  const isLoading = state === 'AUTHENTICATING';

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <View style={styles.content}>
          {/* Logo/Title */}
          <View style={styles.header}>
            <Text style={styles.title}>LLM Council</Text>
            <Text style={styles.subtitle}>
              Multiple AI models collaborate to answer your questions
            </Text>
          </View>

          {/* Error Message */}
          {error && (
            <View style={styles.errorBanner}>
              <Text style={styles.errorText}>{error}</Text>
              <TouchableOpacity onPress={clearError}>
                <Text style={styles.errorClose}>✕</Text>
              </TouchableOpacity>
            </View>
          )}

          {/* Login Form */}
          <View style={styles.form}>
            <Text style={styles.label}>Email</Text>
            <TextInput
              style={styles.input}
              value={email}
              onChangeText={setEmail}
              placeholder="demo@llmcouncil.com"
              placeholderTextColor={Colors.mutedForeground}
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={false}
              editable={!isLoading}
            />

            <Text style={styles.label}>Password</Text>
            <TextInput
              style={styles.input}
              value={password}
              onChangeText={setPassword}
              placeholder="Enter password"
              placeholderTextColor={Colors.mutedForeground}
              secureTextEntry
              autoCapitalize="none"
              autoCorrect={false}
              editable={!isLoading}
              onSubmitEditing={handleLogin}
            />

            <TouchableOpacity
              style={[styles.loginButton, isLoading && styles.loginButtonDisabled]}
              onPress={handleLogin}
              disabled={isLoading}
            >
              {isLoading ? (
                <ActivityIndicator color={Colors.primaryForeground} />
              ) : (
                <Text style={styles.loginButtonText}>Sign In</Text>
              )}
            </TouchableOpacity>

            {/* Demo Credentials Hint */}
            <View style={styles.hint}>
              <Text style={styles.hintText}>Demo Account</Text>
              <Text style={styles.hintSubtext}>
                Email: demo@llmcouncil.com{'\n'}
                Password: demo123
              </Text>
            </View>
          </View>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  keyboardView: {
    flex: 1,
  },
  content: {
    flex: 1,
    paddingHorizontal: Spacing.xl,
    justifyContent: 'center',
  },
  header: {
    alignItems: 'center',
    marginBottom: Spacing.xxl,
  },
  title: {
    ...Typography.h1,
    color: Colors.foreground,
    marginBottom: Spacing.sm,
  },
  subtitle: {
    ...Typography.body,
    color: Colors.mutedForeground,
    textAlign: 'center',
  },
  errorBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: Colors.destructive,
    padding: Spacing.md,
    borderRadius: BorderRadius.md,
    marginBottom: Spacing.lg,
  },
  errorText: {
    ...Typography.small,
    color: Colors.destructiveForeground,
    flex: 1,
  },
  errorClose: {
    ...Typography.body,
    color: Colors.destructiveForeground,
    fontWeight: '700',
    marginLeft: Spacing.sm,
  },
  form: {
    width: '100%',
  },
  label: {
    ...Typography.small,
    color: Colors.foreground,
    marginBottom: Spacing.xs,
    fontWeight: '600',
  },
  input: {
    backgroundColor: Colors.card,
    borderRadius: BorderRadius.lg,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.md,
    ...Typography.body,
    color: Colors.foreground,
    marginBottom: Spacing.lg,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  loginButton: {
    backgroundColor: Colors.primary,
    paddingVertical: Spacing.md,
    borderRadius: BorderRadius.lg,
    alignItems: 'center',
    marginTop: Spacing.md,
  },
  loginButtonDisabled: {
    opacity: 0.5,
  },
  loginButtonText: {
    ...Typography.body,
    color: Colors.primaryForeground,
    fontWeight: '700',
  },
  hint: {
    marginTop: Spacing.xl,
    padding: Spacing.md,
    backgroundColor: Colors.muted,
    borderRadius: BorderRadius.md,
    borderLeftWidth: 4,
    borderLeftColor: Colors.primary,
  },
  hintText: {
    ...Typography.small,
    color: Colors.foreground,
    fontWeight: '600',
    marginBottom: Spacing.xs,
  },
  hintSubtext: {
    ...Typography.tiny,
    color: Colors.mutedForeground,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
});

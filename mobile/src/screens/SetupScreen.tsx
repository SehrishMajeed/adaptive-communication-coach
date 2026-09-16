import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView, Alert } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../app/NavigationTypes';
import type { PracticeSetup } from '../../../shared/types';
import { PracticeContextCard } from '../components/PracticeContextCard';
import { checkAndRequestPermissions } from '../services/permissions';

type Props = NativeStackScreenProps<RootStackParamList, 'Setup'>;

const defaultSetup: PracticeSetup = {
  scenario: 'Explain a technical project to a non-technical person in 60 seconds.',
  audience: 'recruiter or non-technical interviewer',
  goal: 'make the project understandable and relevant',
  requested_duration_seconds: 60,
};

export const SetupScreen: React.FC<Props> = ({ navigation }) => {
  const handleStart = async () => {
    const hasPermissions = await checkAndRequestPermissions();
    if (hasPermissions) {
      navigation.navigate('Record', { setup: defaultSetup });
    } else {
      Alert.alert('Permission Required', 'Camera and Microphone permissions are required to practice.');
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        <Text style={styles.header}>Aura Coach</Text>
        
        <PracticeContextCard setup={defaultSetup} />

        <View style={styles.spacer} />

        <TouchableOpacity 
          style={styles.button} 
          onPress={handleStart}
          accessibilityRole="button"
          accessibilityLabel="Start Practice"
          accessibilityHint="Navigates to the recording screen after permissions are granted"
        >
          <Text style={styles.buttonText}>Start Practice</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#121212',
  },
  container: {
    flex: 1,
    padding: 16,
  },
  header: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFF',
    marginBottom: 24,
    textAlign: 'center',
  },
  spacer: {
    flex: 1,
  },
  button: {
    backgroundColor: '#3B82F6',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: '600',
  },
});

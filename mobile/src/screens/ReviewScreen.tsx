import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView, Alert } from 'react-native';
import Video from 'react-native-video';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../app/NavigationTypes';
import { analyzeRecording } from '../services/api';
import { Loader } from '../components/Loader';

type Props = NativeStackScreenProps<RootStackParamList, 'Review'>;

export const ReviewScreen: React.FC<Props> = ({ navigation, route }) => {
  const { setup, sessionId, videoUri, audioUri, durationSeconds } = route.params;
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const result = await analyzeRecording({ audioUri, videoUri, durationSeconds }, sessionId, setup);
      navigation.replace('Feedback', { setup, result });
    } catch (error: any) {
      setIsSubmitting(false);
      Alert.alert('Analysis Failed', error.message || 'An error occurred during analysis.');
    }
  };

  const handleRetake = () => {
    navigation.replace('Record', { setup, sessionId });
  };

  if (isSubmitting) {
    return <Loader text="Analyzing your practice..." />;
  }

  return (
    <SafeAreaView style={styles.container}>
      <Video
        source={{ uri: videoUri }}
        style={styles.video}
        controls={true}
        resizeMode="contain"
      />
      <View style={styles.controls}>
        <TouchableOpacity style={styles.retakeButton} onPress={handleRetake}>
          <Text style={styles.retakeText}>Retake</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.submitButton} onPress={handleSubmit}>
          <Text style={styles.submitText}>Submit for Feedback</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: 'black' },
  video: { flex: 1 },
  controls: {
    flexDirection: 'row',
    padding: 16,
    justifyContent: 'space-between',
    backgroundColor: '#121212',
  },
  retakeButton: {
    flex: 1,
    padding: 16,
    backgroundColor: '#333',
    borderRadius: 8,
    marginRight: 8,
    alignItems: 'center',
  },
  retakeText: { color: 'white', fontWeight: 'bold' },
  submitButton: {
    flex: 1,
    padding: 16,
    backgroundColor: '#3B82F6',
    borderRadius: 8,
    marginLeft: 8,
    alignItems: 'center',
  },
  submitText: { color: 'white', fontWeight: 'bold' },
});

import React, { useRef, useState, useEffect, useCallback } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView } from 'react-native';
import { Camera, useCameraDevice } from 'react-native-vision-camera';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../app/NavigationTypes';
import { logger } from '../shared/observability/logger';

type Props = NativeStackScreenProps<RootStackParamList, 'Record'>;

type LocalRecorderRef = {
  startRecording: (options: {
    onRecordingFinished: (video: { path: string }) => void;
    onRecordingError: (error: Error) => void;
  }) => void;
  stopRecording: () => Promise<void>;
};

export const RecordScreen: React.FC<Props> = ({ navigation, route }) => {
  const { setup, sessionId } = route.params;
  const device = useCameraDevice('front');
  const camera = useRef<LocalRecorderRef | null>(null);
  const durationRef = useRef(0);
  
  const [isRecording, setIsRecording] = useState(false);
  const [timeLeft, setTimeLeft] = useState(setup.requested_duration_seconds);

  const handleStopRecording = useCallback(async () => {
    if (!camera.current || !isRecording) return;
    setIsRecording(false);
    await camera.current.stopRecording();
  }, [isRecording]);

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (isRecording && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((prev: number) => prev - 1);
        durationRef.current += 1;
      }, 1000);
    } else if (isRecording && timeLeft === 0) {
      handleStopRecording();
    }
    return () => clearInterval(interval);
  }, [handleStopRecording, isRecording, timeLeft]);

  const handleStartRecording = async () => {
    if (!camera.current) return;
    setIsRecording(true);
    setTimeLeft(setup.requested_duration_seconds);
    durationRef.current = 0;
    
    camera.current.startRecording({
      onRecordingFinished: (video) => {
        const uri = video.path.startsWith('file://') ? video.path : `file://${video.path}`;
        navigation.replace('Review', {
          setup,
          sessionId,
          videoUri: uri,
          audioUri: uri,
          durationSeconds: Math.max(durationRef.current, 1),
        });
      },
      onRecordingError: (error) => logger.error(error),
    });
  };

  if (device == null) return <SafeAreaView style={styles.container}><Text style={styles.text}>No Camera Device Found</Text></SafeAreaView>;

  return (
    <SafeAreaView style={styles.container}>
      <Camera
        style={StyleSheet.absoluteFill}
        device={device}
        isActive={true}
        ref={camera as React.Ref<never>}
      />
      
      <View style={styles.overlay}>
        <Text style={styles.timer}>00:{(timeLeft < 10 ? '0' : '')}{timeLeft}</Text>
        
        <View style={styles.controls}>
          {isRecording ? (
            <TouchableOpacity 
              style={styles.stopButton} 
              onPress={handleStopRecording}
              accessibilityRole="button"
              accessibilityLabel="Stop Recording"
              accessibilityHint="Stops the camera recording and proceeds to review"
            >
              <View style={styles.stopSquare} />
            </TouchableOpacity>
          ) : (
            <TouchableOpacity 
              style={styles.recordButton} 
              onPress={handleStartRecording}
              accessibilityRole="button"
              accessibilityLabel="Start Recording"
              accessibilityHint="Starts recording your practice session"
            >
              <View style={styles.recordCircle} />
            </TouchableOpacity>
          )}
        </View>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'black',
  },
  text: {
    color: 'white',
    textAlign: 'center',
    marginTop: 20,
  },
  overlay: {
    flex: 1,
    justifyContent: 'space-between',
    padding: 20,
  },
  timer: {
    color: 'white',
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginTop: 40,
    textShadowColor: 'rgba(0,0,0,0.5)',
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 4,
  },
  controls: {
    alignItems: 'center',
    marginBottom: 40,
  },
  recordButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  recordCircle: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: 'red',
  },
  stopButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  stopSquare: {
    width: 30,
    height: 30,
    backgroundColor: 'red',
    borderRadius: 4,
  },
});

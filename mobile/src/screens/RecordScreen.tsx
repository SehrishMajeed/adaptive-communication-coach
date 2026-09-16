import React, { useRef, useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView } from 'react-native';
import { Camera, useCameraDevice } from 'react-native-vision-camera';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../app/NavigationTypes';

type Props = NativeStackScreenProps<RootStackParamList, 'Record'>;

export const RecordScreen: React.FC<Props> = ({ navigation, route }) => {
  const { setup, sessionId } = route.params;
  const device = useCameraDevice('front');
  const camera = useRef<any>(null);
  
  const [isRecording, setIsRecording] = useState(false);
  const [timeLeft, setTimeLeft] = useState(setup.requested_duration_seconds);
  const [actualDuration, setActualDuration] = useState(0);

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (isRecording && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((prev: number) => prev - 1);
        setActualDuration((prev: number) => prev + 1);
      }, 1000);
    } else if (isRecording && timeLeft === 0) {
      handleStopRecording();
    }
    return () => clearInterval(interval);
  }, [isRecording, timeLeft]);

  const handleStartRecording = async () => {
    if (!camera.current) return;
    setIsRecording(true);
    setTimeLeft(setup.requested_duration_seconds);
    setActualDuration(0);
    
    camera.current.startRecording({
      onRecordingFinished: (video: any) => {
        // Ensure path has file:// prefix if not already present
        const uri = video.path.startsWith('file://') ? video.path : `file://${video.path}`;
        navigation.replace('Review', {
          setup,
          sessionId,
          videoUri: uri,
          audioUri: uri,
          durationSeconds: actualDuration || 1, // Fallback to 1s min
        });
      },
      onRecordingError: (error: any) => console.error(error),
    });
  };

  const handleStopRecording = async () => {
    if (!camera.current || !isRecording) return;
    setIsRecording(false);
    await camera.current.stopRecording();
  };

  if (device == null) return <SafeAreaView style={styles.container}><Text style={styles.text}>No Camera Device Found</Text></SafeAreaView>;

  return (
    <SafeAreaView style={styles.container}>
      <Camera
        style={StyleSheet.absoluteFill}
        device={device}
        isActive={true}
        ref={camera}
      />
      
      <View style={styles.overlay}>
        <Text style={styles.timer}>00:{(timeLeft < 10 ? '0' : '')}{timeLeft}</Text>
        
        <View style={styles.controls}>
          {isRecording ? (
            <TouchableOpacity style={styles.stopButton} onPress={handleStopRecording}>
              <View style={styles.stopSquare} />
            </TouchableOpacity>
          ) : (
            <TouchableOpacity style={styles.recordButton} onPress={handleStartRecording}>
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

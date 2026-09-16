import { Platform } from 'react-native';
import { check, request, PERMISSIONS, RESULTS } from 'react-native-permissions';

export const checkAndRequestPermissions = async (): Promise<boolean> => {
  const cameraPermission = Platform.OS === 'ios' ? PERMISSIONS.IOS.CAMERA : PERMISSIONS.ANDROID.CAMERA;
  const micPermission = Platform.OS === 'ios' ? PERMISSIONS.IOS.MICROPHONE : PERMISSIONS.ANDROID.RECORD_AUDIO;

  let camStatus = await check(cameraPermission);
  if (camStatus === RESULTS.DENIED) {
    camStatus = await request(cameraPermission, {
      title: 'Camera Permission',
      message: 'Aura Coach needs camera access to record your practice explanation. Video stays on your device.',
      buttonPositive: 'OK',
    });
  }

  let micStatus = await check(micPermission);
  if (micStatus === RESULTS.DENIED) {
    micStatus = await request(micPermission, {
      title: 'Microphone Permission',
      message: 'Aura Coach needs microphone access to record your practice explanation.',
      buttonPositive: 'OK',
    });
  }

  return camStatus === RESULTS.GRANTED && micStatus === RESULTS.GRANTED;
};

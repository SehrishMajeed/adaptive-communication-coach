import { NativeModules, Platform } from 'react-native';

type AudioExtractorModule = {
  extractMonoPcmWav: (inputUri: string) => Promise<string>;
};

const nativeAudioExtractor = NativeModules.AudioExtractor as AudioExtractorModule | undefined;

export const extractMonoPcmWav = async (inputUri: string): Promise<string> => {
  if (Platform.OS !== 'android') {
    throw new Error('Audio extraction is only implemented for Android.');
  }
  if (!nativeAudioExtractor?.extractMonoPcmWav) {
    throw new Error('Android audio extraction is not available in this build.');
  }
  return nativeAudioExtractor.extractMonoPcmWav(inputUri);
};

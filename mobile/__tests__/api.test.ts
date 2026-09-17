import { analyzeRecording, apiBase } from '../src/services/api';

describe('mobile API configuration', () => {
  it('uses localhost in dev so adb reverse can connect a real Android device to the backend', () => {
    expect(apiBase()).toBe('http://localhost:8000');
  });

  it('does not mislabel a recorded video file as backend-ready WAV audio', async () => {
    const fetchSpy = jest.spyOn(globalThis, 'fetch');

    await expect(analyzeRecording({
      audioUri: 'file:///tmp/recording.mp4',
      videoUri: 'file:///tmp/recording.mp4',
      durationSeconds: 5,
    })).rejects.toThrow('extracts a mono PCM WAV audio file');

    expect(fetchSpy).not.toHaveBeenCalled();
    fetchSpy.mockRestore();
  });
});

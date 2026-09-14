import { expect, it, vi } from 'vitest';
import { encodeWav, prepareAudio } from './audio';

it('writes mono PCM16 with accurate sample metadata', async () => {
  const data = new Float32Array(8000); data[0] = 1; data[1] = -1;
  const buffer = { duration: 1, length: 8000, sampleRate: 8000, numberOfChannels: 1, getChannelData: () => data } as unknown as AudioBuffer;
  const blob = encodeWav(buffer);
  const bytes = await new Promise<ArrayBuffer>(resolve => { const reader = new FileReader(); reader.onload = () => resolve(reader.result as ArrayBuffer); reader.readAsArrayBuffer(blob); });
  const view = new DataView(bytes);
  expect(blob.type).toBe('audio/wav');
  expect(view.getUint16(22, true)).toBe(1);
  expect(view.getUint32(24, true)).toBe(8000);
  expect(view.getUint32(40, true)).toBe(16000);
  expect(view.getInt16(44, true)).toBe(32767);
  expect(view.getInt16(46, true)).toBe(-32768);
});

it('closes the audio context when decoding fails', async () => {
  const close = vi.fn().mockResolvedValue(undefined);
  vi.stubGlobal('AudioContext', class { close = close; decodeAudioData = vi.fn().mockRejectedValue(new Error('codec')); });
  await expect(prepareAudio({ arrayBuffer: async () => new ArrayBuffer(1) } as Blob)).rejects.toThrow('codec');
  expect(close).toHaveBeenCalledOnce(); vi.unstubAllGlobals();
});

export function encodeWav(buffer: AudioBuffer): Blob {
  if (!Number.isFinite(buffer.duration) || buffer.duration < 1 || buffer.duration > 65 ||
      buffer.sampleRate < 8000 || buffer.sampleRate > 96000 || buffer.numberOfChannels < 1) {
    throw new Error('Unsupported audio');
  }
  const result = new ArrayBuffer(44 + buffer.length * 2);
  const view = new DataView(result);
  const write = (offset: number, text: string) => [...text].forEach((char, i) => view.setUint8(offset + i, char.charCodeAt(0)));
  write(0, 'RIFF'); view.setUint32(4, result.byteLength - 8, true); write(8, 'WAVE');
  write(12, 'fmt '); view.setUint32(16, 16, true); view.setUint16(20, 1, true);
  view.setUint16(22, 1, true); view.setUint32(24, buffer.sampleRate, true);
  view.setUint32(28, buffer.sampleRate * 2, true); view.setUint16(32, 2, true);
  view.setUint16(34, 16, true); write(36, 'data'); view.setUint32(40, buffer.length * 2, true);
  const channels = Array.from({ length: buffer.numberOfChannels }, (_, i) => buffer.getChannelData(i));
  for (let i = 0; i < buffer.length; i++) {
    const average = channels.reduce((sum, channel) => sum + channel[i], 0) / channels.length;
    const sample = Math.max(-1, Math.min(1, average));
    view.setInt16(44 + i * 2, Math.round(sample * (sample < 0 ? 32768 : 32767)), true);
  }
  return new Blob([result], { type: 'audio/wav' });
}

export async function prepareAudio(blob: Blob): Promise<Blob> {
  // decodeAudioData needs a complete recording. Some browsers cannot decode their
  // chosen recording codec; fail recoverably and keep local review in that case.
  const context = new AudioContext();
  try {
    const decoded = await context.decodeAudioData(await blob.arrayBuffer());
    return encodeWav(decoded);
  } finally {
    await context.close();
  }
}

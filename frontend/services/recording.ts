export interface Recording {
  videoBlob: Blob;
  audioBlob: Blob;
  durationSeconds: number;
}

export function startCapture(
  stream: MediaStream,
  complete: (recording: Recording) => void,
  failed: () => void,
  remaining: (seconds: number) => void,
): { stop: () => void; cancel: () => void } {
  const recorders: MediaRecorder[] = [];
  const chunks: Blob[][] = [[], []];
  let stopping = false;
  let cancelled = false;
  let finished = false;
  let stopped = 0;
  let startedAt = 0;
  let durationSeconds = 0;
  let timeout: ReturnType<typeof setTimeout> | undefined;
  let interval: ReturnType<typeof setInterval> | undefined;
  const clearTimers = () => { clearTimeout(timeout); clearInterval(interval); };
  const release = () => stream.getTracks().forEach(track => track.stop());
  const cancel = () => {
    if (cancelled || finished) return;
    cancelled = true;
    clearTimers();
    for (const recorder of recorders) {
      recorder.onstop = null;
      recorder.onerror = null;
      recorder.ondataavailable = null;
      try { if (recorder.state !== 'inactive') recorder.stop(); } catch { /* Release tracks even if the browser recorder failed. */ }
    }
    release();
  };
  const fail = () => { if (!cancelled && !finished) { cancel(); failed(); } };
  const stop = () => {
    if (stopping || cancelled || finished) return;
    stopping = true;
    durationSeconds = (performance.now() - startedAt) / 1000;
    clearTimers();
    try {
      for (const recorder of recorders) {
        if (recorder.state !== 'inactive') recorder.stop();
      }
    } catch { fail(); }
  };
  try {
    // Negotiate each track's container separately; never label MP4 bytes WebM.
    const choose = (types: string[]) => types.find(type => MediaRecorder.isTypeSupported(type));
    const videoType = choose(['video/webm;codecs=vp8,opus', 'video/webm', 'video/mp4']);
    const audioType = choose(['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus', 'audio/mp4']);
    if (!videoType || !audioType) throw new Error('Unsupported recording format');
    recorders.push(new MediaRecorder(stream, { mimeType: videoType }));
    recorders.push(new MediaRecorder(new MediaStream(stream.getAudioTracks()), { mimeType: audioType }));
    recorders.forEach((recorder, i) => {
      recorder.ondataavailable = event => { if (!cancelled && event.data.size) chunks[i].push(event.data); };
      recorder.onerror = fail;
      recorder.onstop = () => {
        if (cancelled || finished) return;
        if (!stopping) stop();
        stopped += 1;
        if (stopped !== 2) return;
        if (chunks.some(parts => !parts.length) || durationSeconds < 1 || durationSeconds > 65) { fail(); return; }
        finished = true;
        clearTimers();
        release();
        complete({
          videoBlob: new Blob(chunks[0], { type: recorders[0].mimeType }),
          audioBlob: new Blob(chunks[1], { type: recorders[1].mimeType }),
          durationSeconds,
        });
      };
    });
    startedAt = performance.now();
    recorders.forEach(recorder => recorder.start());
    timeout = setTimeout(stop, 60_000);
    interval = setInterval(() => remaining(Math.max(0, Math.ceil(60 - (performance.now() - startedAt) / 1000))), 250);
  } catch {
    fail();
  }
  return { stop, cancel };
}

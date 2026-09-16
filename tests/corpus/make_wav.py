import wave
import struct
import math

def generate_wav(filename, duration_sec=1, sample_rate=44100):
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(duration_sec * sample_rate):
            # 440 Hz sine wave
            value = int(32767.0 * math.sin(2.0 * math.pi * 440.0 * i / sample_rate))
            data = struct.pack('<h', value)
            wav_file.writeframesraw(data)

if __name__ == "__main__":
    generate_wav("c:/Users/sehri/OneDrive/Desktop/portfolio project/adaptive-communication-coach/tests/corpus/test_audio.wav")

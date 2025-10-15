# project_alpha_tts_temp.py
import numpy as np
import soundfile as sf
from scipy.signal import butter, lfilter
import tempfile
import os

class ChefsKissTTS:
    def __init__(self, sr=22050):
        self.sr = sr
        self.base_freq = 100         # deep base pitch
        self.harmonics = [1, 2, 3]   # harmonics for richness

    def text_to_phonemes(self, text):
        phonemes = []
        for c in text:
            if c.isalpha():
                phonemes.append(ord(c) % 40 + 60)
            elif c in ",;:":
                phonemes.append(30)  # slight pause
            elif c in ".!?":
                phonemes.append(20)  # longer pause
        if not phonemes:
            phonemes = [100]
        return phonemes

    def apply_lowpass_filter(self, audio, cutoff=700):
        nyq = 0.5 * self.sr
        normal_cutoff = cutoff / nyq
        b, a = butter(2, normal_cutoff, btype='low', analog=False)
        return lfilter(b, a, audio)

    def phonemes_to_wave(self, phonemes):
        audio = np.array([])
        for f in phonemes:
            duration = 0.25
            if f <= 30: duration = 0.35
            elif f <= 20: duration = 0.5

            t = np.linspace(0, duration, int(self.sr*duration))
            wave = np.zeros_like(t)

            for h in self.harmonics:
                freq = (self.base_freq + f) * h
                vibrato = 3 * np.sin(2*np.pi*5*t)
                wave += (0.25 / h) * np.sin(2*np.pi*(freq + vibrato)*t)

            envelope = np.linspace(0.1,1,len(t)) * np.linspace(1,0.9,len(t))
            wave *= envelope
            wave = self.apply_lowpass_filter(wave, cutoff=700)
            audio = np.concatenate([audio, wave])
        return audio

    def generate_temp_audio(self, text):
        """
        Generates temporary WAV audio file.
        Returns path. Caller must delete after use.
        """
        phonemes = self.text_to_phonemes(text)
        audio = self.phonemes_to_wave(phonemes)
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp_file.close()
        sf.write(tmp_file.name, audio, self.sr)
        return tmp_file.name

    def speak_and_cleanup(self, text):
        """
        Generates audio, returns bytes, then deletes temp file
        """
        file_path = self.generate_temp_audio(text)
        with open(file_path, "rb") as f:
            audio_bytes = f.read()
        os.remove(file_path)
        return audio_bytes


# -----------------------
# Example Usage
# -----------------------
if __name__ == "__main__":
    tts = ChefsKissTTS()
    audio_bytes = tts.speak_and_cleanup("Hello Mega Sanji AI! This is a temporary manly voice.")
    
    # Save temporarily to test
    with open("temp_test.wav", "wb") as f:
        f.write(audio_bytes)
    
    print("✅ Temporary audio generated and cleanup handled. Check temp_test.wav for testing.")
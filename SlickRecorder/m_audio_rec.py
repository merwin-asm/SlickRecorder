import pyaudio
import wave
import threading
from pynput import keyboard
from pydub import AudioSegment
import numpy as np
import time
import os


# Constants
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
OUTPUT_FILENAME = "mic.wav"
recording = True

def record_audio():
    global recording
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("Recording... Press ESC to stop.")

    frames = []

    os.system("touch .started_recording")    
    
    while recording:
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recording as a WAV file
    with wave.open(OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    quit()

def on_press(key):
    global recording
    if key == keyboard.Key.esc:
        recording = False

def listen_for_escape():
    global recording
    with keyboard.Listener(on_press=on_press) as listener:
        while recording:
            time.sleep(0.3)

if True:
    # Start the recording in a separate thread
    recording_thread = threading.Thread(target=record_audio)
    recording_thread.start()

    # Start listening for ESC key in the main thread
    listen_for_escape()


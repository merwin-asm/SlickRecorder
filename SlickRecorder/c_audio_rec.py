import subprocess
import pyaudio
import wave
from pynput import keyboard
import threading
import time
import os


# Audio recording parameters
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 0  # Set to 0 for indefinite recording

# File to save the recording
WAVE_OUTPUT_FILENAME = "pc.wav"

# Variable to control recording
recording = True

def on_press(key):
    global recording
    if key == keyboard.Key.esc:
        recording = False

def get_device_index_by_name(p, device_name):
    """Find the device index by device name."""
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if device_name in info['name']:
            return i
    return None

def record_audio():
    global recording
    audio = pyaudio.PyAudio()


    device_name = 'virtual_sink.monitor'

    # Find the device index
    device_index = get_device_index_by_name(audio, device_name)

    # Open stream from the virtual sink
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK,
                        input_device_index=device_index)

    frames = []

    print("Recording... Press ESC to stop.")
    os.system("touch .started_recording")
    while recording:
        data = stream.read(CHUNK)
        frames.append(data)

    # Stop recording
    print("Stopped recording.")
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recording
    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

def setup_virtual_sink():
    # Create a virtual sink and loopback module
    subprocess.run(["pactl", "load-module", "module-null-sink", "sink_name=virtual_sink"], check=True)
    subprocess.run(["pactl", "load-module", "module-loopback", "sink=virtual_sink"], check=True)

def cleanup_virtual_sink():
    # Unload the virtual sink and loopback module
    subprocess.run(["pactl", "unload-module", "module-loopback"], check=True)
    subprocess.run(["pactl", "unload-module", "module-null-sink"], check=True)

def main():
    setup_virtual_sink()
    
    # Wait a bit to ensure the sink is set up
    time.sleep(1)

    # Set up key listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    # Start recording in a separate thread
    record_thread = threading.Thread(target=record_audio)
    record_thread.start()

    # Wait for recording to finish
    record_thread.join()
    listener.stop()
    
    cleanup_virtual_sink()

if __name__ == "__main__":
    main()


import speech_recognition as sr
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from pydub import AudioSegment

def extract_audio_from_video(video_path, audio_path):
    # Extract audio from the video
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_path)
    
    # Convert audio to WAV format using pydub (if necessary)
    audio_segment = AudioSegment.from_file(audio_path)
    audio_segment.export(audio_path, format="wav")
import numpy as np
import math

def transcribe_audio(audio_path):
    # Initialize recognizer
    recognizer = sr.Recognizer()
    
    # Load audio file
    audio = AudioSegment.from_file(audio_path)
    duration_ms = len(audio)
    
    # Split audio into segments (e.g., 4 seconds each)
    segment_length_ms = 4000  # 4 seconds
    captions = []
    
    for start_ms in range(0, duration_ms, segment_length_ms):
        end_ms = min(start_ms + segment_length_ms, duration_ms)
        segment = audio[start_ms:end_ms]
        segment_path = 'temp_segment.wav'
        segment.export(segment_path, format="wav")
        
        with sr.AudioFile(segment_path) as source:
            audio_data = recognizer.record(source)
            try:
                # Transcribe audio segment
                text = recognizer.recognize_google(audio_data)
                start_time = start_ms / 1000.0  # Convert milliseconds to seconds
                duration = (end_ms - start_ms) / 1000.0  # Convert milliseconds to seconds
                captions.append({
                    'text': text,
                    'start_time': start_time,
                    'duration': duration
                })
            except sr.UnknownValueError:
                print(f"Google Speech Recognition could not understand audio segment from {start_ms}ms to {end_ms}ms")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
    
    return captions

def transcribe_audio_(audio_path):
    # Initialize recognizer
    recognizer = sr.Recognizer()
    
    # Load audio file
    with sr.AudioFile(audio_path) as source:
        # Recognize the audio
        audio_data = recognizer.record(source)
        try:
            # Use Google's Web Speech API to transcribe audio
            text = recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            text = ""
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            text = ""
    
    # Return a single caption entry for the whole audio file
    return [{'text': text, 'start_time': 0, 'duration': 0}]
"""
def add_captions_to_video(video_path, output_path, captions):
    # Load the video file
    video = VideoFileClip(video_path)
    
    # Create text clips for each caption
    text_clips = []
    for caption in captions:
        print(f"Creating text clip: '{caption['text']}' from {caption['start_time']} for {caption['duration']} seconds")
        
        text_clip = TextClip(
            caption['text'], 
            fontsize=24, 
            color='white', 
            bg_color='transparent',
            size=video.size
        )
        text_clip = text_clip.set_duration(caption['duration']).set_start(caption['start_time'])
        text_clip = text_clip.set_position(('center', 'bottom'))

        text_clips.append(text_clip)
    
    # Overlay the text clips on the video
    final_video = CompositeVideoClip([video] + text_clips)
    
    # Write the final video to the output path
    final_video.write_videofile(output_path, codec='libx264', fps=24)
"""
# Paths to the input and output files
video_path = 'screen_recording.mp4'
audio_path = 'audio.wav'
output_path = 'screen_recording.mp4'

# Extract audio from video
extract_audio_from_video(video_path, audio_path)

# Transcribe audio to get captions
captions = transcribe_audio(audio_path)
print(captions)
def add_captions_to_video(video_path, output_path, captions):
    # Load the video file
    video = VideoFileClip(video_path)
    
    # Create text clips for each caption
    text_clips = []
    for caption in captions:
        print(f"Creating text clip: '{caption['text']}' from {caption['start_time']} for {caption['duration']} seconds")
        
        text_clip = TextClip(
            caption['text'], 
            fontsize=35, 
            color='white', 
            bg_color='transparent',
            size=video.size
        )
        text_clip = text_clip.set_duration(caption['duration']).set_start(caption['start_time'])
        text_clip = text_clip.set_position(('center', 330))

        text_clips.append(text_clip)
    
    # Overlay the text clips on the video
    final_video = CompositeVideoClip([video] + text_clips)
    
    # Write the final video to the output path
    final_video.write_videofile(output_path, codec='libx264', fps=24)
# Add captions to the video
add_captions_to_video(video_path, output_path, captions)


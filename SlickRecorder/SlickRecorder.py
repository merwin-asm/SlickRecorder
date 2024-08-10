from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
import time
import os
import threading
import refine
import atexit
import json

""" .settings.json file :

        {
        'record_mic': self.recordMicCheckbox.isChecked(),
        'record_pc': self.recordPCCheckbox.isChecked(),
        'show_keyboard': self.showKeyboardCheckbox.isChecked(),
        'codec': self.codecComboBox.currentText(),
        'voice_caption': self.voiceCaptionCheckbox.isChecked(),
        'cursor':cursor,
        'saving_location': self.savingLocationInput.text(),
        'monitor': self.monitorComboBox.currentText(),
        'fullscreen': self.fullscreenCheckbox.isChecked(),
        'x_start':.....,
        'x_end': self.xEndInput.text() if not self.fullscreenCheckbox.isChecked() else None,
        'y_start': self.yStartInput.text() if not  self.fullscreenCheckbox.isChecked() else None,
        'y_end': self.yEndInput.text() if not self.fullscreenCheckbox.isChecked() else None
        }

"""


f = open(".settings.json", "r")
data =  json.loads(f.read())
f.close()



mic = data["record_mic"]
pc = data["record_pc"]
saving = data['saving_location']
refine_times = 4

caption = data['voice_caption']
cursor = data['cursor']
if data["show_keyboard"] == True:
    keyboard = 1
else:
    keyboard = 0

monitor = data['monitor']
if data['fullscreen']:
    x1, y1, x2, y2 = "None", 0,0,0
else:
    x1 , y1 , x2, y2 = data['x_start'], data['y_start'], data['x_end'], data['y_end']

codec = data['codec']

D = []
T = 0
src = ""



def ending():
    if (not mic) and pc:
        enable_mic()

    os.system("rm screen_recording_.mp4")

    if pc and mic:
        os.system("rm pc.wav")
    elif pc:
        os.system("rm pc.wav")
    elif mic:
        os.system("rm mic.wav")

    print("\nEXITED!")

atexit.register(ending)

def combine():
    global refine_times

    if mic and pc:
        refine.refine_audio("pc.wav", times=refine_times)
        audio = AudioFileClip("pc.wav")
    elif mic:
        refine.refine_audio("mic.wav", times=refine_times)
        audio = AudioFileClip("mic.wav")
    elif pc:
        audio = AudioFileClip("pc.wav")
    
    if mic or pc:
        video = VideoFileClip('screen_recording_.mp4')
        # Set the combined audio to the video
        video = video.set_audio(audio)
        # Export the final video
        video.write_videofile('screen_recording.mp4', codec='libx264', audio_codec='aac')

def current_path():
    x = os.path.abspath(__file__).split('/')
    x.pop()
    return "/".join(x)

# Define two functions to run simultaneously
def function_one():
    global x1, y1, x2, y2, monitor, keyboard, codec, cursor
    os.system(f"python3 {current_path()}/recorder.py {x1} {y1} {x2} {y2} {monitor} {keyboard} {codec} {cursor}")
    D.append(0)

def function_two():
    os.system(f"python3 {current_path()}/m_audio_rec.py")
    D.append(0)

def function_three():
    os.system(f"python3 {current_path()}/c_audio_rec.py")
    D.append(0)

def dissable_mic():
    global src

    os.system("pactl info | grep \"Default Source\" > .default_src_pactl")
    
    f = open(".default_src_pactl")
    data = f.read()
    f.close()
    
    os.system("rm .default_src_pactl")

    src = data.split(":")[1].replace("\n", "") 
    os.system(f"pactl get-source-volume {src} > .prev_src_vol")
    os.system(f"pactl set-source-volume {src} 0%")
    print(f"Temp Dissabled {src}")

def enable_mic():
    global src

    f = open(".prev_src_vol")
    data = f.read()
    f.close()

    per = "100%"
    for word in data.split():
        if word.endswith("%"):
            per = word
            break

    os.system(f"pactl set-source-volume {src} {per}")
    os.system("rm .prev_src_vol")
    print(f"Enabled {src} with {per}")

def main():
    global T
    # Create thread objects for each function
    thread_one = threading.Thread(target=function_one).start()
    T += 1
    
    if mic and pc:
        T += 1
        
        thread_three = threading.Thread(target=function_three)
        thread_three.start()
        #thread_three.join()
    elif mic and (not pc):
        T += 1
        
        thread_two = threading.Thread(target=function_two)
        thread_two.start()
        #thread_two.join()
    elif (not mic) and pc:
        T += 1

        dissable_mic()
        
        thread_three = threading.Thread(target=function_three)
        thread_three.start()
        #thread_three.join()
    

    while len(D) != T:
        time.sleep(0.3)

    print("Both functions have completed. Exiting the program.")


main()

os.system("ffmpeg -i screen_recording.mp4 -b:v 4M screen_recording_.mp4")

combine()

if caption:
    os.system("python3 {current_path()}/captions.py")

import time


if os.getcwd != saving:
    os.system(f"cp screen_recording.mp4 {saving}/screen_recording_{time.time()}.mp4")
    os.system("rm screen_recording.mp4")


import cv2
import numpy as np
import pyautogui
from PIL import Image
import time
import threading
from pynput import keyboard
from PIL import Image, ImageDraw, ImageFont
import sys
import os


a = sys.argv

if a[1] != "None":
    x1, y1 = int(a[1]) , int(a[2])
    x2, y2 = int(a[3]) , int(a[4])

def current_path():
    x = os.path.abspath(__file__).split('/')
    x.pop()
    return "/".join(x)


# Parameters
keyboard_ = a[6]
monitor_index = int(a[5])
output_file = 'screen_recording.mp4'
try:
    cursor_image_path = a[8]    
except:
    cursor_image_path = f'{current_path()}/cursor7.png'
cursor_size = (32, 32)  # Standard cursor size
codec = cv2.VideoWriter_fourcc(*a[7])
screen_size = pyautogui.size()

# monitor
from screeninfo import get_monitors
monitors = get_monitors()
monitor = monitors[monitor_index]
x1, y1 = monitor.x, monitor.y
x2, y2 = monitor.width + x1, monitor.height + y1


# Function to draw the custom cursor on the frame
def draw_cursor(frame, cursor_img_path, cursor_pos):
    cursor_img = Image.open(cursor_img_path).convert("RGBA")
    cursor_img = cursor_img.resize(cursor_size, Image.ANTIALIAS)  # Resize cursor image
    cursor_img_np = np.array(cursor_img)
    cursor_h, cursor_w, _ = cursor_img_np.shape
    y, x = cursor_pos

    # Ensure the cursor is within bounds
    y = min(max(0, y), frame.shape[0] - cursor_h)
    x = min(max(0, x), frame.shape[1] - cursor_w)

    # Overlay the cursor image
    for i in range(cursor_h):
        for j in range(cursor_w):
            if cursor_img_np[i, j, 3] > 0:  # Check alpha channel
                frame[y + i, x + j] = cursor_img_np[i, j, :3]


recording = True
pressed_keys = set()
key_text = ""

def on_press(key):
    global recording, pressed_keys, key_text

    try:
        key_name = key.char
    except AttributeError:
        key_name = str(key).replace('Key.', '')

    pressed_keys.add(key_name)
    
    # Record the key combination
    if pressed_keys:
        combination = '+'.join(sorted(pressed_keys))
        key_text = combination

    if key == keyboard.Key.esc:
        recording = False

def on_release(key):
    global pressed_keys
    
    try:
        key_name = key.char
    except AttributeError:
        key_name = str(key).replace('Key.', '')

    if key_name in pressed_keys:
        pressed_keys.remove(key_name)

    # Stop listener with ESC key
    if key == keyboard.Key.esc:
        return False


def listen_for_escape():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


esc_thread = threading.Thread(target=listen_for_escape)
esc_thread.start()

print("Screen Recording started. Press 'ESC' to stop recording.")
start_time = time.time()
frames = []
frame_times = []
key_text_frames = 4
key_text_counter = 0
current_key_text = ""

def add_key_text(frame, text):
    global keyboard_
    
    if keyboard_ == "0":
        return frame

    x = frame.shape[1] - int(frame.shape[1]/2) - 150
    y = frame.shape[0] - int(frame.shape[0]/2) + 100

    font_scale = 1
    font_thickness = 2
    font_color = (0 , 0 , 0)
    # Load the overlay image
    overlay_img = cv2.imread(f"{current_path()}/keyboard_text.png", cv2.IMREAD_UNCHANGED)  # Read image with alpha channel

    if overlay_img is None:
        raise FileNotFoundError(f"Image file 'keyboard_text.png' not found.")

    # Resize the overlay image to fit the frame if necessary
    h, w = overlay_img.shape[:2]
    if x + w > frame.shape[1] or y + h > frame.shape[0]:
        raise ValueError("The overlay image is out of bounds of the frame.")

    # Create a region of interest (ROI) in the frame
    roi = frame[y:y+h, x:x+w]

    # Split the overlay image into its color and alpha channels
    overlay_color = overlay_img[:, :, :3]
    overlay_alpha = overlay_img[:, :, 3] / 255.0

    # Blend the overlay image with the ROI
    for c in range(0, 3):
        roi[:, :, c] = (overlay_alpha * overlay_color[:, :, c] + (1 - overlay_alpha) * roi[:, :, c])

    # Add text to the overlay image
    text_position = (overlay_img.shape[1] - int(overlay_img.shape[1]/2)-50, overlay_img.shape[0]- 90)
    #cv2.putText(roi, text, text_position, fontHeight=font_scale, color=font_color, thickness=font_thickness)
    cv2.putText(roi, text, text_position, cv2.FONT_HERSHEY_DUPLEX, font_scale, font_color,font_thickness, cv2.LINE_AA)

    # Place the overlay image back onto the frame
    frame[y:y+h, x:x+w] = roi

    return frame

import os
while not os.path.isfile(".started_recording"):
    time.sleep(0.3)
while recording:
    # Record the start time for this frame
    frame_start_time = time.time()

    # Capture screen
    #screen = pyautogui.screenshot()
    screen = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))

    screen_np = np.array(screen)
    frame = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
    if a[1] != "None":
        frame = frame[y1:y2, x1:x2]

    # Get cursor position
    cursor_x, cursor_y = pyautogui.position()
    if a[1] == "None":
        # draw_cursor(frame, cursor_image_path, (cursor_y - cursor_size[1] // 2, cursor_x - cursor_size[0] // 2))
        draw_cursor(frame, cursor_image_path, (cursor_y - cursor_size[1] // 2 - x1, cursor_x - cursor_size[0] // 2 - y1))

    else:
        draw_cursor(frame, cursor_image_path, (cursor_y - cursor_size[1] // 2 - x1, cursor_x - cursor_size[0] // 2 - y1))
    
    if key_text != "":
        if current_key_text != key_text:
            current_key_text =  key_text
            key_text_counter = 0

        if key_text_counter == key_text_frames:
            key_text_counter = 0
            key_text = ""
            current_key_text = ""
        else:
            key_text_counter += 1
            print(key_text)
            frame = add_key_text(frame, key_text.title())

    # Store the frame and the timestamp
    frames.append(frame)
    frame_times.append(frame_start_time - start_time)



print("Recording stopped.")

# Calculate the average frame rate based on actual times
duration = frame_times[-1] if frame_times else 0
average_frame_rate = len(frames) / duration if duration > 0 else 0
print(f"Average frame rate: {average_frame_rate:.2f} fps")

# Write video with variable frame rate
if frames:
    first_frame = frames[0]
    height, width, _ = first_frame.shape
    video_writer = cv2.VideoWriter(output_file, codec, average_frame_rate, (width, height))
        
    for frame in frames:
        video_writer.write(frame)

video_writer.release()
cv2.destroyAllWindows()


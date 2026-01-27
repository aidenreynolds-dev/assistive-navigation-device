#!/usr/bin/env python3
"""
Vision Assistance Hat – Main Controller Script
This program runs on a Raspberry Pi. It captures an image when a physical button
is pressed, sends the image to OpenAI for analysis, speaks the response out loud,
and uses a vibration motor for haptic feedback.

The code below is heavily commented for clarity and grading.
"""

import RPi.GPIO as GPIO
import subprocess
import base64
from time import sleep
from threading import Thread
from queue import Queue
from openai import OpenAI
import os

# ===============================
# PIN CONFIGURATION (GPIO)
# ===============================
# Physical pin numbers (BOARD mode)
BtnPin = 11   # Push button input pin
VibPin = 29   # Vibration motor output pin

# ===============================
# OPENAI MODEL + FILE SETTINGS
# ===============================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # API key replaced later for safety
MODEL = "gpt-5-nano-2025-08-07"         # Vision-capable lightweight model
IMAGE_PATH = "captured_image.jpg"       # Temporary saved camera image
RESOLUTION = "640x480"                  # Webcam capture resolution

# ===============================
# CAMERA CAPTURE FUNCTION
# ===============================
def capture_image(path: str):
    """Capture an image using fswebcam and save it to disk."""
    print(" Capturing image...")

    # -r sets the resolution
    # -S 2 skips first 2 frames for clarity
    # --no-banner removes timestamp/banner overlay
    subprocess.run([
        "fswebcam", "-r", RESOLUTION, "-S", "2", "--no-banner", path
    ], check=True)

    print(" Image captured successfully!")

# ===============================
# CONVERT IMAGE TO BASE64 DATA URL
# ===============================
def to_data_url(path: str) -> str:
    """Read the image file and convert it into a base64 data URL."""
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"

# ===============================
# EXTRACT TEXT FROM OPENAI RESPONSE
# ===============================
def extract_text(resp):
    """Safely extract text content from the OpenAI response object."""
    try:
        # Some models return resp.output_text
        if hasattr(resp, "output_text"):
            return resp.output_text.strip()

        # Others return nested content
        for item in getattr(resp, "output", []):
            for part in getattr(item, "content", []):
                if getattr(part, "type", "") in ("output_text", "text"):
                    return part.text.strip()
    except Exception:
        pass

    # Fallback (should rarely be needed)
    return str(resp)

# ===============================
# SEND IMAGE TO OPENAI + GET DESCRIPTION
# ===============================
def analyze_image():
    """Capture an image and ask the OpenAI model to describe it."""
    capture_image(IMAGE_PATH)

    data_url = to_data_url(IMAGE_PATH)
    prompt = "Describe what’s visible in one short sentence (<= 15 words)."

    print(" Sending image to OpenAI...")

    resp = client.responses.create(
        model=MODEL,
        reasoning={"effort": "low"},
        max_output_tokens=256,
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},      # Instruction text
                {"type": "input_image", "image_url": data_url} # Encoded image
            ]
        }],
    )

    description = extract_text(resp)
    print(" AI says:", description)
    return description

# ===============================
# SPEECH OUTPUT USING ESPEAK
# ===============================
def speak(text: str):
    """Convert text to speech and play it via headphone jack."""
    safe_text = text.replace('"', '').replace("'", "")  # Avoid breaking shell command

    try:
        # espeak generates audio → piped to aplay → played out loud
        subprocess.Popen(
            f'espeak "{safe_text}" --stdout | aplay -D plughw:2,0',
            shell=True,
            stderr=subprocess.DEVNULL
        )
        print(f" Speaking: {safe_text}")
    except Exception as e:
        print(" Speech failed:", e)

# ===============================
# VIBRATION FEEDBACK
# ===============================
def vibrate(duration=0.3):
    """Activate the vibration motor for haptic feedback."""
    GPIO.output(VibPin, GPIO.HIGH)
    sleep(duration)
    GPIO.output(VibPin, GPIO.LOW)

# ===============================
# INITIAL GPIO SETUP
# ===============================
def setup():
    """Configure GPIO pins and prepare hardware."""
    GPIO.setmode(GPIO.BOARD)  # Use physical board pin numbers

    # Button uses internal pull-up → pressed = LOW
    GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Vibration motor output pin
    GPIO.setup(VibPin, GPIO.OUT)
    GPIO.output(VibPin, GPIO.LOW)

    print(" Setup complete. Waiting for button press...")

# ===============================
# TASK QUEUE SYSTEM
# ===============================
# Queue prevents multiple button presses from running at once.
task_queue = Queue()

# ===============================
# BUTTON EVENT CALLBACK
# ===============================
def button_pressed(channel):
    """Triggered when button is physically pressed."""
    print(" Button pressed! Queuing capture task...")
    vibrate(0.2)  # Quick confirmation vibration
    task_queue.put("capture")

# ===============================
# BACKGROUND TASK PROCESSOR
# ===============================
def process_tasks():
    """Continuously process queued tasks (image capture + AI analysis)."""
    while True:
        if not task_queue.empty():
            task = task_queue.get()

            if task == "capture":
                try:
                    description = analyze_image()

                    # Success feedback
                    vibrate(0.5)
                    print(" Description:", description)
                    speak(description)

                except Exception as e:
                    # Error feedback: long vibration
                    print(" Error:", e)
                    vibrate(1.0)

        sleep(0.1)  # Avoid CPU overload

# ===============================
# CLEAN SHUTDOWN HANDLER
# ===============================
def destroy():
    """Safely shut down GPIO before exiting."""
    GPIO.output(VibPin, GPIO.LOW)
    GPIO.cleanup()
    print(" GPIO cleaned up.")

# ===============================
# MAIN PROGRAM ENTRY
# ===============================
if __name__ == '__main__':
    setup()

    # Detect falling edge (button press → LOW)
    GPIO.add_event_detect(
        BtnPin,
        GPIO.FALLING,
        callback=button_pressed,
        bouncetime=500  # Debounce to avoid multiple triggers
    )

    try:
        process_tasks()  # Infinite loop
    except KeyboardInterrupt:
        # Ctrl+C → clean exit
        destroy()


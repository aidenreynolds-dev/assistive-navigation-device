# assistive-navigation-device

A wearable assistive device using Raspberry Pi and AI to help visually impaired users navigate their surroundings using audio and haptic feedback.

---

## Overview
This project is a wearable system that captures images of the user's surroundings and uses artificial intelligence to describe them in real time. The output is delivered through audio and vibration feedback, allowing visually impaired users to better understand and navigate their environment.

---

## Problem Statement
Visually impaired individuals often face challenges such as identifying objects, reading labels, and navigating unfamiliar spaces. Many existing solutions are expensive, slow, or overly complex. This project aims to provide an affordable, portable, and easy-to-use alternative.

---

## Solution
The device consists of a camera mounted on a wearable hat, a wristband button for input, and speaker/vibration outputs.

When the button is pressed:
1. The camera captures an image.
2. The image is sent to the OpenAI API for analysis.
3. The response is converted into text.
4. The text is converted into speech.
5. Audio and haptic feedback are delivered to the user.

---

## Technology Stack
- Raspberry Pi / Arduino
- Python
- OpenAI API
- Camera Module
- Text-to-Speech Engine
- Speaker & Vibration Motor

---

## Features
- One-button operation
- Real-time AI image analysis
- Audio and vibration feedback
- Wearable and portable design
- Modular software architecture

---

## Project Development Process
1. User research and ideation
2. Product research and concept design
3. Hardware implementation
4. Software development
5. Prototyping and assembly
6. User testing and iteration

---

## Demo
https://www.youtube.com/watch?v=k_EpGdcFMfQ

Images and videos are available in the media folder.

---

## My Role
- Developed core Python logic
- Integrated OpenAI API
- Assisted with hardware setup
- Participated in user testing and analysis

---

## Results and Future Work
- Successfully tested with multiple users
- Improved stability and comfort based on feedback
- Planned improvements include Bluetooth audio support and adjustable camera positioning

---

## Setup Instructions
1. Clone this repository
2. Install required Python dependencies
3. Connect hardware components
4. Configure OpenAI API key
5. Run the main program

Detailed setup instructions are available in the docs folder.

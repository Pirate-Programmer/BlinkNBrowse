# Eye Blink & Gesture Controlled USB Keyboard

--> Using Raspberry Pi 4 model B this is super portable handy lazy control of PC

## Requirements

**Hardware:**  
- Raspberry Pi 4  
- USB webcam or Raspberry Pi Camera  
- USB-C cable  

**Software:**  
- Python 3.11 (installed via pyenv)  

**Additional Setup:**  
- Keyboard gadget script to make Pi act as a USB HID keyboard  

## Functionality

- Detects **eye blinks** and **hand gestures** using **MediaPipe** and **OpenCV**  
- Sends **keyboard inputs** to the connected host laptop over **USB HID protocol**  
- All detection scripts can be **automatically launched on boot** using **systemd**  

## Communication Overview

- Raspberry Pi acts as a **USB HID device** over the USB-C connection  
- Eye blink and gesture events are converted into **HID reports**  
- Host computer receives these reports as **keyboard input events**  
- Communication is **host-driven, packet-based, low-latency, and reliable**  

## Tech Stack

- **Python 3.11** (via pyenv)  
- **MediaPipe** for computer vision tracking  
- **OpenCV** for image capture and processing  
- **USB HID gadget** framework on Raspberry Pi  
- **systemd** for automated script execution on boot  

## Usage

1. Run the keyboard gadget setup on the Raspberry Pi:  
   ```bash
   sudo ./make_into_keyboard.sh

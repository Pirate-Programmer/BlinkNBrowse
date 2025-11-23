#Run On RaspberryPi after doing the settings so its recongnized as a hid keyboard 
import time

# Path to the HID device
HID_DEVICE = "/dev/hidg0"

# HID key codes 
KEYS = {
    # Letters
    'a': 0x04, 'b': 0x05, 'c': 0x06, 'd': 0x07, 'e': 0x08, 'f': 0x09, 'g': 0x0A,
    'h': 0x0B, 'i': 0x0C, 'j': 0x0D, 'k': 0x0E, 'l': 0x0F, 'm': 0x10, 'n': 0x11,
    'o': 0x12, 'p': 0x13, 'q': 0x14, 'r': 0x15, 's': 0x16, 't': 0x17, 'u': 0x18,
    'v': 0x19, 'w': 0x1A, 'x': 0x1B, 'y': 0x1C, 'z': 0x1D,

    # Numbers (top row)
    '1': 0x1E, '2': 0x1F, '3': 0x20, '4': 0x21, '5': 0x22, '6': 0x23,
    '7': 0x24, '8': 0x25, '9': 0x26, '0': 0x27,

    # Numpad
    'numlock': 0x53, 'kp/': 0x54, 'kp*': 0x55, 'kp-': 0x56, 'kp+': 0x57, 'kpenter': 0x58,
    'kp1': 0x59, 'kp2': 0x5A, 'kp3': 0x5B, 'kp4': 0x5C, 'kp5': 0x5D, 'kp6': 0x5E,
    'kp7': 0x5F, 'kp8': 0x60, 'kp9': 0x61, 'kp0': 0x62, 'kp.': 0x63,

    # Control keys
    'enter': 0x28, 'esc': 0x29, 'backspace': 0x2A, 'tab': 0x2B, 'space': 0x2C,
    'minus': 0x2D, 'equal': 0x2E, 'leftbrace': 0x2F, 'rightbrace': 0x30,
    'semicolon': 0x33, 'apostrophe': 0x34, 'grave': 0x35, 'comma': 0x36,
    'dot': 0x37, 'slash': 0x38, 'capslock': 0x39,

    # Function keys
    'f1': 0x3A, 'f2': 0x3B, 'f3': 0x3C, 'f4': 0x3D, 'f5': 0x3E, 'f6': 0x3F,
    'f7': 0x40, 'f8': 0x41, 'f9': 0x42, 'f10': 0x43, 'f11': 0x44, 'f12': 0x45,

    # Modifiers
    'ctrl': 0x01, 'shift': 0x02, 'alt': 0x04, 'gui': 0x08
}

MODIFIER = {
    'ctrl': 0x01,
    'shift': 0x02,
    'alt': 0x04,
    'gui': 0x08
}


class hid_keyboard:

    def __init__(self):
        self.hid = open(HID_DEVICE, 'wb')
        self.modifier = 0          # currently held modifier keys
        self.pressed_keys = []     # currently held non-modifier keys

    def press_key(self, key_code=0, modifier=0):
        """Hold a key or modifier without releasing others."""
        self.modifier |= modifier
        if key_code != 0 and key_code not in self.pressed_keys:
            self.pressed_keys.append(key_code)
        self._send_report()

    def release_key(self, key_code=0, modifier=0):
        """Release a specific key or modifier, keep others held."""
        self.modifier &= ~modifier
        if key_code in self.pressed_keys:
            self.pressed_keys.remove(key_code)
        self._send_report()

    def release_keys(self):
        """Release all keys/modifiers."""
        self.modifier = 0
        self.pressed_keys = []
        self._send_report()

    def send_key(self, key_code, modifier=0, hold_time=0.05):
        """Press and release a key with optional modifier."""
        self.press_key(key_code, modifier)
        time.sleep(hold_time)
        self.release_key(key_code, modifier)
        time.sleep(0.01)

    def type_string(self, text):
        """Type letters/numbers (a-z, 0-9, space)."""
        for char in text.lower():
            if char == ' ':
                self.send_key(KEYS['space'])
            elif char in KEYS:
                self.send_key(KEYS[char])
            else:
                print(f"Character '{char}' not mapped, skipping")

    # --- Chrome/browser helpers ---
    def right_tab(self):
        self.send_key(KEYS["tab"], MODIFIER["ctrl"])

    def hold_alt(self):
        self.press_key(0x00, MODIFIER["alt"])

    def release_alt(self):
        self.release_key(modifier=MODIFIER["alt"])

    def send_tab(self):
        self.send_key(KEYS["tab"])

    # --- Mouse key helpers ---
    def right_click(self):
        self.press_key(KEYS['kp/'])
        self.send_key(KEYS['kp5'])

    def double_click(self):
        self.send_key(KEYS['kp+'])

    # --- Internal report ---
    def _send_report(self):
        # HID report is 8 bytes: [modifier, reserved, k1..k6]
        keys = self.pressed_keys[:6] + [0]*(6 - len(self.pressed_keys[:6]))
        report = bytes([self.modifier, 0x00] + keys)
        report += bytes(8 - len(report))
        self.hid.write(report)
        self.hid.flush()








        

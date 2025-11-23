k#!/bin/bash
# filename: setup_keyboard_gadget.sh
# Run as root: sudo ./setup_keyboard_gadget.sh

set -e

GADGET_DIR=/sys/kernel/config/usb_gadget/keyboard

# Load libcomposite if not already loaded
if ! lsmod | grep -q libcomposite; then
    echo "Loading libcomposite module..."
    sudo modprobe libcomposite
    sleep 1
fi

# Ensure usb_gadget exists
if [ ! -d "/sys/kernel/config/usb_gadget" ]; then
    echo "Error: /sys/kernel/config/usb_gadget does not exist. Is configfs mounted?"
    exit 1
fi

# Remove existing gadget if present
if [ -d "$GADGET_DIR" ]; then
    echo "Cleaning up existing gadget..."
    if [ -f "$GADGET_DIR/UDC" ]; then
        echo "" > "$GADGET_DIR/UDC" || true
    fi
    rm -rf "$GADGET_DIR"
fi

# Create gadget folder
mkdir -p "$GADGET_DIR"
cd "$GADGET_DIR"

# Device descriptor
printf "%s" 0x1d6b > idVendor
printf "%s" 0x0104 > idProduct
printf "%s" 0x0100 > bcdDevice
printf "%s" 0x0200 > bcdUSB

# Strings
mkdir -p strings/0x409
echo "fedcba9876543210" > strings/0x409/serialnumber
echo "Raspberry Pi" > strings/0x409/manufacturer
echo "USB Keyboard" > strings/0x409/product

# Configuration
mkdir -p configs/c.1/strings/0x409
echo "Config 1" > configs/c.1/strings/0x409/configuration
echo 120 > configs/c.1/MaxPower

# HID function
mkdir -p functions/hid.usb0
echo 1 > functions/hid.usb0/protocol
echo 1 > functions/hid.usb0/subclass
echo 8 > functions/hid.usb0/report_length

# HID report descriptor using printf (safer than echo)
printf '\x05\x01\x09\x06\xa1\x01\x05\x07\x19\xe0\x29\xe7\x15\x00\x25\x01\x75\x01\x95\x08\x81\x02\x95\x01\x75\x08\x81\x01\x95\x05\x75\x01\x05\x08\x19\x01\x29\x05\x91\x02\x95\x01\x75\x03\x91\x01\x95\x06\x75\x08\x15\x00\x25\x65\x05\x07\x19\x00\x29\x65\x81\x00\xc0' > functions/hid.usb0/report_desc

# Link HID function to configuration
ln -s functions/hid.usb0 configs/c.1/

# Wait a tiny bit before binding UDC to avoid "device busy"
sleep 1

# Bind gadget to UDC
UDC_NAME=$(ls /sys/class/udc | head -n1)
echo "$UDC_NAME" > UDC

echo "Keyboard gadget setup complete!"
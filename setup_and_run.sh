#!/bin/bash

# Install required system dependencies
apt-get update
apt-get install -y \
    libxcb-cursor0 \
    libxcb-xinerama0 \
    libxcb-randr0 \
    libxcb-xtest0 \
    libxcb-shape0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0

# Run the application
python main.py
#!/bin/bash

# Prompt for installation directory
echo "Enter installation directory (leave blank for current directory):"
read install_dir

# Default to current directory if empty input
install_dir="${install_dir:-$(pwd)}"

# Install Python (assuming Python 3 is available)
sudo apt update
sudo apt install python3 python3-pip -y

# Clone repository
echo "Cloning repository..."
git clone https://github.com/justinsanjp/pytube "$install_dir/pytube"
cd "$install_dir/pytube"

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Create shortcut on desktop
echo "Create shortcut on desktop? (yes/no)"
read create_desktop_shortcut

if [ "$create_desktop_shortcut" = "yes" ]; then
    desktop_dir="$HOME/Desktop"
    cp "$install_dir/pytube/pytube.desktop" "$desktop_dir"
    echo "Desktop shortcut created."
fi

# Create shortcut in application menu (for GNOME)
echo "Create shortcut in application menu? (yes/no)"
read create_menu_shortcut

if [ "$create_menu_shortcut" = "yes" ]; then
    applications_dir="$HOME/.local/share/applications"
    cp "$install_dir/pytube/pytube.desktop" "$applications_dir"
    echo "Application menu shortcut created."
fi

# Run pytube
echo "Run pytube? (yes/no)"
read run_pytube

if [ "$run_pytube" = "yes" ]; then
    python3 "$install_dir/pytube/main.py"
fi

echo "Setup completed."

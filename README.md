# Digital Picture Frame Web App

A simple Python Flask application to turn your Raspberry Pi (or any computer) into a digital picture frame with web upload capabilities.

## Features
- **Slideshow:** Automatically cycles through photos in full screen.
- **Web Upload:** Upload photos from your phone or computer via the web interface.
- **Auto-Scan:** Automatically detects new photos added to the folder.

## Installation

1.  **Install Python:** Ensure Python 3 is installed (usually pre-installed on Raspberry Pi).
2.  **Run the Setup Script (Recommended for Linux/Raspberry Pi):**
    This script automatically creates a virtual environment and installs dependencies, solving "externally-managed-environment" errors.
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```

3.  **Manual Installation (Alternative):**
    *   **Create a Virtual Environment:**
        *   **Linux/macOS:**
            ```bash
            python3 -m venv venv
            source venv/bin/activate
            ```
        *   **Windows:**
            ```bash
            python -m venv venv
            venv\Scripts\activate
            ```
    *   **Install Dependencies:**
        ```bash
        pip install -r requirements.txt
        ```

## Usage

1.  **Start the Application:**
    *   **With Virtual Environment Activated:**
        ```bash
        python app.py
        ```
    *   **Directly:**
        ```bash
        ./venv/bin/python app.py  # Linux/macOS
        .\venv\Scripts\python app.py  # Windows
        ```
2.  **Access the Frame:**
    - On the device itself: Open a browser and go to `http://localhost:5000`
    - From another device: Open a browser and go to `http://<IP-ADDRESS-OF-PI>:5000` (e.g., `http://192.168.1.100:5000`)

3.  **Upload Photos:**
    - Hover your mouse (or tap) near the bottom-right corner of the screen to reveal the "Choose Files" button.
    - Select photos to upload. They will automatically be added to the slideshow.

## Configuration
- **Photos Folder:** Photos are stored in `static/photos`. You can manually copy images there as well.
- **Slideshow Speed:** Edit `templates/index.html` and change `const slideInterval = 5000;` (milliseconds).

## Local Display (Feh) Integration
This application can automatically run a local slideshow using `feh` on the device (e.g., Raspberry Pi connected to a screen).
- **Prerequisites:** Ensure `feh` is installed (`sudo apt install feh`).
- **Usage:** The slideshow starts automatically when the app runs. You can also control it via the web interface (Start/Stop/Restart buttons in the bottom-right menu).
- **Note:** `feh` requires a graphical environment. If you are on a "Lite" OS, you may need to install X11 or use a desktop version.

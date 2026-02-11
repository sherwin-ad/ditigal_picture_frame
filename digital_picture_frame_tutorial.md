# Digital Picture Frame Tutorial

This guide uses **Raspberry Pi OS** and the lightweight image viewer **`feh`** to create a standalone photo frame that starts automatically using a **Raspberry Pi 3 Model B**.

## 1. Required Components

Since you already have the **Raspberry Pi 3 Model B**, you will need:

*   **MicroSD Card:** 8GB or larger (Class 10 recommended).
*   **Power Supply:** Official Raspberry Pi Micro USB power supply (2.5A / 5.1V).
*   **Display:** Any monitor or TV with HDMI input.
    *   *Recommendation:* A standard 1080p computer monitor or the official **Raspberry Pi Touch Display** (requires a specific case).
*   **HDMI Cable:** To connect the Pi to the display.
*   **Case:** Official Raspberry Pi 3 Case (or one that mounts to the back of your monitor/VESA mount).
*   **USB Drive:** For easily transferring photos.
*   **Keyboard & Mouse:** Required only for the initial setup.

## 2. Install Raspberry Pi OS

We will use the **Raspberry Pi Imager**, the official tool for writing the operating system.

1.  **Download Imager:** on your main computer, download [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
2.  **Insert SD Card:** Plug your MicroSD card into your computer.
3.  **Choose OS:** Open Imager. Click **"Choose OS"**.
    *   Select **Raspberry Pi OS (Legacy, 32-bit)**.
    *   *Why Legacy?* It uses the X11 window system by default, which is much easier to configure for slideshow scripts than the newer Wayland-based "Bookworm" release.
4.  **Choose Storage:** Click **"Choose Storage"** and select your SD card.
5.  **Write:** Click **"Next"** then **"Write"**. Wait for the verification to finish.

## 3. Initial Setup

1.  Insert the MicroSD card into your Raspberry Pi.
2.  Connect the display, keyboard, mouse, and finally the power.
3.  Follow the **Welcome Wizard** on screen:
    *   Set your Country, Language, and Timezone.
    *   Create a username (e.g., `admin`) and password.
    *   Connect to your Wi-Fi network.
    *   Let the system check for updates (this ensures you have the latest software).
4.  **Restart** when prompted.

## 4. Transfer Photos

We will create a specific folder for your slideshow images.

1.  Open the **File Manager** (folder icon on the taskbar).
2.  Right-click in the empty space and create a **New Folder** named `frame_photos`.
3.  Insert your USB drive containing your pictures into the Pi.
4.  Copy your photos from the USB drive into the `/home/admin/frame_photos` folder.

## 5. Install the Slideshow Viewer

We will use `feh`, a fast and simple image viewer that runs from the command line but displays on the desktop.

1.  Open the **Terminal** (black icon on the taskbar).
2.  Type the following command and press **Enter** (you may need to type `y` to confirm):
    ```bash
    sudo apt update && sudo apt install feh -y
    ```
3.  **Test it:** Type this command to see if your slideshow works:
    ```bash
    feh -Y -x -q -D 5 -B black -F -Z -z -r /home/admin/frame_photos
    ```
    *   **Explanation of commands:**
        *   `-Y`: Hide pointer
        *   `-x`: Borderless
        *   `-q`: Quiet mode (no errors)
        *   `-D 5`: Delay of 5 seconds per slide
        *   `-B black`: Black background
        *   `-F`: Fullscreen
        *   `-Z`: Auto-zoom
        *   `-z`: Randomize order
        *   `-r`: Recursive (search all subfolders)
4.  Press **Esc** on your keyboard to exit the slideshow.

## 6. Configure Auto-Start

We need the Pi to log in automatically and start the slideshow.

### Step A: Enable Auto-Login
1.  Open Terminal and type:
    ```bash
    sudo raspi-config
    ```
2.  Select **1 System Options** > **S5 Boot / Auto Login**.
3.  Select **B4 Desktop Autologin**.
4.  Select **Finish** and reboot if asked.

### Step B: Create Autostart Script
1.  Open Terminal.
2.  Create the autostart directory (just in case it doesn't exist):
    ```bash
    mkdir -p /home/admin/.config/autostart
    ```
3.  Create a new shortcut file:
    ```bash
    nano /home/admin/.config/autostart/slideshow.desktop
    ```
4.  Paste the following text into the editor:
    ```ini
    [Desktop Entry]
    Type=Application
    Name=Slideshow
    Exec=feh -Y -x -q -D 5 -B black -F -Z -z -r /home/admin/frame_photos
    StartupNotify=false
    Terminal=false
    ```
    *(Note: If you chose a username other than `admin`, update the path `/home/admin/...` accordingly)*.
5.  Save the file: Press **Ctrl+O**, **Enter**, then **Ctrl+X**.

## 7. Prevent Screen Sleep (Blanking)

By default, the screen will turn black after 10 minutes. We must disable this.

1.  Open the main **Raspberry Pi Menu** (top left).
2.  Go to **Preferences** > **Raspberry Pi Configuration**.
3.  Click the **Display** tab.
4.  Look for **Screen Blanking** and switch it to **Disable**.
5.  Click **OK**.

## 8. Final Launch

1.  Reboot your Raspberry Pi:
    ```bash
    sudo reboot
    ```
2.  The Pi should boot up, automatically log in to the desktop, and immediately launch your photo slideshow.

---

### Optional Enhancements

*   **Hide the Mouse Cursor:** If the mouse cursor stays visible despite the command, install `unclutter`:
    `sudo apt install unclutter`
*   **Remote Photo Updates:** To update photos without unplugging the USB, enable **SSH** in `raspi-config` > `Interface Options` and use a program like **FileZilla** on your PC to drag-and-drop new photos into the `frame_photos` folder over Wi-Fi.

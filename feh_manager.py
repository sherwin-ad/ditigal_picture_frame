import os
import subprocess
import threading
import time
import shutil
import platform

class FehController:
    def __init__(self, image_folder, delay=5):
        self.image_folder = image_folder
        self.delay = delay
        self.process = None
        self.running = False
        self.thread = None

    def _is_feh_installed(self):
        return shutil.which('feh') is not None

    def start(self):
        if self.running:
            print("Feh is already running.")
            return

        if not self._is_feh_installed():
            print("Error: 'feh' is not installed or not found in PATH.")
            print("Please install it (e.g., 'sudo apt install feh').")
            return

        # Check if we are on a system that likely has a display
        # (This is a rough check, mainly to avoid errors on headless servers or Windows dev environments)
        if platform.system() == 'Windows':
            print("Warning: 'feh' is a Linux application. It will not run on Windows.")
            return

        print(f"Starting feh slideshow in {self.image_folder}...")
        self.running = True
        self.thread = threading.Thread(target=self._run_feh)
        self.thread.daemon = True
        self.thread.start()

    def _run_feh(self):
        # Command arguments:
        # -F: Fullscreen
        # -Z: Zoom to fill screen
        # -Y: Hide pointer
        # -D: Slide delay
        # --reload: Reload filelist every <delay> seconds (or just checking periodically)
        # --auto-zoom: Zoom pictures to screen size
        
        # Note: --reload <int> checks directory for changes. 
        # using 5 seconds for reload check as well.
        
        cmd = [
            'feh',
            '-F', '-Z', '-Y',
            '-D', str(self.delay),
            '--reload', '2',  # Check for new files every 2 seconds
            self.image_folder
        ]

        # Set DISPLAY environment variable if not set (common issue when running from services/SSH)
        env = os.environ.copy()
        if 'DISPLAY' not in env:
            env['DISPLAY'] = ':0'

        try:
            self.process = subprocess.Popen(cmd, env=env)
            self.process.wait()
        except Exception as e:
            print(f"Error running feh: {e}")
        finally:
            self.running = False
            self.process = None

    def stop(self):
        if self.process and self.process.poll() is None:
            print("Stopping feh...")
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.running = False

    def restart(self):
        self.stop()
        time.sleep(1)
        self.start()

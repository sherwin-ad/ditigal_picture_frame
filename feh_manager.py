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

        # Set DISPLAY environment variable to target the main display (Raspberry Pi default is :0)
        env = os.environ.copy()
        
        # Force DISPLAY to :0 if we are running on Linux to ensure it targets the main screen
        # This is critical if the app is started via SSH or a system service
        if platform.system() == 'Linux':
            env['DISPLAY'] = ':0'
            
            # Try to locate .Xauthority to allow access to the display
            # This is often needed when running as root or a different user
            if 'XAUTHORITY' not in env:
                user_home = os.path.expanduser('~')
                possible_auths = [
                    os.path.join(user_home, '.Xauthority'),
                    '/home/pi/.Xauthority',  # Standard Pi user
                    '/home/dietpi/.Xauthority', # DietPi user
                ]
                for auth in possible_auths:
                    if os.path.exists(auth):
                        env['XAUTHORITY'] = auth
                        break

        try:
            # Open a log file for stderr to capture feh errors
            with open('feh_error.log', 'a') as log_file:
                log_file.write(f"\n--- Starting feh at {time.ctime()} ---\n")
                log_file.write(f"Command: {' '.join(cmd)}\n")
                log_file.write(f"Environment DISPLAY: {env.get('DISPLAY')}\n")
                log_file.write(f"Environment XAUTHORITY: {env.get('XAUTHORITY')}\n")
                
                self.process = subprocess.Popen(cmd, env=env, stderr=log_file, stdout=log_file)
                self.process.wait()
        except Exception as e:
            print(f"Error running feh: {e}")
            with open('feh_error.log', 'a') as log_file:
                log_file.write(f"Exception: {e}\n")
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

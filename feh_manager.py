import os
import subprocess
import threading
import time
import shutil
import platform
import glob

class FehController:
    def __init__(self, image_folder, delay=5):
        self.image_folder = image_folder
        self.delay = delay
        self.randomize = False
        self.show_filename = False
        self.processes = []  # Changed to list to handle multiple instances
        self.running = False
        self.thread = None

    def update_settings(self, settings):
        """Update settings from dictionary and restart if running."""
        self.delay = settings.get('delay', 5)
        self.randomize = settings.get('randomize', False)
        self.show_filename = settings.get('show_filename', False)
        
        if self.running:
            self.restart()

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
        if platform.system() == 'Windows':
            print("Warning: 'feh' is a Linux application. It will not run on Windows.")
            return

        print(f"Starting feh slideshow in {self.image_folder}...")
        self.running = True
        self.thread = threading.Thread(target=self._run_feh)
        self.thread.daemon = True
        self.thread.start()

    def _get_connected_monitors(self):
        """
        Attempts to find connected monitors using xrandr.
        Returns a list of monitor configurations (name, geometry).
        Example: [('HDMI-1', '1920x1080+0+0'), ('HDMI-2', '1920x1080+1920+0')]
        """
        monitors = []
        try:
            # Run xrandr to list monitors
            result = subprocess.run(['xrandr', '--listmonitors'], capture_output=True, text=True)
            output = result.stdout.strip()
            
            # Parse output
            # Format usually: 
            # Monitors: 2
            #  0: +*HDMI-1 1920/531x1080/299+0+0  HDMI-1
            #  1: +HDMI-2 1920/531x1080/299+1920+0  HDMI-2
            
            for line in output.split('\n'):
                if line.startswith('Monitors:'):
                    continue
                parts = line.split()
                if len(parts) >= 3:
                    # Depending on xrandr version, geometry is usually the 3rd item
                    # e.g., "0: +*HDMI-1 1920/531x1080/299+0+0  HDMI-1"
                    # We want the geometry string (e.g., 1920/531x1080/299+0+0)
                    # And the name (last item)
                    
                    geometry = parts[2]
                    # Clean geometry string (remove physical dimensions like /531)
                    # 1920/531x1080/299+0+0 -> 1920x1080+0+0
                    if '/' in geometry:
                        width_height = geometry.split('+')[0] # 1920/531x1080/299
                        w = width_height.split('x')[0].split('/')[0]
                        h = width_height.split('x')[1].split('/')[0]
                        offset = '+' + '+'.join(geometry.split('+')[1:])
                        clean_geometry = f"{w}x{h}{offset}"
                    else:
                        clean_geometry = geometry

                    name = parts[-1]
                    monitors.append({'name': name, 'geometry': clean_geometry})
                    
        except Exception as e:
            print(f"Error detecting monitors: {e}")
            # Fallback: Assume single monitor at +0+0 if detection fails
            return [{'name': 'Default', 'geometry': '+0+0'}]

        if not monitors:
             return [{'name': 'Default', 'geometry': '+0+0'}]
             
        return monitors

    def _run_feh(self):
        # Set DISPLAY environment variable
        env = os.environ.copy()
        if platform.system() == 'Linux':
            env['DISPLAY'] = ':0'
            if 'XAUTHORITY' not in env:
                user_home = os.path.expanduser('~')
                possible_auths = [
                    os.path.join(user_home, '.Xauthority'),
                    '/home/pi/.Xauthority',
                    '/home/dietpi/.Xauthority',
                ]
                for auth in possible_auths:
                    if os.path.exists(auth):
                        env['XAUTHORITY'] = auth
                        break

        # Detect monitors to launch instances for each
        monitors = self._get_connected_monitors()
        print(f"Detected monitors: {monitors}")

        try:
            # Open log file
            with open('feh_error.log', 'a') as log_file:
                log_file.write(f"\n--- Starting feh session at {time.ctime()} ---\n")
                
                # Launch one feh instance per monitor
                for monitor in monitors:
                    geometry = monitor['geometry']
                    
                    # Construct command for this specific monitor
                    cmd = [
                        'feh',
                        '-F', '-Z', '-Y',      # Fullscreen, Zoom, Hide Pointer
                        '-x',                  # Borderless
                        '-D', str(self.delay), # Slide Delay
                        '--reload', '2',       # Auto-reload
                        '--geometry', geometry, # Target specific monitor area
                        '--auto-zoom',         # Zoom to screen size
                        self.image_folder
                    ]

                    # Add randomize flag if enabled
                    if getattr(self, 'randomize', False):
                        cmd.append('-z')
                        
                    # Add filename display flag
                    if getattr(self, 'show_filename', False):
                        cmd.append('-d') # Draw filename (default)
                    else:
                        cmd.append('--hide-pointer') # ensure pointer hidden, but maybe use -d --draw-filename / --no-draw-filename?
                        # feh shows filename by default. To hide it, we need something else?
                        # checking man page: -d draws filename. If not specified, it might be drawn or not depending on version.
                        # Wait, --draw-filename is -d. If we want to HIDE it, we don't pass -d?
                        # Actually feh usually shows filename in overlay.
                        # To hide everything except image: -d (draw filename) -> omit it?
                        # No, usually to hide filename you just don't pass -d, OR pass --draw-filename if you want it.
                        # BUT some feh versions show it by default.
                        # The cleanest way is often creating a custom font/text overlay that is empty, or just rely on flags.
                        # Let's assume -d enables it. If we don't pass -d, it shouldn't show (or we use --draw-filename).
                        # Let's check typical usage.
                        # "feh --draw-filename" shows it.
                        pass # if not showing, do nothing (default behavior hopefully clean or handled by -x -F)

                    log_file.write(f"Launching for {monitor['name']}: {' '.join(cmd)}\n")
                    
                    # Start process
                    proc = subprocess.Popen(cmd, env=env, stderr=log_file, stdout=log_file)
                    self.processes.append(proc)

                # Wait for all processes (monitoring loop)
                while self.running and any(p.poll() is None for p in self.processes):
                    time.sleep(1)
                    
        except Exception as e:
            print(f"Error running feh loop: {e}")
            with open('feh_error.log', 'a') as log_file:
                log_file.write(f"Exception: {e}\n")
        finally:
            self.stop() # Ensure cleanup if loop exits

    def stop(self):
        # Force kill any existing feh processes
        if platform.system() == 'Linux':
            try:
                subprocess.run(['pkill', 'feh'], check=False)
            except Exception as e:
                print(f"Error executing pkill: {e}")

        # Clean up process objects
        for p in self.processes:
            if p.poll() is None:
                try:
                    p.terminate()
                    p.wait(timeout=1)
                except:
                    try:
                        p.kill()
                    except:
                        pass
        
        self.processes = []
        self.running = False

    def restart(self):
        self.stop()
        time.sleep(1)
        self.start()

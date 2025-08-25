"""
Service manager for running the Local AI Productivity Assistant as a background service
Supports Windows and Linux platforms
"""

import os
import sys
import platform
import subprocess
import logging
import signal
import time
import psutil
from pathlib import Path
from constants import ServiceStatus, SERVICE_NAME, SERVICE_DISPLAY_NAME, SERVICE_DESCRIPTION

logger = logging.getLogger(__name__)

class ServiceManager:
    """Manages the assistant as a background service"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.service_name = SERVICE_NAME
        self.project_root = Path(__file__).parent.parent.absolute()
        self.main_script = self.project_root / "src" / "main.py"
        self.python_exe = sys.executable
        self.pidfile = self.project_root / f"{self.service_name}.pid"
        
        # Determine service approach based on platform
        if self.platform == "windows":
            self.use_nssm = True
        elif self.platform == "linux":
            self.use_systemd = True
        else:
            logger.warning(f"Unsupported platform: {self.platform}")
    
    def install_service(self) -> bool:
        """Install the service based on the platform"""
        try:
            if self.platform == "windows":
                return self._install_windows_service()
            elif self.platform == "linux":
                return self._install_linux_service()
            else:
                logger.error(f"Service installation not supported on {self.platform}")
                return False
        except Exception as e:
            logger.error(f"Failed to install service: {e}")
            return False
    
    def uninstall_service(self) -> bool:
        """Uninstall the service"""
        try:
            if self.platform == "windows":
                return self._uninstall_windows_service()
            elif self.platform == "linux":
                return self._uninstall_linux_service()
            else:
                logger.error(f"Service uninstall not supported on {self.platform}")
                return False
        except Exception as e:
            logger.error(f"Failed to uninstall service: {e}")
            return False
    
    def start_service(self) -> bool:
        """Start the service"""
        try:
            if self.is_running():
                logger.info("Service is already running")
                return True
                
            if self.platform == "windows":
                return self._start_windows_service()
            elif self.platform == "linux":
                return self._start_linux_service()
            else:
                # Fallback: start as background process
                return self._start_background_process()
        except Exception as e:
            logger.error(f"Failed to start service: {e}")
            return False
    
    def stop_service(self) -> bool:
        """Stop the service"""
        try:
            if self.platform == "windows":
                return self._stop_windows_service()
            elif self.platform == "linux":
                return self._stop_linux_service()
            else:
                return self._stop_background_process()
        except Exception as e:
            logger.error(f"Failed to stop service: {e}")
            return False
    
    def restart_service(self) -> bool:
        """Restart the service"""
        logger.info("Restarting service...")
        if self.stop_service():
            time.sleep(2)  # Wait for clean shutdown
            return self.start_service()
        return False
    
    def get_status(self) -> ServiceStatus:
        """Get the current service status"""
        try:
            if self.is_running():
                return ServiceStatus.RUNNING
            else:
                return ServiceStatus.STOPPED
        except Exception as e:
            logger.error(f"Failed to get service status: {e}")
            return ServiceStatus.ERROR
    
    def is_running(self) -> bool:
        """Check if the service is currently running"""
        try:
            # Check if PID file exists and process is running
            if self.pidfile.exists():
                pid = int(self.pidfile.read_text().strip())
                return psutil.pid_exists(pid)
            return False
        except (FileNotFoundError, ValueError, OSError):
            return False
    
    def get_process_info(self) -> dict:
        """Get information about the running process"""
        try:
            if self.pidfile.exists():
                pid = int(self.pidfile.read_text().strip())
                if psutil.pid_exists(pid):
                    process = psutil.Process(pid)
                    return {
                        'pid': pid,
                        'status': process.status(),
                        'memory_info': process.memory_info(),
                        'cpu_percent': process.cpu_percent(),
                        'create_time': process.create_time()
                    }
        except Exception as e:
            logger.error(f"Failed to get process info: {e}")
        return {}
    
    # Windows-specific methods
    def _install_windows_service(self) -> bool:
        """Install Windows service using NSSM"""
        try:
            # Check if NSSM is available
            result = subprocess.run(['nssm', 'version'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("NSSM not found. Please install NSSM first.")
                return False
            
            # Install service
            cmd = [
                'nssm', 'install', self.service_name,
                self.python_exe, str(self.main_script)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Configure service
                subprocess.run(['nssm', 'set', self.service_name, 'DisplayName', SERVICE_DISPLAY_NAME])
                subprocess.run(['nssm', 'set', self.service_name, 'Description', SERVICE_DESCRIPTION])
                subprocess.run(['nssm', 'set', self.service_name, 'AppDirectory', str(self.project_root)])
                logger.info(f"Windows service '{self.service_name}' installed successfully")
                return True
            else:
                logger.error(f"Failed to install Windows service: {result.stderr}")
                return False
                
        except FileNotFoundError:
            logger.error("NSSM not found. Please install NSSM to use Windows service functionality.")
            return False
    
    def _uninstall_windows_service(self) -> bool:
        """Uninstall Windows service"""
        try:
            # Stop service first
            subprocess.run(['nssm', 'stop', self.service_name], capture_output=True)
            
            # Remove service
            result = subprocess.run(['nssm', 'remove', self.service_name, 'confirm'], 
                                 capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Windows service '{self.service_name}' uninstalled successfully")
                return True
            else:
                logger.error(f"Failed to uninstall Windows service: {result.stderr}")
                return False
                
        except FileNotFoundError:
            logger.error("NSSM not found")
            return False
    
    def _start_windows_service(self) -> bool:
        """Start Windows service"""
        try:
            result = subprocess.run(['nssm', 'start', self.service_name], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Windows service '{self.service_name}' started")
                return True
            else:
                logger.error(f"Failed to start Windows service: {result.stderr}")
                return False
        except FileNotFoundError:
            logger.error("NSSM not found")
            return False
    
    def _stop_windows_service(self) -> bool:
        """Stop Windows service"""
        try:
            result = subprocess.run(['nssm', 'stop', self.service_name], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Windows service '{self.service_name}' stopped")
                return True
            else:
                logger.error(f"Failed to stop Windows service: {result.stderr}")
                return False
        except FileNotFoundError:
            logger.error("NSSM not found")
            return False
    
    # Linux-specific methods
    def _install_linux_service(self) -> bool:
        """Install Linux systemd service"""
        try:
            service_content = f"""[Unit]
Description={SERVICE_DESCRIPTION}
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'root')}
WorkingDirectory={self.project_root}
ExecStart={self.python_exe} {self.main_script}
Restart=always
RestartSec=10
Environment=PATH={os.getenv('PATH')}
Environment=PYTHONPATH={self.project_root}

[Install]
WantedBy=multi-user.target
"""
            
            service_file = f"/etc/systemd/system/{self.service_name.lower()}.service"
            
            # Write service file (requires sudo)
            with open(service_file, 'w') as f:
                f.write(service_content)
            
            # Reload systemd and enable service
            subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
            subprocess.run(['sudo', 'systemctl', 'enable', f"{self.service_name.lower()}.service"], check=True)
            
            logger.info(f"Linux service '{self.service_name}' installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install Linux service: {e}")
            return False
        except PermissionError:
            logger.error("Permission denied. Try running with sudo.")
            return False
    
    def _uninstall_linux_service(self) -> bool:
        """Uninstall Linux systemd service"""
        try:
            service_name = f"{self.service_name.lower()}.service"
            
            # Stop and disable service
            subprocess.run(['sudo', 'systemctl', 'stop', service_name], capture_output=True)
            subprocess.run(['sudo', 'systemctl', 'disable', service_name], capture_output=True)
            
            # Remove service file
            service_file = f"/etc/systemd/system/{service_name}"
            if os.path.exists(service_file):
                os.remove(service_file)
            
            # Reload systemd
            subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
            
            logger.info(f"Linux service '{self.service_name}' uninstalled successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to uninstall Linux service: {e}")
            return False
        except PermissionError:
            logger.error("Permission denied. Try running with sudo.")
            return False
    
    def _start_linux_service(self) -> bool:
        """Start Linux systemd service"""
        try:
            result = subprocess.run(['sudo', 'systemctl', 'start', f"{self.service_name.lower()}.service"],
                                 capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Linux service '{self.service_name}' started")
                return True
            else:
                logger.error(f"Failed to start Linux service: {result.stderr}")
                return False
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start Linux service: {e}")
            return False
    
    def _stop_linux_service(self) -> bool:
        """Stop Linux systemd service"""
        try:
            result = subprocess.run(['sudo', 'systemctl', 'stop', f"{self.service_name.lower()}.service"],
                                 capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Linux service '{self.service_name}' stopped")
                return True
            else:
                logger.error(f"Failed to stop Linux service: {result.stderr}")
                return False
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to stop Linux service: {e}")
            return False
    
    # Fallback methods for unsupported platforms
    def _start_background_process(self) -> bool:
        """Start as background process (fallback)"""
        try:
            # Start the main script in background
            process = subprocess.Popen(
                [self.python_exe, str(self.main_script)],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            # Write PID to file
            self.pidfile.write_text(str(process.pid))
            logger.info(f"Background process started with PID: {process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start background process: {e}")
            return False
    
    def _stop_background_process(self) -> bool:
        """Stop background process"""
        try:
            if self.pidfile.exists():
                pid = int(self.pidfile.read_text().strip())
                if psutil.pid_exists(pid):
                    process = psutil.Process(pid)
                    process.terminate()
                    
                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=10)
                    except psutil.TimeoutExpired:
                        # Force kill if not terminated
                        process.kill()
                    
                    logger.info(f"Background process (PID: {pid}) stopped")
                
                self.pidfile.unlink()
                return True
            else:
                logger.info("No background process found")
                return True
                
        except Exception as e:
            logger.error(f"Failed to stop background process: {e}")
            return False
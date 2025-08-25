#!/usr/bin/env python3
"""
Service control script for the Local AI Productivity Assistant
Provides command-line interface to manage the service
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from service_manager import ServiceManager
from constants import ServiceStatus

def setup_logging():
    """Setup logging for the service control script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def print_status(manager: ServiceManager):
    """Print detailed service status"""
    status = manager.get_status()
    print(f"\n🔍 Service Status: {status.value.upper()}")
    
    if status == ServiceStatus.RUNNING:
        process_info = manager.get_process_info()
        if process_info:
            print(f"   PID: {process_info.get('pid', 'N/A')}")
            print(f"   Memory: {process_info.get('memory_info', {}).get('rss', 0) / 1024 / 1024:.1f} MB")
            print(f"   CPU: {process_info.get('cpu_percent', 0):.1f}%")
    
    print(f"   Platform: {manager.platform}")
    print(f"   Python: {manager.python_exe}")
    print(f"   Script: {manager.main_script}")
    print()

def main():
    parser = argparse.ArgumentParser(
        description="Control the Local AI Productivity Assistant service"
    )
    parser.add_argument(
        'action',
        choices=['install', 'uninstall', 'start', 'stop', 'restart', 'status'],
        help='Action to perform'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    setup_logging()
    
    # Create service manager
    manager = ServiceManager()
    
    print("🤖 Local AI Productivity Assistant - Service Control")
    print("=" * 50)
    
    try:
        if args.action == 'install':
            print("📦 Installing service...")
            if manager.install_service():
                print("✅ Service installed successfully!")
                print("\n💡 Next steps:")
                print("   1. Run 'python service_control.py start' to start the service")
                print("   2. Configure your .env file with Discord token")
            else:
                print("❌ Failed to install service")
                if manager.platform == "windows":
                    print("\n💡 For Windows, you need NSSM:")
                    print("   Download from: https://nssm.cc/download")
                    print("   Add nssm.exe to your PATH")
                elif manager.platform == "linux":
                    print("\n💡 For Linux, you may need sudo privileges")
                sys.exit(1)
        
        elif args.action == 'uninstall':
            print("🗑️ Uninstalling service...")
            if manager.uninstall_service():
                print("✅ Service uninstalled successfully!")
            else:
                print("❌ Failed to uninstall service")
                sys.exit(1)
        
        elif args.action == 'start':
            print("🚀 Starting service...")
            if manager.start_service():
                print("✅ Service started successfully!")
                print_status(manager)
            else:
                print("❌ Failed to start service")
                print("\n💡 Make sure:")
                print("   - Your .env file is configured")
                print("   - Discord token is valid")
                print("   - LM Studio is running (if using)")
                sys.exit(1)
        
        elif args.action == 'stop':
            print("🛑 Stopping service...")
            if manager.stop_service():
                print("✅ Service stopped successfully!")
            else:
                print("❌ Failed to stop service")
                sys.exit(1)
        
        elif args.action == 'restart':
            print("🔄 Restarting service...")
            if manager.restart_service():
                print("✅ Service restarted successfully!")
                print_status(manager)
            else:
                print("❌ Failed to restart service")
                sys.exit(1)
        
        elif args.action == 'status':
            print_status(manager)
    
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
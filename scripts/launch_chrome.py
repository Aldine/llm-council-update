#!/usr/bin/env python3
"""
Secure Chrome launcher for Confucius Agent UI Integrity
Launches Chrome with remote debugging enabled, bound to localhost only.
"""

import platform
import subprocess
import time
import sys
import requests
from pathlib import Path


class SecureChromeManager:
    """Manage Chrome with secure remote debugging configuration"""
    
    def __init__(self, port: int = 9222, user_data_dir: str = None):
        self.port = port
        self.host = "127.0.0.1"  # Security: localhost only
        self.user_data_dir = user_data_dir or self._get_default_data_dir()
        self.process = None
    
    def _get_default_data_dir(self) -> str:
        """Get OS-specific default user data directory"""
        system = platform.system()
        
        if system == "Windows":
            return r"C:\temp\chrome-debug"
        elif system == "Darwin":  # macOS
            return "/tmp/chrome-debug"
        else:  # Linux
            return "/tmp/chrome-debug"
    
    def _get_chrome_path(self) -> str:
        """Get OS-specific Chrome executable path"""
        system = platform.system()
        
        if system == "Windows":
            return r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        elif system == "Darwin":  # macOS
            return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        else:  # Linux
            return "google-chrome"
    
    def build_command(self) -> list:
        """Build secure Chrome launch command"""
        chrome_path = self._get_chrome_path()
        
        cmd = [
            chrome_path,
            f"--remote-debugging-port={self.port}",
            f"--remote-debugging-address={self.host}",  # SECURITY: localhost only
            f"--user-data-dir={self.user_data_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-background-networking",  # Privacy
            "--disable-sync",  # Privacy
            "--disable-extensions",  # Reduce attack surface
            "--disable-default-apps"
        ]
        
        return cmd
    
    def is_alive(self) -> bool:
        """Check if Chrome DevTools is responsive"""
        try:
            url = f"http://{self.host}:{self.port}/json/version"
            response = requests.get(url, timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def start(self, timeout: int = 10) -> bool:
        """Start Chrome with secure debugging enabled"""
        if self.is_alive():
            print(f"✓ Chrome already running on port {self.port}")
            return True
        
        cmd = self.build_command()
        
        try:
            print(f"Starting Chrome with remote debugging on {self.host}:{self.port}...")
            print(f"User data dir: {self.user_data_dir}")
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Wait for Chrome to be ready
            for i in range(timeout * 2):
                if self.is_alive():
                    print(f"✓ Chrome ready after {i * 0.5:.1f}s")
                    return True
                time.sleep(0.5)
            
            print(f"✗ Chrome failed to start within {timeout}s")
            return False
            
        except FileNotFoundError:
            print(f"✗ Chrome not found at: {cmd[0]}")
            print("Install Chrome or update the path in _get_chrome_path()")
            return False
        except Exception as e:
            print(f"✗ Failed to start Chrome: {e}")
            return False
    
    def stop(self):
        """Stop Chrome process"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                print("✓ Chrome stopped")
            except:
                self.process.kill()
                print("✓ Chrome force-killed")
    
    def get_version_info(self) -> dict:
        """Get Chrome version information"""
        if not self.is_alive():
            return {}
        
        try:
            url = f"http://{self.host}:{self.port}/json/version"
            response = requests.get(url, timeout=2)
            return response.json()
        except:
            return {}
    
    def get_tabs(self) -> list:
        """Get list of open tabs"""
        if not self.is_alive():
            return []
        
        try:
            url = f"http://{self.host}:{self.port}/json"
            response = requests.get(url, timeout=2)
            return response.json()
        except:
            return []


def print_launch_commands():
    """Print platform-specific launch commands"""
    print("\n" + "="*70)
    print("Manual Chrome Launch Commands (Secure Configuration)")
    print("="*70)
    
    print("\n📦 macOS:")
    print("""
/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome \\
  --remote-debugging-port=9222 \\
  --remote-debugging-address=127.0.0.1 \\
  --user-data-dir=/tmp/chrome-debug \\
  --no-first-run --no-default-browser-check
""")
    
    print("\n📦 Windows PowerShell:")
    print("""
& 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe' `
  --remote-debugging-port=9222 `
  --remote-debugging-address=127.0.0.1 `
  --user-data-dir='C:\\temp\\chrome-debug' `
  --no-first-run --no-default-browser-check
""")
    
    print("\n📦 Linux:")
    print("""
google-chrome \\
  --remote-debugging-port=9222 \\
  --remote-debugging-address=127.0.0.1 \\
  --user-data-dir=/tmp/chrome-debug \\
  --no-first-run --no-default-browser-check
""")
    
    print("\n" + "="*70)
    print("Security Notes:")
    print("  • --remote-debugging-address=127.0.0.1 prevents external access")
    print("  • Firewall should block port 9222 on non-local interfaces")
    print("  • Use unique user-data-dir per project to avoid contamination")
    print("="*70 + "\n")


def quick_health_check(port: int = 9222):
    """Fast health check for Chrome DevTools"""
    print(f"\n🔍 Chrome DevTools Health Check (port {port})...")
    
    try:
        url = f"http://127.0.0.1:{port}/json/version"
        response = requests.get(url, timeout=2)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Chrome DevTools is alive")
            print(f"  Browser: {data.get('Browser', 'Unknown')}")
            print(f"  Protocol: {data.get('Protocol-Version', 'Unknown')}")
            print(f"  WebSocket: {data.get('webSocketDebuggerUrl', 'N/A')}")
            return True
        else:
            print(f"✗ Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to port {port}")
        print(f"  Chrome may not be running with remote debugging enabled")
        return False
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False


def main():
    """CLI for secure Chrome management"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Secure Chrome launcher for Confucius Agent UI Integrity"
    )
    parser.add_argument(
        "command",
        choices=["start", "stop", "check", "info", "tabs", "help"],
        help="Command to execute"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9222,
        help="Remote debugging port (default: 9222)"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        help="Chrome user data directory"
    )
    
    args = parser.parse_args()
    
    if args.command == "help":
        print_launch_commands()
        return
    
    manager = SecureChromeManager(port=args.port, user_data_dir=args.data_dir)
    
    if args.command == "start":
        success = manager.start()
        sys.exit(0 if success else 1)
    
    elif args.command == "stop":
        manager.stop()
    
    elif args.command == "check":
        success = quick_health_check(args.port)
        sys.exit(0 if success else 1)
    
    elif args.command == "info":
        info = manager.get_version_info()
        if info:
            print(json.dumps(info, indent=2))
        else:
            print("Chrome not running or not accessible")
            sys.exit(1)
    
    elif args.command == "tabs":
        tabs = manager.get_tabs()
        if tabs:
            print(f"Found {len(tabs)} tab(s):")
            for i, tab in enumerate(tabs, 1):
                print(f"\n{i}. {tab.get('title', 'Untitled')}")
                print(f"   URL: {tab.get('url', 'N/A')}")
                print(f"   Type: {tab.get('type', 'N/A')}")
        else:
            print("No tabs found or Chrome not running")
            sys.exit(1)


if __name__ == "__main__":
    # If run without arguments, do a quick check
    if len(sys.argv) == 1:
        quick_health_check()
    else:
        main()

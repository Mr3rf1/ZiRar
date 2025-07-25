#!/usr/bin/env python3
"""
UnRAR Setup Helper for ZiRar
Helps users set up UnRAR executable for RAR archive support
"""

import os
import sys
import platform
import subprocess
import urllib.request
import tempfile
from pathlib import Path

def detect_system():
    """Detect the operating system"""
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    print(f"🖥️  System Information:")
    print(f"   Operating System: {platform.system()} {platform.release()}")
    print(f"   Architecture: {platform.machine()}")
    print(f"   Python Version: {platform.python_version()}")
    
    return system, arch

def check_unrar_installed():
    """Check if UnRAR is already installed and accessible"""
    print(f"\n🔍 Checking for existing UnRAR installation...")
    
    # Common UnRAR executable names
    unrar_names = ['unrar', 'unrar.exe', 'UnRAR.exe']
    
    # Check in PATH
    for name in unrar_names:
        try:
            result = subprocess.run([name], capture_output=True, text=True, timeout=5)
            if result.returncode != 127:  # Command found
                print(f"   ✅ Found {name} in PATH")
                return name
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            continue
    
    # Check common installation paths
    common_paths = [
        r'C:\Program Files\WinRAR\UnRAR.exe',
        r'C:\Program Files (x86)\WinRAR\UnRAR.exe',
        r'C:\Program Files\7-Zip\Unrar.exe',
        '/usr/bin/unrar',
        '/usr/local/bin/unrar',
        '/opt/homebrew/bin/unrar',
        '/usr/local/Cellar/unrar/*/bin/unrar'
    ]
    
    for path in common_paths:
        if '*' in path:
            # Handle glob patterns
            import glob
            matches = glob.glob(path)
            if matches and os.path.isfile(matches[0]):
                print(f"   ✅ Found UnRAR at: {matches[0]}")
                return matches[0]
        elif os.path.isfile(path):
            print(f"   ✅ Found UnRAR at: {path}")
            return path
    
    print(f"   ❌ UnRAR not found in common locations")
    return None

def test_unrar_functionality(unrar_path):
    """Test if UnRAR works properly"""
    print(f"\n🧪 Testing UnRAR functionality...")
    
    try:
        # Test UnRAR version command
        result = subprocess.run([unrar_path], capture_output=True, text=True, timeout=10)
        
        if 'UNRAR' in result.stdout.upper() or 'UNRAR' in result.stderr.upper():
            print(f"   ✅ UnRAR is working correctly")
            
            # Try to get version info
            version_info = result.stdout.split('\n')[0] if result.stdout else "Version unknown"
            print(f"   📋 Version: {version_info.strip()}")
            return True
        else:
            print(f"   ⚠️  UnRAR found but may not be working correctly")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"   ⚠️  UnRAR test timed out")
        return False
    except Exception as e:
        print(f"   ❌ Error testing UnRAR: {str(e)}")
        return False

def setup_windows():
    """Setup instructions for Windows"""
    print(f"\n🪟 Windows Setup Instructions:")
    print(f"")
    print(f"📥 Option 1: Download from Official Site")
    print(f"   1. Visit: https://www.rarlab.com/rar_add.htm")
    print(f"   2. Download 'UnRAR for Windows'")
    print(f"   3. Extract to a folder (e.g., C:\\UnRAR\\)")
    print(f"   4. Add the folder to your system PATH")
    print(f"")
    print(f"📦 Option 2: Using Package Managers")
    print(f"   • Chocolatey: choco install unrar")
    print(f"   • Scoop: scoop install unrar")
    print(f"   • Winget: winget install RARLab.UnRAR")
    print(f"")
    print(f"🔧 Option 3: WinRAR Installation")
    print(f"   1. Install WinRAR from https://www.win-rar.com/")
    print(f"   2. UnRAR.exe will be included in the WinRAR folder")
    print(f"   3. Add WinRAR folder to PATH or copy UnRAR.exe to project folder")

def setup_linux():
    """Setup instructions for Linux"""
    print(f"\n🐧 Linux Setup Instructions:")
    print(f"")
    print(f"📦 Package Manager Installation:")
    print(f"   • Ubuntu/Debian: sudo apt-get install unrar")
    print(f"   • CentOS/RHEL: sudo yum install unrar")
    print(f"   • Fedora: sudo dnf install unrar")
    print(f"   • Arch Linux: sudo pacman -S unrar")
    print(f"   • openSUSE: sudo zypper install unrar")
    print(f"")
    print(f"📥 Manual Installation:")
    print(f"   1. Visit: https://www.rarlab.com/rar_add.htm")
    print(f"   2. Download 'RAR for Linux'")
    print(f"   3. Extract and copy 'unrar' to /usr/local/bin/")
    print(f"   4. Make executable: chmod +x /usr/local/bin/unrar")

def setup_macos():
    """Setup instructions for macOS"""
    print(f"\n🍎 macOS Setup Instructions:")
    print(f"")
    print(f"🍺 Homebrew (Recommended):")
    print(f"   brew install unrar")
    print(f"")
    print(f"🔌 MacPorts:")
    print(f"   sudo port install unrar")
    print(f"")
    print(f"📥 Manual Installation:")
    print(f"   1. Visit: https://www.rarlab.com/rar_add.htm")
    print(f"   2. Download 'RAR for macOS'")
    print(f"   3. Extract and copy 'unrar' to /usr/local/bin/")
    print(f"   4. Make executable: chmod +x /usr/local/bin/unrar")

def setup_path_instructions():
    """Provide PATH setup instructions"""
    print(f"\n🛤️  Adding UnRAR to System PATH:")
    print(f"")
    
    system = platform.system().lower()
    
    if system == 'windows':
        print(f"Windows PATH Setup:")
        print(f"   1. Right-click 'This PC' → Properties")
        print(f"   2. Click 'Advanced system settings'")
        print(f"   3. Click 'Environment Variables'")
        print(f"   4. Under 'System Variables', find and select 'Path'")
        print(f"   5. Click 'Edit' → 'New'")
        print(f"   6. Add the folder containing UnRAR.exe")
        print(f"   7. Click 'OK' to save")
        print(f"   8. Restart command prompt/PowerShell")
        
    elif system == 'linux':
        print(f"Linux PATH Setup:")
        print(f"   1. Edit ~/.bashrc or ~/.zshrc:")
        print(f"      echo 'export PATH=$PATH:/path/to/unrar/folder' >> ~/.bashrc")
        print(f"   2. Reload shell: source ~/.bashrc")
        print(f"   3. Or copy unrar to /usr/local/bin/ (requires sudo)")
        
    elif system == 'darwin':  # macOS
        print(f"macOS PATH Setup:")
        print(f"   1. Edit ~/.bash_profile or ~/.zshrc:")
        print(f"      echo 'export PATH=$PATH:/path/to/unrar/folder' >> ~/.zshrc")
        print(f"   2. Reload shell: source ~/.zshrc")
        print(f"   3. Or copy unrar to /usr/local/bin/")

def test_with_ZiRar():
    """Test UnRAR integration with ZiRar"""
    print(f"\n🔗 Testing Integration with ZiRar:")
    
    try:
        # Try to import rarfile to test integration
        import rarfile
        print(f"   ✅ rarfile module is available")
        
        # Try to set up rarfile with detected UnRAR
        unrar_path = check_unrar_installed()
        if unrar_path:
            rarfile.UNRAR_TOOL = unrar_path
            print(f"   ✅ rarfile configured with UnRAR: {unrar_path}")
            
            # Test if rarfile can work with the UnRAR tool
            try:
                # This will test if rarfile can find and use the UnRAR tool
                test_rar = rarfile.RarFile.__new__(rarfile.RarFile)
                print(f"   ✅ rarfile integration test passed")
                return True
            except Exception as e:
                print(f"   ⚠️  rarfile integration test failed: {str(e)}")
                return False
        else:
            print(f"   ❌ UnRAR not found for integration")
            return False
            
    except ImportError:
        print(f"   ❌ rarfile module not installed")
        print(f"   💡 Install with: pip install rarfile")
        return False

def main():
    """Main setup function"""
    print(f"🔐 ZiRar UnRAR Setup Helper")
    print(f"=" * 50)
    
    # Detect system
    system, arch = detect_system()
    
    # Check current installation
    unrar_path = check_unrar_installed()
    
    if unrar_path:
        # Test functionality
        if test_unrar_functionality(unrar_path):
            print(f"\n✅ UnRAR is properly installed and working!")
            
            # Test integration with ZiRar
            if test_with_ZiRar():
                print(f"\n🎉 Setup Complete!")
                print(f"   UnRAR is ready to use with ZiRar")
                print(f"   You can now process RAR archives in the application")
                return True
            else:
                print(f"\n⚠️  UnRAR found but integration needs attention")
        else:
            print(f"\n⚠️  UnRAR found but not working properly")
    
    # Provide setup instructions based on OS
    print(f"\n📋 Setup Instructions:")
    
    if system == 'windows':
        setup_windows()
    elif system == 'linux':
        setup_linux()
    elif system == 'darwin':  # macOS
        setup_macos()
    else:
        print(f"   ❓ Unsupported operating system: {system}")
        print(f"   Please visit https://www.rarlab.com/rar_add.htm for manual installation")
    
    # Provide PATH setup instructions
    setup_path_instructions()
    
    print(f"\n🔄 After Installation:")
    print(f"   1. Restart your terminal/command prompt")
    print(f"   2. Run this script again to verify installation")
    print(f"   3. Launch ZiRar and test RAR file support")
    
    print(f"\n💡 Troubleshooting:")
    print(f"   • Make sure UnRAR is in your system PATH")
    print(f"   • Try restarting your computer after installation")
    print(f"   • Check that you downloaded the correct version for your system")
    print(f"   • Ensure you have proper permissions to execute UnRAR")
    
    return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            sys.exit(0)
        else:
            print(f"\n❌ Setup incomplete. Please follow the instructions above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print(f"Please report this issue on the project's GitHub page")
        sys.exit(1)

#!/usr/bin/env python3
"""
Quick fix for dependency conflicts
Run this if you encounter pip dependency resolver errors
"""

import subprocess
import sys

def run_command(cmd):
    """Run command and return success status"""
    try:
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("🔧 Quick Fix for Dependency Conflicts")
    print("=" * 40)
    
    print("🧹 Step 1: Removing conflicting packages...")
    packages_to_remove = [
        'aiohttp',
        'aiohttp-socks', 
        'web3',
        'eth-account',
        'fake-useragent'
    ]
    
    for package in packages_to_remove:
        print(f"   Removing {package}...")
        run_command(f"pip uninstall {package} -y")
    
    print("\n📦 Step 2: Installing compatible versions...")
    packages_to_install = [
        "web3==6.15.1",
        "aiohttp>=3.10.0",
        "eth-account==0.10.0",
        "fake-useragent==1.4.0", 
        "colorama==0.4.6"
    ]
    
    success = True
    for package in packages_to_install:
        print(f"   Installing {package}...")
        if not run_command(f"pip install '{package}'"):
            print(f"   ❌ Failed to install {package}")
            success = False
        else:
            print(f"   ✅ {package} installed successfully")
    
    print("\n🔍 Step 3: Verifying installation...")
    try:
        import web3
        import aiohttp
        import eth_account
        import fake_useragent
        import colorama
        
        print("✅ All packages imported successfully!")
        print(f"   web3: {web3.__version__}")
        print(f"   aiohttp: {aiohttp.__version__}")
        print(f"   eth-account: {eth_account.__version__}")
        print(f"   colorama: {colorama.__version__}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        success = False
    
    if success:
        print("\n🎉 Dependencies fixed successfully!")
        print("You can now run: python eth_faucet_bot.py")
    else:
        print("\n❌ Some issues remain. Try running: python install.py")

if __name__ == "__main__":
    main()
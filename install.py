#!/usr/bin/env python3
"""
Installation script for ETH Faucet Bot
Handles dependency conflicts and ensures clean installation
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def uninstall_conflicting_packages():
    """Uninstall packages that might cause conflicts"""
    conflicting_packages = [
        'aiohttp',
        'aiohttp-socks', 
        'web3',
        'eth-account',
        'fake-useragent'
    ]
    
    print("🧹 Cleaning up potentially conflicting packages...")
    
    for package in conflicting_packages:
        print(f"   Removing {package}...")
        subprocess.run(f"pip uninstall {package} -y", shell=True, capture_output=True)
    
    print("✅ Cleanup completed")

def install_requirements():
    """Install requirements with specific versions"""
    requirements = [
        "web3==6.15.1",
        "aiohttp>=3.10.0",
        "eth-account==0.10.0", 
        "fake-useragent==1.4.0",
        "colorama==0.4.6"
    ]
    
    print("📦 Installing requirements...")
    
    for requirement in requirements:
        if not run_command(f"pip install '{requirement}'", f"Installing {requirement}"):
            return False
    
    return True

def verify_installation():
    """Verify that all packages are installed correctly"""
    print("🔍 Verifying installation...")
    
    try:
        import web3
        import aiohttp
        import eth_account
        import fake_useragent
        import colorama
        
        print("✅ All packages imported successfully")
        
        # Check versions
        print(f"   web3: {web3.__version__}")
        print(f"   aiohttp: {aiohttp.__version__}")
        print(f"   eth-account: {eth_account.__version__}")
        print(f"   colorama: {colorama.__version__}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def create_config_files():
    """Create configuration files if they don't exist"""
    print("📄 Checking configuration files...")
    
    files_to_create = {
        'accounts.txt': '''# Add your private keys here, one per line
# Example format:
# 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
# 0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890

your_private_key_1_here
your_private_key_2_here''',
        
        '2captcha_key.txt': '''# Add your 2captcha API key here
# Get your API key from: https://2captcha.com/enterpage
# Example: abc123def456ghi789jkl012mno345pqr678stu901vwx234yz

your_2captcha_api_key_here''',
        
        'config.json': '''{
    "claim_interval": 3600,
    "max_retries": 3,
    "timeout": 30,
    "selected_faucet": "sepolia",
    "delay_between_accounts": {
        "min": 10,
        "max": 30
    },
    "retry_delay": 60,
    "balance_check_delay": 30,
    "logging": {
        "enable_file_logging": false,
        "log_file": "bot.log"
    },
    "faucets": {
        "sepolia": {
            "daily_limit": 0.5,
            "cooldown": 86400
        },
        "goerli": {
            "daily_limit": 0.1,
            "cooldown": 86400
        }
    }
}'''
    }
    
    for filename, content in files_to_create.items():
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                f.write(content)
            print(f"✅ Created {filename}")
        else:
            print(f"⚠️  {filename} already exists, skipping...")

def main():
    """Main installation process"""
    print("🚀 ETH Faucet Bot Installation Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Ask user for installation method
    print("\nInstallation options:")
    print("1. Clean install (recommended) - Remove conflicting packages first")
    print("2. Force install - Try to install over existing packages")
    print("3. Update only - Update existing packages")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        print("\n🧹 Starting clean installation...")
        uninstall_conflicting_packages()
        
        if not install_requirements():
            print("❌ Installation failed")
            sys.exit(1)
            
    elif choice == "2":
        print("\n🔨 Starting force installation...")
        if not run_command("pip install -r requirements.txt --force-reinstall", "Force installing requirements"):
            print("❌ Installation failed")
            sys.exit(1)
            
    elif choice == "3":
        print("\n⬆️ Updating packages...")
        if not run_command("pip install -r requirements.txt --upgrade", "Updating requirements"):
            print("❌ Update failed")
            sys.exit(1)
    else:
        print("❌ Invalid choice")
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("❌ Installation verification failed")
        sys.exit(1)
    
    # Create config files
    create_config_files()
    
    print("\n" + "=" * 50)
    print("🎉 Installation completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit accounts.txt and add your private keys")
    print("2. Edit 2captcha_key.txt and add your 2captcha API key")
    print("3. Run the bot: python eth_faucet_bot.py")
    print("\n💡 Need help? Check README.md for detailed instructions")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
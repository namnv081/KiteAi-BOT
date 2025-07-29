#!/usr/bin/env python3
"""
Setup script for Real ETH Faucet Bot
Configures accounts and settings for claiming real testnet ETH
"""

import os
from colorama import *

init(autoreset=True)

def create_accounts_file():
    """Tạo file accounts.txt với hướng dẫn"""
    content = """# Add your real private keys here (one per line)
# ⚠️ IMPORTANT: These should be TESTNET wallets only!
# ⚠️ NEVER use mainnet private keys with real funds!
# 
# Example format:
# 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
# 0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890

# Uncomment and replace with your actual private keys:
# your_testnet_private_key_1_here
# your_testnet_private_key_2_here
"""
    
    if not os.path.exists('accounts.txt'):
        with open('accounts.txt', 'w') as f:
            f.write(content)
        print(f"{Fore.GREEN}✓ Created accounts.txt")
    else:
        print(f"{Fore.YELLOW}⚠ accounts.txt already exists")

def create_2captcha_file():
    """Tạo file 2captcha_key.txt"""
    content = """# Add your 2captcha API key here (optional)
# Get your API key from: https://2captcha.com/enterpage
# 
# Benefits of using 2captcha:
# - Automatic captcha solving
# - Higher success rate
# - No manual intervention needed
#
# Cost: ~$0.001-0.003 per captcha
# 
# If you don't have a key, the bot will still work but you may need to
# solve captchas manually in the browser window.

# Uncomment and replace with your actual API key:
# your_2captcha_api_key_here
"""
    
    if not os.path.exists('2captcha_key.txt'):
        with open('2captcha_key.txt', 'w') as f:
            f.write(content)
        print(f"{Fore.GREEN}✓ Created 2captcha_key.txt")
    else:
        print(f"{Fore.YELLOW}⚠ 2captcha_key.txt already exists")

def create_config_file():
    """Tạo file config.json"""
    import json
    
    config = {
        "headless": False,
        "claim_interval": 3600,
        "max_retries": 3,
        "timeout": 30,
        "delay_between_accounts": {
            "min": 30,
            "max": 60
        }
    }
    
    if not os.path.exists('config.json'):
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        print(f"{Fore.GREEN}✓ Created config.json")
    else:
        print(f"{Fore.YELLOW}⚠ config.json already exists")

def show_instructions():
    """Hiển thị hướng dẫn sử dụng"""
    print(f"\n{Fore.CYAN}📋 Next Steps:")
    print(f"{Fore.WHITE}1. Edit accounts.txt - Add your testnet private keys")
    print(f"{Fore.WHITE}2. Edit 2captcha_key.txt - Add your 2captcha API key (optional)")
    print(f"{Fore.WHITE}3. Install dependencies: pip install -r requirements.txt")
    print(f"{Fore.WHITE}4. Run the bot: python web_faucet_bot.py")
    
    print(f"\n{Fore.YELLOW}⚠️ Important Security Notes:")
    print(f"{Fore.RED}• Only use TESTNET wallets - never mainnet wallets with real funds!")
    print(f"{Fore.RED}• Keep your private keys secure and never share them")
    print(f"{Fore.RED}• This bot is for educational/testing purposes only")
    
    print(f"\n{Fore.CYAN}💡 Tips:")
    print(f"{Fore.WHITE}• Alchemy faucet is BEST (up to 1 ETH, no login required)")
    print(f"{Fore.WHITE}• QuickNode has shorter cooldown (12h vs 24h)")
    print(f"{Fore.WHITE}• Chainlink is reliable backup option")
    print(f"{Fore.WHITE}• Bot will auto-detect and solve captchas if 2captcha key provided")
    print(f"{Fore.WHITE}• Set headless: true in config.json to run without browser window")

def main():
    print(f"{Fore.GREEN + Style.BRIGHT}🚀 Real ETH Faucet Bot Setup")
    print("=" * 50)
    
    print(f"{Fore.CYAN}Creating configuration files...")
    
    create_accounts_file()
    create_2captcha_file() 
    create_config_file()
    
    print(f"\n{Fore.GREEN}✅ Setup completed!")
    
    show_instructions()

if __name__ == "__main__":
    main()
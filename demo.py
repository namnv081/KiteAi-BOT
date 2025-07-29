#!/usr/bin/env python3
"""
Demo Script for ETH Faucet Bot
Runs both the faucet simulator and bot for testing
"""

import asyncio
import subprocess
import sys
import os
import time
from colorama import *

init(autoreset=True)

class Demo:
    def __init__(self):
        self.simulator_process = None
        
    def check_requirements(self):
        """Kiểm tra requirements"""
        print(f"{Fore.CYAN}🔍 Checking requirements...")
        
        required_files = [
            'eth_faucet_bot.py',
            'faucet_simulator.py',
            'accounts.txt',
            '2captcha_key.txt'
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            print(f"{Fore.RED}✗ Missing files: {', '.join(missing_files)}")
            return False
        
        print(f"{Fore.GREEN}✓ All required files found")
        return True
    
    def setup_demo_accounts(self):
        """Tạo demo accounts nếu chưa có"""
        print(f"{Fore.CYAN}📝 Setting up demo accounts...")
        
        # Tạo demo private keys (fake keys for testing)
        demo_accounts = [
            "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        ]
        
        try:
            with open('accounts.txt', 'r') as f:
                content = f.read().strip()
                if 'your_private_key' in content:
                    # Replace demo content
                    with open('accounts.txt', 'w') as f:
                        f.write("# Demo accounts for testing\n")
                        for account in demo_accounts:
                            f.write(f"{account}\n")
                    print(f"{Fore.GREEN}✓ Demo accounts configured")
                else:
                    print(f"{Fore.GREEN}✓ Accounts already configured")
        except Exception as e:
            print(f"{Fore.RED}✗ Error setting up accounts: {e}")
            return False
        
        # Setup demo 2captcha key
        try:
            with open('2captcha_key.txt', 'r') as f:
                content = f.read().strip()
                if 'your_2captcha_api_key_here' in content:
                    with open('2captcha_key.txt', 'w') as f:
                        f.write("demo_key_for_testing_only")
                    print(f"{Fore.GREEN}✓ Demo 2captcha key configured")
                else:
                    print(f"{Fore.GREEN}✓ 2captcha key already configured")
        except Exception as e:
            print(f"{Fore.RED}✗ Error setting up 2captcha key: {e}")
            return False
        
        return True
    
    async def start_simulator(self):
        """Khởi động faucet simulator"""
        print(f"{Fore.CYAN}🚀 Starting faucet simulator...")
        
        try:
            self.simulator_process = subprocess.Popen([
                sys.executable, 'faucet_simulator.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Chờ simulator khởi động
            await asyncio.sleep(3)
            
            # Kiểm tra xem simulator có chạy không
            if self.simulator_process.poll() is None:
                print(f"{Fore.GREEN}✓ Faucet simulator started successfully")
                print(f"{Fore.CYAN}📍 Simulator running on: http://localhost:8080")
                return True
            else:
                stdout, stderr = self.simulator_process.communicate()
                print(f"{Fore.RED}✗ Simulator failed to start:")
                print(f"{Fore.RED}   {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}✗ Error starting simulator: {e}")
            return False
    
    async def test_simulator(self):
        """Test simulator connection"""
        print(f"{Fore.CYAN}🧪 Testing simulator connection...")
        
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:8080/api/status') as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"{Fore.GREEN}✓ Simulator is responding")
                        print(f"   Status: {data.get('status')}")
                        print(f"   Faucet: {data.get('faucet_name')}")
                        return True
                    else:
                        print(f"{Fore.RED}✗ Simulator returned status: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"{Fore.RED}✗ Error testing simulator: {e}")
            return False
    
    def start_bot(self):
        """Khởi động bot"""
        print(f"\n{Fore.CYAN}🤖 Starting ETH Faucet Bot...")
        print(f"{Fore.YELLOW}💡 Select option 1 (Simulator) when prompted")
        print(f"{Fore.YELLOW}💡 The bot will automatically use demo accounts and 2captcha key")
        print("-" * 60)
        
        try:
            subprocess.run([sys.executable, 'eth_faucet_bot.py'])
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Bot stopped by user")
        except Exception as e:
            print(f"\n{Fore.RED}Error running bot: {e}")
    
    def cleanup(self):
        """Dọn dẹp processes"""
        if self.simulator_process and self.simulator_process.poll() is None:
            print(f"{Fore.CYAN}🧹 Stopping faucet simulator...")
            self.simulator_process.terminate()
            self.simulator_process.wait()
            print(f"{Fore.GREEN}✓ Simulator stopped")
    
    async def run_demo(self):
        """Chạy demo hoàn chỉnh"""
        try:
            print(f"{Fore.GREEN + Style.BRIGHT}🎬 ETH Faucet Bot Demo")
            print("=" * 50)
            
            # Kiểm tra requirements
            if not self.check_requirements():
                return False
            
            # Setup demo accounts
            if not self.setup_demo_accounts():
                return False
            
            # Khởi động simulator
            if not await self.start_simulator():
                return False
            
            # Test simulator
            if not await self.test_simulator():
                return False
            
            print(f"\n{Fore.GREEN}🎉 Demo setup completed successfully!")
            print(f"{Fore.CYAN}📋 What's running:")
            print(f"   • Faucet Simulator: http://localhost:8080")
            print(f"   • Demo accounts: 2 test accounts configured")
            print(f"   • Demo 2captcha: Mock key configured")
            
            input(f"\n{Fore.YELLOW}Press Enter to start the bot...")
            
            # Khởi động bot
            self.start_bot()
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Demo interrupted by user")
        except Exception as e:
            print(f"\n{Fore.RED}Demo error: {e}")
        finally:
            self.cleanup()

def main():
    """Main function"""
    demo = Demo()
    
    print(f"{Fore.CYAN}Welcome to ETH Faucet Bot Demo!")
    print(f"{Fore.WHITE}This demo will:")
    print(f"  1. Set up a local faucet simulator")
    print(f"  2. Configure demo accounts and keys")
    print(f"  3. Run the bot against the simulator")
    print(f"\n{Fore.YELLOW}⚠️  This is for testing only - no real ETH will be claimed!")
    
    choice = input(f"\n{Fore.CYAN}Start demo? (y/N): ").strip().lower()
    
    if choice == 'y':
        try:
            asyncio.run(demo.run_demo())
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}👋 Demo cancelled")
    else:
        print(f"{Fore.YELLOW}Demo cancelled")

if __name__ == "__main__":
    main()
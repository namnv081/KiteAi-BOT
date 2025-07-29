#!/usr/bin/env python3
"""
Test script for 2captcha integration
Use this to debug captcha solving issues
"""

import asyncio
import aiohttp
from colorama import *

init(autoreset=True)

class CaptchaTest:
    def __init__(self):
        self.CAPTCHA_API_URL = "http://2captcha.com"
        self.captcha_key = None

    def load_2captcha_key(self):
        """Load 2captcha API key từ file"""
        try:
            with open('2captcha_key.txt', 'r') as file:
                key = file.read().strip()
                if key and key != "your_2captcha_api_key_here":
                    self.captcha_key = key
                    print(f"{Fore.GREEN}✓ 2Captcha API key loaded: {key[:10]}...{key[-4:]}")
                    return True
                else:
                    print(f"{Fore.RED}✗ Please add your 2captcha API key to 2captcha_key.txt")
                    return False
        except FileNotFoundError:
            print(f"{Fore.RED}✗ 2captcha_key.txt file not found")
            return False

    async def test_api_connection(self):
        """Test basic API connection"""
        print(f"\n{Fore.CYAN}🔗 Testing API connection...")
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(f"{self.CAPTCHA_API_URL}/res.php?key={self.captcha_key}&action=getbalance") as response:
                    if response.status == 200:
                        result = await response.text()
                        print(f"{Fore.GREEN}✓ API connection successful")
                        print(f"   Response: {result}")
                        return True
                    else:
                        print(f"{Fore.RED}✗ HTTP Error: {response.status}")
                        return False
        except Exception as e:
            print(f"{Fore.RED}✗ Connection failed: {str(e)}")
            return False

    async def check_balance(self):
        """Kiểm tra balance 2captcha"""
        print(f"\n{Fore.CYAN}💰 Checking 2captcha balance...")
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(f"{self.CAPTCHA_API_URL}/res.php?key={self.captcha_key}&action=getbalance") as response:
                    balance_text = await response.text()
                    
                if balance_text.startswith('ERROR'):
                    print(f"{Fore.RED}✗ Balance check failed: {balance_text}")
                    
                    # Giải thích các lỗi thường gặp
                    if balance_text == "ERROR_WRONG_USER_KEY":
                        print(f"{Fore.YELLOW}💡 Tip: Your API key is invalid. Check 2captcha_key.txt")
                    elif balance_text == "ERROR_KEY_DOES_NOT_EXIST":
                        print(f"{Fore.YELLOW}💡 Tip: API key doesn't exist. Get it from https://2captcha.com/enterpage")
                    
                    return None
                else:
                    balance = float(balance_text)
                    print(f"{Fore.GREEN}✓ Current balance: ${balance:.4f}")
                    
                    if balance < 0.001:
                        print(f"{Fore.YELLOW}⚠ Low balance! Add funds at https://2captcha.com/pay")
                    elif balance < 0.01:
                        print(f"{Fore.YELLOW}⚠ Balance is getting low")
                    else:
                        print(f"{Fore.GREEN}✓ Balance looks good!")
                    
                    return balance
                    
        except Exception as e:
            print(f"{Fore.RED}✗ Error checking balance: {str(e)}")
            return None

    async def test_captcha_submit(self):
        """Test submitting a test captcha"""
        print(f"\n{Fore.CYAN}🧩 Testing captcha submission...")
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                # Test với site key của Google (test site key)
                submit_data = {
                    'key': self.captcha_key,
                    'method': 'userrecaptcha',
                    'googlekey': '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI',  # Test site key
                    'pageurl': 'https://google.com',
                    'json': 1
                }
                
                async with session.post(f"{self.CAPTCHA_API_URL}/in.php", data=submit_data) as response:
                    result = await response.json()
                    
                if result.get('status') == 1:
                    captcha_id = result['request']
                    print(f"{Fore.GREEN}✓ Captcha submitted successfully")
                    print(f"   Captcha ID: {captcha_id}")
                    
                    # Test getting result (sẽ fail vì là test, nhưng API sẽ respond)
                    print(f"{Fore.CYAN}🔍 Testing result retrieval...")
                    await asyncio.sleep(5)
                    
                    async with session.get(f"{self.CAPTCHA_API_URL}/res.php?key={self.captcha_key}&action=get&id={captcha_id}&json=1") as response:
                        result = await response.json()
                        
                    if result.get('request') == 'CAPCHA_NOT_READY':
                        print(f"{Fore.GREEN}✓ Result API working correctly (captcha still processing)")
                        return True
                    else:
                        print(f"{Fore.YELLOW}⚠ Unexpected result: {result}")
                        return True
                        
                else:
                    error_msg = result.get('error_text', result.get('request', 'Unknown error'))
                    print(f"{Fore.RED}✗ Captcha submission failed: {error_msg}")
                    
                    # Giải thích các lỗi
                    if error_msg == "ERROR_ZERO_BALANCE":
                        print(f"{Fore.YELLOW}💡 Tip: Add funds to your 2captcha account")
                    elif error_msg == "ERROR_NO_SLOT_AVAILABLE":
                        print(f"{Fore.YELLOW}💡 Tip: 2captcha is busy, try again later")
                    elif error_msg == "ERROR_WRONG_GOOGLEKEY":
                        print(f"{Fore.YELLOW}💡 Tip: Invalid site key (this is expected for test)")
                    
                    return False
                    
        except Exception as e:
            print(f"{Fore.RED}✗ Error testing captcha submission: {str(e)}")
            return False

    async def run_all_tests(self):
        """Chạy tất cả tests"""
        print(f"{Fore.GREEN + Style.BRIGHT}🧪 2Captcha Integration Test")
        print("=" * 50)
        
        # Test 1: Load API key
        if not self.load_2captcha_key():
            return False
        
        # Test 2: API connection
        if not await self.test_api_connection():
            return False
        
        # Test 3: Check balance
        balance = await self.check_balance()
        if balance is None:
            return False
        
        # Test 4: Test captcha submission (if balance > 0)
        if balance > 0.001:
            await self.test_captcha_submit()
        else:
            print(f"\n{Fore.YELLOW}⚠ Skipping captcha test due to low balance")
        
        print(f"\n{Fore.GREEN}🎉 All basic tests completed!")
        print(f"\n{Fore.CYAN}📋 Summary:")
        print(f"   • API key: Valid")
        print(f"   • Connection: Working")
        print(f"   • Balance: ${balance:.4f}")
        print(f"   • Ready to use: {'Yes' if balance > 0.001 else 'No (add funds)'}")
        
        return True

async def main():
    test = CaptchaTest()
    await test.run_all_tests()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Test cancelled by user")
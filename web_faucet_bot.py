#!/usr/bin/env python3
"""
Web Faucet Bot - Claims ETH from real testnet faucets using web automation
Uses Selenium to interact with faucet websites and 2captcha for solving captchas
"""

from web3 import Web3
from eth_account import Account
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio
import aiohttp
import json
import random
import time
import os

init(autoreset=True)

class WebFaucetBot:
    def __init__(self):
        # Cấu hình các faucet thực tế
        self.faucets = {
            "alchemy": {
                "name": "Alchemy Sepolia Faucet (Recommended)",
                "url": "https://www.alchemy.com/faucets/ethereum-sepolia",
                "rpc_url": "https://eth-sepolia.g.alchemy.com/v2/demo",
                "explorer": "https://sepolia.etherscan.io/tx/",
                "chain_id": 11155111,
                "amount": "up to 1 ETH",
                "cooldown": "24 hours",
                "requires_login": False,
                "selectors": {
                    "address_input": "input[placeholder*='address' i], input[name*='address' i], input[id*='address' i], input[type='text']",
                    "submit_button": "button:contains('Send Me ETH'), button:contains('Drip'), button[type='submit']",
                    "success_message": ".success, .alert-success, [class*='success'], .notification",
                    "error_message": ".error, .alert-error, [class*='error'], .alert"
                }
            },
            "chainlink": {
                "name": "Chainlink Sepolia Faucet",
                "url": "https://faucets.chain.link/sepolia",
                "rpc_url": "https://ethereum-sepolia-rpc.publicnode.com",
                "explorer": "https://sepolia.etherscan.io/tx/",
                "chain_id": 11155111,
                "amount": "0.1 ETH",
                "cooldown": "24 hours",
                "selectors": {
                    "address_input": "input[placeholder*='address' i], input[name*='address' i], input[id*='address' i]",
                    "submit_button": "button[type='submit'], button:contains('Request'), button:contains('Send'), button:contains('Claim')",
                    "success_message": ".success, .alert-success, [class*='success']",
                    "error_message": ".error, .alert-error, [class*='error']"
                }
            },
            "quicknode": {
                "name": "QuickNode Sepolia Faucet",
                "url": "https://faucet.quicknode.com/ethereum/sepolia",
                "rpc_url": "https://ethereum-sepolia-rpc.publicnode.com",
                "explorer": "https://sepolia.etherscan.io/tx/",
                "chain_id": 11155111,
                "amount": "0.05 ETH",
                "cooldown": "12 hours",
                "selectors": {
                    "address_input": "input[placeholder*='address' i], input[name*='address' i], input[id*='address' i]",
                    "submit_button": "button[type='submit'], button:contains('Drip'), button:contains('Request')",
                    "success_message": ".success, .alert-success, [class*='success']",
                    "error_message": ".error, .alert-error, [class*='error']"
                }
            },
            "infura": {
                "name": "Infura Sepolia Faucet",
                "url": "https://www.infura.io/faucet/sepolia",
                "rpc_url": "https://sepolia.infura.io/v3/demo",
                "explorer": "https://sepolia.etherscan.io/tx/",
                "chain_id": 11155111,
                "amount": "0.5 ETH",
                "cooldown": "24 hours",
                "requires_login": False,
                "selectors": {
                    "address_input": "input[placeholder*='address' i], input[name*='address' i], input[id*='address' i], input[type='text']",
                    "submit_button": "button:contains('RECEIVE'), button:contains('Request'), button[type='submit']",
                    "success_message": ".success, .alert-success, [class*='success']",
                    "error_message": ".error, .alert-error, [class*='error']"
                }
            }
        }
        
        self.driver = None
        self.wait = None
        self.captcha_key = None
        self.accounts = []
        self.config = {}
        
    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{Fore.CYAN}[{timestamp}]{Style.RESET_ALL} {message}")

    def setup_driver(self):
        """Thiết lập Chrome WebDriver"""
        try:
            self.log(f"{Fore.CYAN}🔧 Setting up Chrome WebDriver...")
            
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument(f'--user-agent={FakeUserAgent().random}')
            
            # Chạy headless nếu không cần debug
            if self.config.get('headless', True):
                chrome_options.add_argument('--headless')
            
            # Tự động download ChromeDriver
            service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 30)
            
            self.log(f"{Fore.GREEN}✓ WebDriver setup completed")
            return True
            
        except Exception as e:
            self.log(f"{Fore.RED}✗ Failed to setup WebDriver: {str(e)}")
            return False

    def load_config(self):
        """Load cấu hình từ file"""
        try:
            with open('config.json', 'r') as file:
                self.config = json.load(file)
                self.log(f"{Fore.GREEN}✓ Configuration loaded")
                return True
        except FileNotFoundError:
            self.config = {
                "headless": False,  # Set False để xem browser hoạt động
                "claim_interval": 3600,
                "max_retries": 3,
                "timeout": 30
            }
            self.log(f"{Fore.YELLOW}⚠ Using default configuration")
            return True
        except Exception as e:
            self.log(f"{Fore.RED}✗ Error loading config: {e}")
            return False

    def load_accounts(self):
        """Load danh sách private keys"""
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip() and not line.startswith('#')]
                
            valid_accounts = []
            for private_key in accounts:
                try:
                    account = Account.from_key(private_key)
                    valid_accounts.append({
                        'private_key': private_key,
                        'address': account.address
                    })
                except Exception as e:
                    self.log(f"{Fore.RED}✗ Invalid private key: {private_key[:10]}...")
                    
            self.accounts = valid_accounts
            self.log(f"{Fore.GREEN}✓ Loaded {len(valid_accounts)} valid accounts")
            return len(valid_accounts) > 0
            
        except FileNotFoundError:
            self.log(f"{Fore.RED}✗ accounts.txt file not found")
            return False

    def load_2captcha_key(self):
        """Load 2captcha API key"""
        try:
            with open('2captcha_key.txt', 'r') as file:
                key = file.read().strip()
                if key and key != "your_2captcha_api_key_here":
                    self.captcha_key = key
                    self.log(f"{Fore.GREEN}✓ 2Captcha API key loaded")
                    return True
                else:
                    self.log(f"{Fore.YELLOW}⚠ 2captcha key not configured (captcha solving disabled)")
                    return True  # Không bắt buộc phải có
        except FileNotFoundError:
            self.log(f"{Fore.YELLOW}⚠ 2captcha_key.txt not found (captcha solving disabled)")
            return True

    async def solve_recaptcha(self, site_key, page_url):
        """Giải reCAPTCHA sử dụng 2captcha"""
        if not self.captcha_key:
            self.log(f"{Fore.YELLOW}⚠ No 2captcha key - skipping captcha")
            return None

        try:
            async with aiohttp.ClientSession() as session:
                # Submit captcha
                submit_data = {
                    'key': self.captcha_key,
                    'method': 'userrecaptcha',
                    'googlekey': site_key,
                    'pageurl': page_url,
                    'json': 1
                }
                
                async with session.post('http://2captcha.com/in.php', data=submit_data) as response:
                    result = await response.json()
                    
                if result.get('status') != 1:
                    self.log(f"{Fore.RED}✗ Captcha submit failed: {result.get('error_text')}")
                    return None
                
                captcha_id = result['request']
                self.log(f"{Fore.YELLOW}⏳ Solving captcha... ID: {captcha_id}")
                
                # Wait for result
                for attempt in range(60):  # Max 10 minutes
                    await asyncio.sleep(10)
                    
                    async with session.get(f'http://2captcha.com/res.php?key={self.captcha_key}&action=get&id={captcha_id}&json=1') as response:
                        result = await response.json()
                        
                    if result.get('status') == 1:
                        self.log(f"{Fore.GREEN}✓ Captcha solved successfully")
                        return result['request']
                    elif result.get('request') != 'CAPCHA_NOT_READY':
                        self.log(f"{Fore.RED}✗ Captcha failed: {result.get('request')}")
                        return None
                
                self.log(f"{Fore.RED}✗ Captcha timeout")
                return None
                
        except Exception as e:
            self.log(f"{Fore.RED}✗ Captcha error: {str(e)}")
            return None

    def wait_for_element(self, selector, timeout=30):
        """Chờ element xuất hiện"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element
        except TimeoutException:
            return None

    def find_element_by_selectors(self, selectors):
        """Tìm element bằng nhiều selector"""
        if isinstance(selectors, str):
            selectors = [selectors]
            
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    return element
            except NoSuchElementException:
                continue
        return None

    async def claim_from_faucet(self, faucet_config, address):
        """Claim ETH từ một faucet cụ thể"""
        faucet_name = faucet_config['name']
        faucet_url = faucet_config['url']
        
        try:
            self.log(f"{Fore.CYAN}🌐 Opening {faucet_name}...")
            self.driver.get(faucet_url)
            
            # Chờ page load
            time.sleep(3)
            
            # Tìm input field cho address
            selectors = faucet_config['selectors']
            address_input = self.find_element_by_selectors([
                selectors['address_input'],
                "input[type='text']",
                "input[placeholder*='0x']",
                "input"
            ])
            
            if not address_input:
                self.log(f"{Fore.RED}✗ Could not find address input field")
                return False
            
            # Nhập address
            self.log(f"{Fore.CYAN}📝 Entering address...")
            address_input.clear()
            address_input.send_keys(address)
            time.sleep(1)
            
            # Kiểm tra reCAPTCHA
            recaptcha_frames = self.driver.find_elements(By.CSS_SELECTOR, "iframe[src*='recaptcha']")
            recaptcha_divs = self.driver.find_elements(By.CSS_SELECTOR, ".g-recaptcha, [data-sitekey]")
            
            if (recaptcha_frames or recaptcha_divs) and self.captcha_key:
                self.log(f"{Fore.YELLOW}🧩 Detected reCAPTCHA, solving...")
                
                # Try to extract real site key
                site_key = None
                try:
                    # Look for data-sitekey attribute
                    for elem in recaptcha_divs:
                        if elem.get_attribute('data-sitekey'):
                            site_key = elem.get_attribute('data-sitekey')
                            break
                    
                    # Look in page source for site key
                    if not site_key:
                        page_source = self.driver.page_source
                        import re
                        site_key_match = re.search(r'data-sitekey="([^"]+)"', page_source)
                        if site_key_match:
                            site_key = site_key_match.group(1)
                        else:
                            # Look for sitekey in script
                            site_key_match = re.search(r'sitekey["\s]*:["\s]*([^"]+)', page_source)
                            if site_key_match:
                                site_key = site_key_match.group(1)
                    
                    if not site_key:
                        site_key = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"  # Fallback
                        self.log(f"{Fore.YELLOW}⚠ Using fallback site key")
                    else:
                        self.log(f"{Fore.GREEN}✓ Extracted site key: {site_key[:20]}...")
                        
                except Exception as e:
                    site_key = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
                    self.log(f"{Fore.YELLOW}⚠ Error extracting site key, using fallback: {e}")
                
                captcha_token = await self.solve_recaptcha(site_key, faucet_url)
                
                if captcha_token:
                    # Try multiple methods to inject captcha solution
                    try:
                        # Method 1: Direct injection
                        self.driver.execute_script(f"""
                            var responses = document.getElementsByName('g-recaptcha-response');
                            for (var i = 0; i < responses.length; i++) {{
                                responses[i].innerHTML = '{captcha_token}';
                                responses[i].value = '{captcha_token}';
                            }}
                        """)
                        
                        # Method 2: Override grecaptcha
                        self.driver.execute_script(f"""
                            if (typeof grecaptcha !== 'undefined') {{
                                grecaptcha.getResponse = function() {{ return '{captcha_token}'; }};
                                if (grecaptcha.execute) {{
                                    grecaptcha.execute();
                                }}
                            }}
                        """)
                        
                        # Method 3: Trigger callback if exists
                        self.driver.execute_script(f"""
                            if (window.recaptchaCallback) {{
                                window.recaptchaCallback('{captcha_token}');
                            }}
                        """)
                        
                        self.log(f"{Fore.GREEN}✓ Captcha solution injected")
                        time.sleep(2)
                        
                    except Exception as e:
                        self.log(f"{Fore.YELLOW}⚠ Error injecting captcha: {e}")
                        
            elif recaptcha_frames or recaptcha_divs:
                self.log(f"{Fore.YELLOW}⚠ reCAPTCHA detected but no 2captcha key - you may need to solve manually")
                time.sleep(5)  # Give user time to solve manually
            
            # Tìm và click submit button
            submit_button = self.find_element_by_selectors([
                selectors['submit_button'],
                "button[type='submit']",
                "button:contains('Send')",
                "button:contains('Request')",
                "button:contains('Claim')",
                "input[type='submit']"
            ])
            
            if not submit_button:
                self.log(f"{Fore.RED}✗ Could not find submit button")
                return False
            
            self.log(f"{Fore.CYAN}🚀 Submitting claim request...")
            submit_button.click()
            
            # Chờ kết quả
            time.sleep(5)
            
            # Kiểm tra success message
            success_elements = self.driver.find_elements(By.CSS_SELECTOR, selectors['success_message'])
            error_elements = self.driver.find_elements(By.CSS_SELECTOR, selectors['error_message'])
            
            # Kiểm tra page content
            page_text = self.driver.page_source.lower()
            
            if any(elem.is_displayed() for elem in success_elements) or \
               any(keyword in page_text for keyword in ['success', 'sent', 'transaction', 'txn', 'hash']):
                self.log(f"{Fore.GREEN}✓ Claim appears successful!")
                
                # Tìm transaction hash nếu có
                tx_patterns = [
                    r'0x[a-fA-F0-9]{64}',
                    r'txn[:\s]*([a-fA-F0-9]{64})',
                    r'hash[:\s]*([a-fA-F0-9]{64})'
                ]
                
                for pattern in tx_patterns:
                    import re
                    matches = re.findall(pattern, page_text)
                    if matches:
                        tx_hash = matches[0] if isinstance(matches[0], str) else matches[0][0]
                        explorer_url = f"{faucet_config['explorer']}{tx_hash}"
                        self.log(f"{Fore.BLUE}🔗 Transaction: {explorer_url}")
                        break
                
                return True
                
            elif any(elem.is_displayed() for elem in error_elements) or \
                 any(keyword in page_text for keyword in ['error', 'failed', 'limit', 'cooldown']):
                error_text = ""
                for elem in error_elements:
                    if elem.is_displayed():
                        error_text = elem.text
                        break
                
                self.log(f"{Fore.RED}✗ Claim failed: {error_text or 'Unknown error'}")
                return False
            else:
                self.log(f"{Fore.YELLOW}⚠ Unclear result - check manually")
                return False
                
        except Exception as e:
            self.log(f"{Fore.RED}✗ Error claiming from {faucet_name}: {str(e)}")
            return False

    async def check_balance(self, address, rpc_url):
        """Kiểm tra balance của address"""
        try:
            web3 = Web3(Web3.HTTPProvider(rpc_url))
            balance_wei = web3.eth.get_balance(address)
            balance_eth = web3.from_wei(balance_wei, 'ether')
            return float(balance_eth)
        except Exception as e:
            self.log(f"{Fore.RED}✗ Error checking balance: {str(e)}")
            return 0

    def select_faucet(self):
        """Cho phép user chọn faucet"""
        print(f"\n{Fore.YELLOW}Available Faucets:")
        print("-" * 70)
        
        for i, (key, faucet) in enumerate(self.faucets.items(), 1):
            login_icon = "🔐" if faucet.get('requires_login') else "🌐"
            
            print(f"{Fore.WHITE}{i}. {login_icon} {faucet['name']}")
            print(f"   💰 Amount: {faucet['amount']}")
            print(f"   ⏰ Cooldown: {faucet['cooldown']}")
            
            if faucet.get('requires_login'):
                print(f"   {Fore.YELLOW}⚠️  Requires account login{Style.RESET_ALL}")
            else:
                print(f"   {Fore.GREEN}✅ No login required{Style.RESET_ALL}")
            print()
        
        while True:
            try:
                choice = int(input(f"\n{Fore.CYAN}Select faucet (1-{len(self.faucets)}): "))
                if 1 <= choice <= len(self.faucets):
                    selected_key = list(self.faucets.keys())[choice - 1]
                    return self.faucets[selected_key]
                else:
                    print(f"{Fore.RED}Invalid choice. Please select 1-{len(self.faucets)}")
            except ValueError:
                print(f"{Fore.RED}Please enter a valid number")

    def mask_address(self, address):
        """Ẩn một phần address"""
        return f"{address[:6]}...{address[-4:]}"

    async def process_account(self, account, faucet_config):
        """Xử lý một account"""
        address = account['address']
        masked_address = self.mask_address(address)
        
        self.log(f"{Fore.CYAN}{'='*60}")
        self.log(f"{Fore.WHITE}🔄 Processing account: {masked_address}")
        self.log(f"{Fore.CYAN}{'='*60}")
        
        # Kiểm tra balance trước khi claim
        balance_before = await self.check_balance(address, faucet_config['rpc_url'])
        self.log(f"{Fore.CYAN}💰 Current balance: {balance_before:.6f} ETH")
        
        # Claim từ faucet
        success = await self.claim_from_faucet(faucet_config, address)
        
        if success:
            # Chờ một chút rồi kiểm tra balance mới
            self.log(f"{Fore.CYAN}⏳ Waiting for transaction confirmation...")
            await asyncio.sleep(60)
            
            balance_after = await self.check_balance(address, faucet_config['rpc_url'])
            received = balance_after - balance_before
            
            if received > 0:
                self.log(f"{Fore.GREEN}💎 Received: {received:.6f} ETH")
                self.log(f"{Fore.GREEN}💰 New balance: {balance_after:.6f} ETH")
            else:
                self.log(f"{Fore.YELLOW}⚠ Balance unchanged - transaction may be pending")
            
            self.log(f"{Fore.GREEN}✅ Account {masked_address} processed successfully")
            return True
        else:
            self.log(f"{Fore.RED}❌ Failed to process account {masked_address}")
            return False

    async def main(self):
        """Hàm chính"""
        try:
            print(f"{Fore.GREEN + Style.BRIGHT}🤖 Web Faucet Bot - Real Testnet Claims")
            print("=" * 60)
            
            # Load cấu hình
            if not self.load_config():
                return
            
            # Load accounts
            if not self.load_accounts():
                return
            
            # Load 2captcha key (optional)
            self.load_2captcha_key()
            
            # Setup WebDriver
            if not self.setup_driver():
                return
            
            # Chọn faucet
            selected_faucet = self.select_faucet()
            self.log(f"{Fore.GREEN}✓ Selected: {selected_faucet['name']}")
            
            if selected_faucet.get('requires_login'):
                self.log(f"{Fore.YELLOW}⚠️  This faucet requires manual login")
                self.log(f"{Fore.YELLOW}   Please login manually when browser opens")
                input(f"{Fore.CYAN}Press Enter when ready to continue...")
            
            # Hiển thị thông tin
            self.log(f"{Fore.WHITE}📊 Total accounts: {len(self.accounts)}")
            self.log(f"{Fore.WHITE}🌐 Target faucet: {selected_faucet['name']}")
            
            successful_claims = 0
            failed_claims = 0
            
            for i, account in enumerate(self.accounts, 1):
                self.log(f"\n{Fore.BLUE}📍 Account {i}/{len(self.accounts)}")
                
                success = await self.process_account(account, selected_faucet)
                
                if success:
                    successful_claims += 1
                else:
                    failed_claims += 1
                
                # Delay giữa các accounts
                if i < len(self.accounts):
                    delay = random.randint(30, 60)
                    self.log(f"{Fore.YELLOW}⏳ Waiting {delay}s before next account...")
                    await asyncio.sleep(delay)
            
            # Báo cáo kết quả
            self.log(f"\n{Fore.CYAN}{'='*60}")
            self.log(f"{Fore.GREEN}✅ Successful claims: {successful_claims}")
            self.log(f"{Fore.RED}❌ Failed claims: {failed_claims}")
            self.log(f"{Fore.CYAN}{'='*60}")
            
        except KeyboardInterrupt:
            self.log(f"\n{Fore.YELLOW}👋 Bot stopped by user")
        except Exception as e:
            self.log(f"\n{Fore.RED}💥 Unexpected error: {str(e)}")
        finally:
            if self.driver:
                self.log(f"{Fore.CYAN}🧹 Closing browser...")
                self.driver.quit()

if __name__ == "__main__":
    try:
        bot = WebFaucetBot()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(f"\n{Fore.CYAN}👋 Goodbye!")
    except Exception as e:
        print(f"\n{Fore.RED}💥 Error: {e}")
from web3 import Web3
from eth_account import Account
from aiohttp import ClientSession, ClientTimeout, ClientResponseError
from fake_useragent import FakeUserAgent
from datetime import datetime, timezone
from colorama import *
import asyncio
import json
import random
import time
import os

init(autoreset=True)

class EthFaucetBot:
    def __init__(self):
        # Cấu hình các faucet ETH testnet phổ biến
        self.faucets = {
            "sepolia": {
                "name": "Sepolia Testnet",
                "rpc_url": "https://ethereum-sepolia-rpc.publicnode.com",
                "explorer": "https://sepolia.etherscan.io/tx/",
                "chain_id": 11155111,
                "faucet_url": "https://sepoliafaucet.com/api/claim",
                "site_key": "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"  # Test site key
            },
            "goerli": {
                "name": "Goerli Testnet", 
                "rpc_url": "https://ethereum-goerli-rpc.publicnode.com",
                "explorer": "https://goerli.etherscan.io/tx/",
                "chain_id": 5,
                "faucet_url": "https://goerlifaucet.com/api/claim",
                "site_key": "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
            }
        }
        
        # API endpoints
        self.CAPTCHA_API_URL = "http://2captcha.com"
        self.captcha_key = None
        self.accounts = []
        self.config = {}
        
        # Headers cho requests
        self.headers = {
            'User-Agent': FakeUserAgent().random,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Origin': 'https://sepoliafaucet.com',
            'Referer': 'https://sepoliafaucet.com/'
        }

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{Fore.CYAN}[{timestamp}]{Style.RESET_ALL} {message}")

    def welcome(self):
        print(f"""
{Fore.GREEN + Style.BRIGHT}╔══════════════════════════════════════════════════════════════╗
║                    ETH TESTNET FAUCET BOT                   ║
║                     Auto Claim with 2Captcha                ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """)

    def load_config(self):
        """Load cấu hình từ file config.json"""
        try:
            with open('config.json', 'r') as file:
                self.config = json.load(file)
                self.log(f"{Fore.GREEN}✓ Loaded configuration successfully")
                return True
        except FileNotFoundError:
            self.log(f"{Fore.YELLOW}⚠ Config file not found, using default settings")
            self.config = {
                "claim_interval": 3600,  # 1 giờ
                "max_retries": 3,
                "timeout": 30,
                "selected_faucet": "sepolia"
            }
            return False
        except json.JSONDecodeError as e:
            self.log(f"{Fore.RED}✗ Error parsing config file: {e}")
            return False

    def load_accounts(self):
        """Load danh sách private keys từ file accounts.txt"""
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
                
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
        """Load 2captcha API key từ file"""
        try:
            with open('2captcha_key.txt', 'r') as file:
                key = file.read().strip()
                if key and key != "your_2captcha_key":
                    self.captcha_key = key
                    self.log(f"{Fore.GREEN}✓ 2Captcha API key loaded")
                    return True
                else:
                    self.log(f"{Fore.YELLOW}⚠ Please add your 2captcha API key to 2captcha_key.txt")
                    return False
        except FileNotFoundError:
            self.log(f"{Fore.RED}✗ 2captcha_key.txt file not found")
            return False

    async def solve_recaptcha(self, site_key, page_url):
        """Giải reCAPTCHA sử dụng 2captcha service"""
        if not self.captcha_key:
            self.log(f"{Fore.RED}✗ No 2captcha API key provided")
            return None

        try:
            async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                # Gửi captcha để giải
                submit_data = {
                    'key': self.captcha_key,
                    'method': 'userrecaptcha',
                    'googlekey': site_key,
                    'pageurl': page_url,
                    'json': 1
                }
                
                async with session.post(f"{self.CAPTCHA_API_URL}/in.php", data=submit_data) as response:
                    result = await response.json()
                    
                if result['status'] != 1:
                    self.log(f"{Fore.RED}✗ Failed to submit captcha: {result.get('error_text', 'Unknown error')}")
                    return None
                
                captcha_id = result['request']
                self.log(f"{Fore.YELLOW}⏳ Solving captcha... ID: {captcha_id}")
                
                # Chờ kết quả
                for attempt in range(30):  # Tối đa 5 phút
                    await asyncio.sleep(10)
                    
                    async with session.get(f"{self.CAPTCHA_API_URL}/res.php?key={self.captcha_key}&action=get&id={captcha_id}&json=1") as response:
                        result = await response.json()
                        
                    if result['status'] == 1:
                        self.log(f"{Fore.GREEN}✓ Captcha solved successfully")
                        return result['request']
                    elif result['error_text'] != 'CAPCHA_NOT_READY':
                        self.log(f"{Fore.RED}✗ Captcha solving failed: {result.get('error_text')}")
                        return None
                
                self.log(f"{Fore.RED}✗ Captcha solving timeout")
                return None
                
        except Exception as e:
            self.log(f"{Fore.RED}✗ Error solving captcha: {str(e)}")
            return None

    async def check_balance(self, address, faucet_config):
        """Kiểm tra balance hiện tại của address"""
        try:
            web3 = Web3(Web3.HTTPProvider(faucet_config['rpc_url']))
            balance_wei = web3.eth.get_balance(address)
            balance_eth = web3.from_wei(balance_wei, 'ether')
            return float(balance_eth)
        except Exception as e:
            self.log(f"{Fore.RED}✗ Error checking balance: {str(e)}")
            return 0

    async def claim_faucet(self, account, faucet_config):
        """Claim ETH từ faucet"""
        address = account['address']
        
        try:
            # Kiểm tra balance trước khi claim
            balance_before = await self.check_balance(address, faucet_config)
            self.log(f"{Fore.CYAN}💰 Current balance: {balance_before:.6f} ETH")
            
            # Giải captcha
            self.log(f"{Fore.YELLOW}🔄 Solving captcha for {address[:10]}...")
            captcha_token = await self.solve_recaptcha(
                faucet_config['site_key'], 
                faucet_config['faucet_url']
            )
            
            if not captcha_token:
                return False
            
            # Gửi request claim
            async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                claim_data = {
                    'address': address,
                    'captcha': captcha_token
                }
                
                async with session.post(
                    faucet_config['faucet_url'], 
                    json=claim_data, 
                    headers=self.headers
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get('success'):
                            tx_hash = result.get('txHash')
                            self.log(f"{Fore.GREEN}✓ Claim successful!")
                            
                            if tx_hash:
                                explorer_url = f"{faucet_config['explorer']}{tx_hash}"
                                self.log(f"{Fore.BLUE}🔗 Transaction: {explorer_url}")
                            
                            # Chờ một chút rồi kiểm tra balance mới
                            await asyncio.sleep(30)
                            balance_after = await self.check_balance(address, faucet_config)
                            received = balance_after - balance_before
                            
                            if received > 0:
                                self.log(f"{Fore.GREEN}💎 Received: {received:.6f} ETH")
                                self.log(f"{Fore.GREEN}💰 New balance: {balance_after:.6f} ETH")
                            
                            return True
                        else:
                            error_msg = result.get('message', 'Unknown error')
                            self.log(f"{Fore.RED}✗ Claim failed: {error_msg}")
                            return False
                    else:
                        self.log(f"{Fore.RED}✗ HTTP Error: {response.status}")
                        return False
                        
        except ClientResponseError as e:
            self.log(f"{Fore.RED}✗ Request error: {e}")
            return False
        except Exception as e:
            self.log(f"{Fore.RED}✗ Unexpected error: {str(e)}")
            return False

    def mask_address(self, address):
        """Ẩn một phần address để bảo mật"""
        return f"{address[:6]}...{address[-4:]}"

    async def process_account(self, account, faucet_config):
        """Xử lý một account"""
        address = account['address']
        masked_address = self.mask_address(address)
        
        self.log(f"{Fore.CYAN}{'='*60}")
        self.log(f"{Fore.WHITE}🔄 Processing account: {masked_address}")
        self.log(f"{Fore.CYAN}{'='*60}")
        
        success = await self.claim_faucet(account, faucet_config)
        
        if success:
            self.log(f"{Fore.GREEN}✅ Account {masked_address} processed successfully")
        else:
            self.log(f"{Fore.RED}❌ Failed to process account {masked_address}")
        
        return success

    def select_faucet(self):
        """Cho phép user chọn faucet"""
        print(f"\n{Fore.YELLOW}Available Faucets:")
        for i, (key, faucet) in enumerate(self.faucets.items(), 1):
            print(f"{Fore.WHITE}{i}. {faucet['name']}")
        
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

    async def main(self):
        """Hàm chính của bot"""
        try:
            self.clear_terminal()
            self.welcome()
            
            # Load cấu hình
            self.load_config()
            
            # Load accounts
            if not self.load_accounts():
                self.log(f"{Fore.RED}✗ No valid accounts found. Exiting...")
                return
            
            # Load 2captcha key
            if not self.load_2captcha_key():
                self.log(f"{Fore.RED}✗ 2captcha API key required. Exiting...")
                return
            
            # Chọn faucet
            selected_faucet = self.select_faucet()
            self.log(f"{Fore.GREEN}✓ Selected: {selected_faucet['name']}")
            
            # Hiển thị thông tin
            self.log(f"{Fore.WHITE}📊 Total accounts: {len(self.accounts)}")
            self.log(f"{Fore.WHITE}⏱️  Claim interval: {self.config.get('claim_interval', 3600)} seconds")
            
            while True:
                self.log(f"\n{Fore.MAGENTA}🚀 Starting claim cycle...")
                
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
                        delay = random.randint(10, 30)
                        self.log(f"{Fore.YELLOW}⏳ Waiting {delay}s before next account...")
                        await asyncio.sleep(delay)
                
                # Báo cáo kết quả
                self.log(f"\n{Fore.CYAN}{'='*60}")
                self.log(f"{Fore.GREEN}✅ Successful claims: {successful_claims}")
                self.log(f"{Fore.RED}❌ Failed claims: {failed_claims}")
                self.log(f"{Fore.CYAN}{'='*60}")
                
                # Chờ đến chu kỳ tiếp theo
                wait_time = self.config.get('claim_interval', 3600)
                self.log(f"\n{Fore.YELLOW}⏰ Waiting {wait_time}s until next cycle...")
                
                for remaining in range(wait_time, 0, -1):
                    hours, remainder = divmod(remaining, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    
                    print(f"\r{Fore.CYAN}⏳ Next cycle in: {time_str}", end="", flush=True)
                    await asyncio.sleep(1)
                
                print()  # New line after countdown
                
        except KeyboardInterrupt:
            self.log(f"\n{Fore.YELLOW}👋 Bot stopped by user")
        except Exception as e:
            self.log(f"\n{Fore.RED}💥 Unexpected error: {str(e)}")
            raise

if __name__ == "__main__":
    try:
        bot = EthFaucetBot()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(f"\n{Fore.CYAN}👋 Goodbye!")
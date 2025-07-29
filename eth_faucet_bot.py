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
        # Cấu hình các faucet ETH testnet
        self.faucets = {
            "simulator": {
                "name": "Test Faucet Simulator (Local)",
                "rpc_url": "https://ethereum-sepolia-rpc.publicnode.com",
                "explorer": "https://sepolia.etherscan.io/tx/",
                "chain_id": 11155111,
                "faucet_url": "http://localhost:8080/api/claim",
                "site_key": "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI",  # Test site key
                "type": "api",
                "amount": "0.05-0.5 ETH",
                "cooldown": "1 hour"
            },
            "sepolia_alchemy": {
                "name": "Sepolia Testnet (Alchemy)",
                "rpc_url": "https://ethereum-sepolia-rpc.publicnode.com",
                "explorer": "https://sepolia.etherscan.io/tx/",
                "chain_id": 11155111,
                "faucet_url": "https://sepoliafaucet.com/",
                "site_key": "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI",  # Test site key
                "type": "web_form",
                "amount": "0.5 ETH",
                "cooldown": "24 hours"
            },
            "sepolia_quicknode": {
                "name": "Sepolia Testnet (QuickNode)",
                "rpc_url": "https://ethereum-sepolia-rpc.publicnode.com", 
                "explorer": "https://sepolia.etherscan.io/tx/",
                "chain_id": 11155111,
                "faucet_url": "https://faucet.quicknode.com/ethereum/sepolia",
                "site_key": "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI",
                "type": "web_form", 
                "amount": "0.1 ETH",
                "cooldown": "24 hours"
            },
            "sepolia_chainlink": {
                "name": "Sepolia Testnet (Chainlink)",
                "rpc_url": "https://ethereum-sepolia-rpc.publicnode.com",
                "explorer": "https://sepolia.etherscan.io/tx/",
                "chain_id": 11155111,
                "faucet_url": "https://faucets.chain.link/sepolia",
                "site_key": "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI",
                "type": "web_form",
                "amount": "0.1 ETH", 
                "cooldown": "24 hours"
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

    async def check_2captcha_balance(self):
        """Kiểm tra balance 2captcha"""
        if not self.captcha_key:
            return None
        
        try:
            async with ClientSession(timeout=ClientTimeout(total=10)) as session:
                async with session.get(f"{self.CAPTCHA_API_URL}/res.php?key={self.captcha_key}&action=getbalance") as response:
                    balance_text = await response.text()
                    
                if balance_text.startswith('ERROR'):
                    self.log(f"{Fore.RED}✗ 2captcha balance check failed: {balance_text}")
                    return None
                else:
                    balance = float(balance_text)
                    self.log(f"{Fore.CYAN}💰 2captcha balance: ${balance:.4f}")
                    return balance
                    
        except Exception as e:
            self.log(f"{Fore.YELLOW}⚠ Could not check 2captcha balance: {str(e)}")
            return None

    async def solve_recaptcha(self, site_key, page_url, max_retries=3):
        """Giải reCAPTCHA sử dụng 2captcha service với retry logic"""
        if not self.captcha_key:
            self.log(f"{Fore.RED}✗ No 2captcha API key provided")
            return None

        # Kiểm tra balance trước khi giải captcha
        balance = await self.check_2captcha_balance()
        if balance is not None and balance < 0.001:
            self.log(f"{Fore.RED}✗ Insufficient 2captcha balance: ${balance:.4f}")
            return None

        for retry in range(max_retries):
            if retry > 0:
                self.log(f"{Fore.YELLOW}🔄 Retrying captcha solve... Attempt {retry + 1}/{max_retries}")
                await asyncio.sleep(5)

            try:
                async with ClientSession(timeout=ClientTimeout(total=60)) as session:
                    # Gửi captcha để giải
                    submit_data = {
                        'key': self.captcha_key,
                        'method': 'userrecaptcha',
                        'googlekey': site_key,
                        'pageurl': page_url,
                        'json': 1
                    }
                    
                    self.log(f"{Fore.CYAN}📤 Submitting captcha to 2captcha...")
                    async with session.post(f"{self.CAPTCHA_API_URL}/in.php", data=submit_data) as response:
                        if response.status != 200:
                            self.log(f"{Fore.RED}✗ HTTP error submitting captcha: {response.status}")
                            continue
                            
                        result = await response.json()
                        
                    if result.get('status') != 1:
                        error_msg = result.get('error_text', result.get('request', 'Unknown error'))
                        self.log(f"{Fore.RED}✗ Failed to submit captcha: {error_msg}")
                        
                        # Xử lý các lỗi cụ thể
                        if error_msg in ['ERROR_ZERO_BALANCE', 'ERROR_NO_SLOT_AVAILABLE']:
                            self.log(f"{Fore.RED}💳 2captcha service issue: {error_msg}")
                            return None
                        continue
                    
                    captcha_id = result['request']
                    self.log(f"{Fore.YELLOW}⏳ Solving captcha... ID: {captcha_id}")
                    
                    # Chờ kết quả với timeout thông minh
                    max_wait_time = 300  # 5 phút
                    wait_interval = 10   # Kiểm tra mỗi 10 giây
                    waited_time = 0
                    
                    while waited_time < max_wait_time:
                        await asyncio.sleep(wait_interval)
                        waited_time += wait_interval
                        
                        try:
                            async with session.get(f"{self.CAPTCHA_API_URL}/res.php?key={self.captcha_key}&action=get&id={captcha_id}&json=1") as response:
                                if response.status != 200:
                                    self.log(f"{Fore.YELLOW}⚠ HTTP error checking captcha result: {response.status}")
                                    continue
                                    
                                result = await response.json()
                                
                        except Exception as e:
                            self.log(f"{Fore.YELLOW}⚠ Error checking captcha result: {str(e)}")
                            continue
                        
                        if result.get('status') == 1:
                            self.log(f"{Fore.GREEN}✓ Captcha solved successfully in {waited_time}s")
                            return result['request']
                        elif result.get('request') == 'CAPCHA_NOT_READY':
                            # Vẫn đang xử lý, tiếp tục chờ
                            progress_bar = "█" * (waited_time // 30) + "░" * (10 - waited_time // 30)
                            self.log(f"{Fore.CYAN}⏳ [{progress_bar}] Waiting... {waited_time}s/{max_wait_time}s")
                            continue
                        else:
                            error_msg = result.get('request', 'Unknown error')
                            self.log(f"{Fore.RED}✗ Captcha solving failed: {error_msg}")
                            break
                    
                    if waited_time >= max_wait_time:
                        self.log(f"{Fore.RED}✗ Captcha solving timeout after {max_wait_time}s")
                        # Report bad captcha để không bị charge
                        try:
                            async with session.get(f"{self.CAPTCHA_API_URL}/res.php?key={self.captcha_key}&action=reportbad&id={captcha_id}") as response:
                                self.log(f"{Fore.YELLOW}📝 Reported bad captcha to get refund")
                        except:
                            pass
                        continue
                        
            except asyncio.TimeoutError:
                self.log(f"{Fore.RED}✗ Timeout connecting to 2captcha service")
                continue
            except Exception as e:
                self.log(f"{Fore.RED}✗ Error solving captcha: {str(e)}")
                continue
        
        self.log(f"{Fore.RED}✗ Failed to solve captcha after {max_retries} attempts")
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

    async def claim_faucet(self, account, faucet_config, max_retries=2):
        """Claim ETH từ faucet với retry logic"""
        address = account['address']
        
        for attempt in range(max_retries):
            if attempt > 0:
                self.log(f"{Fore.YELLOW}🔄 Retrying claim... Attempt {attempt + 1}/{max_retries}")
                await asyncio.sleep(10)
            
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
                    self.log(f"{Fore.RED}✗ Failed to solve captcha")
                    if attempt < max_retries - 1:
                        continue
                    return False
                
                # Gửi request claim với retry
                claim_success = False
                for claim_attempt in range(3):  # Retry claim request 3 lần
                    try:
                        async with ClientSession(timeout=ClientTimeout(total=45)) as session:
                            claim_data = {
                                'address': address,
                                'captcha': captcha_token
                            }
                            
                            self.log(f"{Fore.CYAN}📤 Submitting claim request...")
                            async with session.post(
                                faucet_config['faucet_url'], 
                                json=claim_data, 
                                headers=self.headers
                            ) as response:
                                
                                response_text = await response.text()
                                
                                if response.status == 200:
                                    try:
                                        result = await response.json()
                                    except:
                                        # Nếu không parse được JSON, thử với text response
                                        self.log(f"{Fore.YELLOW}⚠ Non-JSON response: {response_text[:100]}...")
                                        if "success" in response_text.lower() or "sent" in response_text.lower():
                                            claim_success = True
                                            break
                                        else:
                                            continue
                                    
                                    if result.get('success') or result.get('status') == 'success':
                                        tx_hash = result.get('txHash') or result.get('hash') or result.get('transactionHash')
                                        self.log(f"{Fore.GREEN}✓ Claim successful!")
                                        
                                        if tx_hash:
                                            explorer_url = f"{faucet_config['explorer']}{tx_hash}"
                                            self.log(f"{Fore.BLUE}🔗 Transaction: {explorer_url}")
                                        
                                        claim_success = True
                                        break
                                    else:
                                        error_msg = result.get('message') or result.get('error') or 'Unknown error'
                                        self.log(f"{Fore.RED}✗ Claim failed: {error_msg}")
                                        
                                        # Kiểm tra lỗi rate limit
                                        if any(keyword in error_msg.lower() for keyword in ['rate limit', 'too many', 'wait', 'cooldown']):
                                            self.log(f"{Fore.YELLOW}⏰ Rate limited, this is normal")
                                            return False
                                        
                                        if claim_attempt < 2:
                                            await asyncio.sleep(5)
                                            continue
                                        else:
                                            return False
                                            
                                elif response.status == 429:
                                    self.log(f"{Fore.YELLOW}⚠ Rate limited (HTTP 429)")
                                    return False
                                elif response.status >= 500:
                                    self.log(f"{Fore.YELLOW}⚠ Server error: {response.status}, retrying...")
                                    if claim_attempt < 2:
                                        await asyncio.sleep(10)
                                        continue
                                    else:
                                        return False
                                else:
                                    self.log(f"{Fore.RED}✗ HTTP Error: {response.status}")
                                    self.log(f"{Fore.RED}Response: {response_text[:200]}...")
                                    if claim_attempt < 2:
                                        await asyncio.sleep(5)
                                        continue
                                    else:
                                        return False
                                        
                    except asyncio.TimeoutError:
                        self.log(f"{Fore.RED}✗ Request timeout")
                        if claim_attempt < 2:
                            await asyncio.sleep(5)
                            continue
                        else:
                            return False
                    except Exception as e:
                        self.log(f"{Fore.RED}✗ Request error: {str(e)}")
                        if claim_attempt < 2:
                            await asyncio.sleep(5)
                            continue
                        else:
                            return False
                
                if claim_success:
                    # Chờ một chút rồi kiểm tra balance mới
                    self.log(f"{Fore.CYAN}⏳ Waiting for transaction confirmation...")
                    await asyncio.sleep(self.config.get('balance_check_delay', 30))
                    
                    balance_after = await self.check_balance(address, faucet_config)
                    received = balance_after - balance_before
                    
                    if received > 0:
                        self.log(f"{Fore.GREEN}💎 Received: {received:.6f} ETH")
                        self.log(f"{Fore.GREEN}💰 New balance: {balance_after:.6f} ETH")
                    else:
                        self.log(f"{Fore.YELLOW}⚠ Balance unchanged, transaction may be pending")
                    
                    return True
                else:
                    if attempt < max_retries - 1:
                        continue
                    return False
                        
            except Exception as e:
                self.log(f"{Fore.RED}✗ Unexpected error: {str(e)}")
                if attempt < max_retries - 1:
                    continue
                return False
        
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
        print("-" * 70)
        
        for i, (key, faucet) in enumerate(self.faucets.items(), 1):
            status_icon = "🟢" if key == "simulator" else "🟡"
            type_icon = "🔧" if faucet.get('type') == 'api' else "🌐"
            
            print(f"{Fore.WHITE}{i}. {status_icon} {faucet['name']}")
            print(f"   {type_icon} Type: {faucet.get('type', 'web_form').title()}")
            print(f"   💰 Amount: {faucet.get('amount', 'Unknown')}")
            print(f"   ⏰ Cooldown: {faucet.get('cooldown', 'Unknown')}")
            
            if key == "simulator":
                print(f"   {Fore.GREEN}✅ Ready to test (local simulator){Style.RESET_ALL}")
            else:
                print(f"   {Fore.YELLOW}⚠️  May require manual interaction{Style.RESET_ALL}")
            print()
        
        print(f"{Fore.CYAN}💡 Recommendation: Start with option 1 (Simulator) for testing")
        
        while True:
            try:
                choice = int(input(f"\n{Fore.CYAN}Select faucet (1-{len(self.faucets)}): "))
                if 1 <= choice <= len(self.faucets):
                    selected_key = list(self.faucets.keys())[choice - 1]
                    selected_faucet = self.faucets[selected_key]
                    
                    if selected_key != "simulator":
                        print(f"\n{Fore.YELLOW}⚠️  Warning: {selected_faucet['name']} may not work with automated requests")
                        print(f"{Fore.YELLOW}   Most real faucets require manual captcha solving via web interface")
                        confirm = input(f"{Fore.CYAN}Continue anyway? (y/N): ").strip().lower()
                        if confirm != 'y':
                            continue
                    
                    return selected_faucet
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
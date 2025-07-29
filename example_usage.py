#!/usr/bin/env python3
"""
Example usage of ETH Faucet Bot
Demonstrates how to use the bot programmatically
"""

import asyncio
from eth_faucet_bot import EthFaucetBot

async def run_single_claim_example():
    """
    Example: Chạy bot để claim 1 lần cho tất cả accounts
    """
    print("🚀 Starting single claim example...")
    
    bot = EthFaucetBot()
    
    # Load cấu hình
    bot.load_config()
    
    # Load accounts
    if not bot.load_accounts():
        print("❌ No accounts found")
        return
    
    # Load 2captcha key
    if not bot.load_2captcha_key():
        print("❌ No 2captcha key found")
        return
    
    # Chọn faucet (Sepolia)
    selected_faucet = bot.faucets["sepolia"]
    print(f"✅ Selected faucet: {selected_faucet['name']}")
    
    # Claim cho tất cả accounts
    successful_claims = 0
    
    for i, account in enumerate(bot.accounts, 1):
        print(f"\n📍 Processing account {i}/{len(bot.accounts)}")
        
        success = await bot.process_account(account, selected_faucet)
        
        if success:
            successful_claims += 1
            print(f"✅ Account {i} claimed successfully")
        else:
            print(f"❌ Account {i} failed")
        
        # Delay giữa các accounts
        if i < len(bot.accounts):
            print("⏳ Waiting 15s before next account...")
            await asyncio.sleep(15)
    
    print(f"\n🎉 Completed! Successful claims: {successful_claims}/{len(bot.accounts)}")

async def check_balances_example():
    """
    Example: Chỉ kiểm tra balance của tất cả accounts
    """
    print("💰 Checking balances for all accounts...")
    
    bot = EthFaucetBot()
    
    if not bot.load_accounts():
        print("❌ No accounts found")
        return
    
    faucet_config = bot.faucets["sepolia"]
    
    print(f"\n📊 Balance report for {faucet_config['name']}:")
    print("-" * 50)
    
    total_balance = 0
    
    for i, account in enumerate(bot.accounts, 1):
        address = account['address']
        masked_address = bot.mask_address(address)
        
        balance = await bot.check_balance(address, faucet_config)
        total_balance += balance
        
        print(f"{i:2d}. {masked_address}: {balance:.6f} ETH")
    
    print("-" * 50)
    print(f"💎 Total balance: {total_balance:.6f} ETH")
    print(f"📈 Average per account: {total_balance/len(bot.accounts):.6f} ETH")

async def custom_config_example():
    """
    Example: Sử dụng cấu hình tùy chỉnh
    """
    print("⚙️ Custom configuration example...")
    
    bot = EthFaucetBot()
    
    # Override cấu hình mặc định
    bot.config = {
        "claim_interval": 1800,  # 30 phút thay vì 1 giờ
        "max_retries": 5,        # Retry nhiều hơn
        "timeout": 45,           # Timeout lâu hơn
        "delay_between_accounts": {
            "min": 5,
            "max": 15
        }
    }
    
    print(f"✅ Custom config loaded:")
    print(f"   - Claim interval: {bot.config['claim_interval']}s")
    print(f"   - Max retries: {bot.config['max_retries']}")
    print(f"   - Timeout: {bot.config['timeout']}s")
    print(f"   - Account delay: {bot.config['delay_between_accounts']['min']}-{bot.config['delay_between_accounts']['max']}s")

if __name__ == "__main__":
    print("🤖 ETH Faucet Bot - Usage Examples")
    print("=" * 50)
    
    # Chọn example để chạy
    examples = {
        "1": ("Single claim for all accounts", run_single_claim_example),
        "2": ("Check balances only", check_balances_example),
        "3": ("Custom configuration demo", custom_config_example)
    }
    
    print("\nAvailable examples:")
    for key, (description, _) in examples.items():
        print(f"{key}. {description}")
    
    choice = input(f"\nSelect example (1-{len(examples)}): ").strip()
    
    if choice in examples:
        description, example_func = examples[choice]
        print(f"\n🚀 Running: {description}")
        print("=" * 50)
        
        try:
            asyncio.run(example_func())
        except KeyboardInterrupt:
            print(f"\n👋 Example stopped by user")
        except Exception as e:
            print(f"\n💥 Error: {e}")
    else:
        print("❌ Invalid choice")
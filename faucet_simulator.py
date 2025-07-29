#!/usr/bin/env python3
"""
Faucet Simulator Server
Simulates a working ETH testnet faucet for testing purposes
"""

from aiohttp import web, ClientSession
import json
import random
import asyncio
from datetime import datetime
import hashlib

class FaucetSimulator:
    def __init__(self):
        self.claims_history = {}  # Track claims per address
        self.rate_limit_duration = 3600  # 1 hour in seconds
        
    async def handle_claim(self, request):
        """Handle faucet claim requests"""
        try:
            # Parse request data
            if request.content_type == 'application/json':
                data = await request.json()
            else:
                data = await request.post()
            
            address = data.get('address', '').strip()
            captcha = data.get('captcha', '').strip()
            
            # Validate address format
            if not address or not address.startswith('0x') or len(address) != 42:
                return web.json_response({
                    'success': False,
                    'message': 'Invalid Ethereum address format'
                }, status=400)
            
            # Validate captcha (simulate captcha check)
            if not captcha or len(captcha) < 10:
                return web.json_response({
                    'success': False,
                    'message': 'Invalid captcha token'
                }, status=400)
            
            # Check rate limiting
            current_time = datetime.now().timestamp()
            last_claim = self.claims_history.get(address, 0)
            
            if current_time - last_claim < self.rate_limit_duration:
                remaining_time = int(self.rate_limit_duration - (current_time - last_claim))
                return web.json_response({
                    'success': False,
                    'message': f'Rate limited. Try again in {remaining_time} seconds',
                    'error': 'RATE_LIMITED'
                }, status=429)
            
            # Simulate some random failures (10% chance)
            if random.random() < 0.1:
                error_messages = [
                    'Faucet temporarily unavailable',
                    'Insufficient funds in faucet',
                    'Network congestion, try again later'
                ]
                return web.json_response({
                    'success': False,
                    'message': random.choice(error_messages)
                }, status=503)
            
            # Simulate processing delay
            await asyncio.sleep(random.uniform(1, 3))
            
            # Generate fake transaction hash
            tx_data = f"{address}{current_time}{captcha}"
            tx_hash = "0x" + hashlib.sha256(tx_data.encode()).hexdigest()
            
            # Record successful claim
            self.claims_history[address] = current_time
            
            # Return success response
            amount = random.uniform(0.05, 0.5)  # Random amount between 0.05-0.5 ETH
            
            return web.json_response({
                'success': True,
                'message': 'Claim successful',
                'txHash': tx_hash,
                'amount': f"{amount:.6f}",
                'address': address,
                'timestamp': int(current_time)
            })
            
        except Exception as e:
            return web.json_response({
                'success': False,
                'message': f'Internal server error: {str(e)}'
            }, status=500)
    
    async def handle_status(self, request):
        """Handle status requests"""
        return web.json_response({
            'status': 'online',
            'faucet_name': 'Test Faucet Simulator',
            'rate_limit': f'{self.rate_limit_duration} seconds',
            'amount_range': '0.05 - 0.5 ETH',
            'total_claims': len(self.claims_history),
            'uptime': 'Always up (simulator)'
        })
    
    async def handle_balance(self, request):
        """Handle balance requests"""
        return web.json_response({
            'balance': '1000.0 ETH',
            'status': 'healthy'
        })

async def create_app():
    """Create the web application"""
    simulator = FaucetSimulator()
    
    app = web.Application()
    
    # Add CORS headers
    async def cors_handler(request, handler):
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    app.middlewares.append(cors_handler)
    
    # Routes
    app.router.add_post('/api/claim', simulator.handle_claim)
    app.router.add_get('/api/status', simulator.handle_status)
    app.router.add_get('/api/balance', simulator.handle_balance)
    
    # Handle OPTIONS requests for CORS
    async def handle_options(request):
        return web.Response(status=200)
    
    app.router.add_route('OPTIONS', '/{path:.*}', handle_options)
    
    return app

async def main():
    """Start the faucet simulator server"""
    app = await create_app()
    
    print("🚀 Starting Faucet Simulator Server...")
    print("📍 Server will run on: http://localhost:8080")
    print("🔗 API Endpoints:")
    print("   • POST /api/claim - Claim testnet ETH")
    print("   • GET /api/status - Check faucet status") 
    print("   • GET /api/balance - Check faucet balance")
    print("\n💡 Use this URL in your bot: http://localhost:8080/api/claim")
    print("⚠️  This is a simulator - no real ETH will be sent!")
    print("\n🛑 Press Ctrl+C to stop the server\n")
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Faucet Simulator...")
        await runner.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
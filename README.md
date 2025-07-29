# ETH Testnet Faucet Bot

🤖 **Auto ETH Testnet Faucet Bot with 2Captcha Integration**

Một bot tự động để claim ETH từ các faucet testnet phổ biến với tích hợp dịch vụ giải captcha 2captcha.

## ✨ Tính năng chính

- 🔄 **Tự động claim ETH** từ nhiều faucet testnet
- 🧩 **Tích hợp 2Captcha** để giải reCAPTCHA tự động
- 💼 **Hỗ trợ multi-account** - quản lý nhiều ví cùng lúc
- ⚡ **Kiểm tra balance** trước và sau khi claim
- 🔁 **Chạy liên tục** với chu kỳ tùy chỉnh
- 📊 **Báo cáo chi tiết** về kết quả claim
- 🎯 **Hỗ trợ nhiều testnet**: Sepolia, Goerli
- ⏰ **Delay ngẫu nhiên** giữa các account để tránh detect

## 🛠 Yêu cầu hệ thống

- **Python 3.8+**
- **2Captcha API Key** (có thể mua tại [2captcha.com](https://2captcha.com))
- **Private keys** của các ví ETH cần claim

## 📦 Cài đặt

### 1. Clone repository

```bash
git clone <repository-url>
cd eth-faucet-bot
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình

#### a) Thêm private keys (`accounts.txt`)

```
# Add your private keys here, one per line
0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890
```

#### b) Thêm 2Captcha API key (`2captcha_key.txt`)

```
your_2captcha_api_key_here
```

> 💡 **Lấy API key**: Đăng ký tại [2captcha.com](https://2captcha.com/enterpage) và copy API key từ dashboard

#### c) Cấu hình bot (tùy chọn) (`config.json`)

```json
{
    "claim_interval": 3600,
    "max_retries": 3,
    "timeout": 30,
    "selected_faucet": "sepolia",
    "delay_between_accounts": {
        "min": 10,
        "max": 30
    }
}
```

## 🚀 Cách sử dụng

### Chạy bot

```bash
python eth_faucet_bot.py
```

### Chọn faucet

Khi chạy, bot sẽ hiển thị menu để chọn faucet:

```
Available Faucets:
1. Sepolia Testnet
2. Goerli Testnet

Select faucet (1-2): 1
```

### Quá trình hoạt động

1. **Khởi tạo**: Bot load cấu hình và kiểm tra accounts
2. **Chọn faucet**: User chọn testnet muốn claim
3. **Claim cycle**: Bot xử lý từng account:
   - Kiểm tra balance hiện tại
   - Giải captcha qua 2captcha
   - Gửi request claim
   - Kiểm tra balance sau claim
   - Hiển thị kết quả
4. **Chờ chu kỳ tiếp theo**: Bot đợi theo `claim_interval` rồi lặp lại

## 📊 Các testnet được hỗ trợ

| Testnet | Chain ID | RPC URL | Faucet Amount |
|---------|----------|---------|---------------|
| **Sepolia** | 11155111 | ethereum-sepolia-rpc.publicnode.com | ~0.5 ETH |
| **Goerli** | 5 | ethereum-goerli-rpc.publicnode.com | ~0.1 ETH |

## ⚙️ Cấu hình chi tiết

### `config.json` options:

```json
{
    "claim_interval": 3600,          // Thời gian chờ giữa các chu kỳ (giây)
    "max_retries": 3,                // Số lần retry khi thất bại
    "timeout": 30,                   // Timeout cho HTTP requests
    "delay_between_accounts": {      // Delay giữa các account
        "min": 10,
        "max": 30
    },
    "retry_delay": 60,               // Delay khi retry
    "balance_check_delay": 30        // Delay khi check balance sau claim
}
```

## 📝 Log và monitoring

Bot hiển thị log chi tiết:

```
[2024-01-20 10:30:15] ✓ Loaded 5 valid accounts
[2024-01-20 10:30:16] ✓ 2Captcha API key loaded
[2024-01-20 10:30:17] ✓ Selected: Sepolia Testnet
[2024-01-20 10:30:18] 🔄 Processing account: 0x1234...abcd
[2024-01-20 10:30:19] 💰 Current balance: 0.125000 ETH
[2024-01-20 10:30:20] ⏳ Solving captcha... ID: 12345678
[2024-01-20 10:30:45] ✓ Captcha solved successfully  
[2024-01-20 10:30:46] ✓ Claim successful!
[2024-01-20 10:30:47] 🔗 Transaction: https://sepolia.etherscan.io/tx/0x...
[2024-01-20 10:31:17] 💎 Received: 0.500000 ETH
[2024-01-20 10:31:17] 💰 New balance: 0.625000 ETH
```

## 🛡️ Bảo mật

- ✅ Private keys được lưu local, không gửi lên server
- ✅ Address được mask trong log để bảo mật
- ✅ Delay ngẫu nhiên để tránh pattern detection
- ✅ Error handling để tránh crash

## ⚠️ Lưu ý quan trọng

1. **Chi phí 2Captcha**: Mỗi captcha giải thành công tốn ~$0.001-0.003
2. **Rate limit**: Các faucet có giới hạn thời gian (thường 24h/lần)
3. **Testnet only**: Bot chỉ hoạt động trên testnet, không phải mainnet
4. **Backup private keys**: Luôn backup private keys ở nơi an toàn

## 🔧 Troubleshooting

### Lỗi thường gặp:

**"Invalid private key"**
```
Kiểm tra format private key trong accounts.txt
Đảm bảo private key bắt đầu bằng 0x và có 64 ký tự hex
```

**"2captcha API key required"**
```
Thêm API key hợp lệ vào file 2captcha_key.txt
Kiểm tra balance 2captcha account
```

**"Claim failed: Rate limited"**
```
Faucet có cooldown, chờ đủ thời gian rồi thử lại
Thường là 24h cho mỗi address
```

**"Captcha solving timeout"**
```
2captcha server quá tải, thử lại sau
Kiểm tra balance 2captcha
```

## 📈 Tips tối ưu

1. **Sử dụng nhiều ví**: Tăng tổng amount claim được
2. **Chạy vào giờ thấp điểm**: Ít competition hơn
3. **Monitor balance 2captcha**: Đảm bảo đủ credit
4. **Backup cấu hình**: Lưu accounts.txt và config.json

## 🤝 Đóng góp

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## ⚡ Support

Nếu gặp vấn đề hoặc có câu hỏi, vui lòng tạo issue trên GitHub.

---

**⚠️ Disclaimer**: Tool này chỉ dành cho mục đích educational và testing. Sử dụng có trách nhiệm và tuân thủ ToS của các faucet.
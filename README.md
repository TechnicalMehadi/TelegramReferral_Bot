# 📢 Telegram Referral Bot - SHIB Coin Reward System

## 🚀 Quick Setup Guide (Copy-Paste Friendly)

### 🔑 Basic Configuration (Edit These First)
```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Get from @BotFather
ADMIN_ID = YOUR_ADMIN_ID_HERE      # Your personal Telegram ID
ADMIN_CHAT_ID = YOUR_GROUP_ID      # Payment processing group ID
```

### 🐕 Coin Settings (Customize Your Coin)
```python
COIN_NAME = "Shiba Inu Coin"       # Change coin name (e.g., "Doge Coin")
COIN_SYMBOL = "SHIB"               # Change ticker symbol (e.g., "DOGE")
```

### 💰 Reward System (Adjust Numbers)
```python
JOIN_REWARD = 20                   # Coins for joining channels
REFERRAL_REWARD = 10               # Coins per successful referral
WITHDRAWAL_THRESHOLD = 30          # Minimum coins to withdraw
```

### 📢 Promotion Channels (Add Your Channels)
```python
CHANNELS = [
    ("@YourChannel1", "🌟 Official Channel"),
    ("@YourChannel2", "📢 News Channel"),
    # Add more as needed - format: ("@username", "Display Name")
]
```

### 🌐 Withdrawal Networks (Edit If Needed)
```python
NETWORKS = [
    "TRC20",    # Tron network
    "ERC20",    # Ethereum
    "BEP20",    # Binance Smart Chain
    "ARB"       # Arbitrum
    # Add/remove networks as required
]
```

## 🖼️ Customize Welcome Image
1. Place your `welcome.png` in the bot folder
2. Recommended size: 800x400 pixels
3. Or delete the file to use text-only welcome

## ⚙️ Advanced Settings (Optional)
```python
# Database file name (change if needed)
USER_DB_FILE = "user_data.pkl"  

# Auto-backup settings (enable if needed)
AUTO_BACKUP = True  
BACKUP_INTERVAL = 3600  # Seconds (1 hour)
```

## 🏃‍♂️ How to Run
1. Install requirements:
```bash
pip install python-telegram-bot pickle5
```

2. Save all configurations above in `bot.py`

3. Start the bot:
```bash
python bot.py
```

## 📝 Important Notes for Technical Mehadi Users
1. Replace all placeholder text (YOUR_XXX_HERE) with your actual details
2. For YouTube channel promotion:
   - Set `COIN_NAME = "Technical Mehadi Token"`
   - Set `COIN_SYMBOL = "TMT"`
3. Add your YouTube channel in the CHANNELS list
4. Recommended welcome message:
```python
WELCOME_MSG = (
    "👋 Welcome to Technical Mehadi Reward Bot!\n\n"
    "🎥 Watch our YouTube videos\n"
    "💰 Earn TMT tokens for joining and referring\n"
    "💸 Withdraw to your wallet anytime!"
)
```

## 🆘 Support
For any issues, contact:  
📧 Email: mdmehadihasan0011@gmail.com  
📱 Telegram: @shuvoofficial  
🎥 YouTube: [Technical Mehadi](https://youtube.com/@technicalmehadi)  

---

**Pro Tip:** After setup, test all bot commands as admin first before public launch! 🚀

[🔄 Click to Copy Full Config] [🖥️ Test Bot Now] [📺 Watch Tutorial]  

---

<div align="center">
    <em>❤️ Made for Technical Mehadi YouTube Channel ❤️</em>
</div>

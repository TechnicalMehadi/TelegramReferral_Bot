import logging
import pickle
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes,
    MessageHandler, filters
)
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Tuple
import html

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== CONFIGURATION =====
BOT_TOKEN = "7379455627:AAEBC5I-U8-V8cX5ZHDGjjM7CH-QWUGTiBI"
ADMIN_ID = 5890970827  # Can only broadcast and view stats
ADMIN_CHAT_ID = 7709642612 # Payment admins (can approve/reject withdrawals)
USER_DB_FILE = "user_data.pkl"
WELCOME_PHOTO = "welcome.png"  # Make sure this file exists

# Coin configuration - change these to update all references
COIN_NAME = "Shiba Inu Coin"  # This will be used throughout the bot
COIN_SYMBOL = "SHIB"  # For shorthand references

# Channel list - replace with your actual channels
CHANNELS = [
    ("@onlineincome_max", "📢 Channel 1"),
    ("@onlineincome_max", "📢 Channel 2"),
    ("@onlineincome_max", "📢 Channel 3"),
    ("@onlineincome_max", "📢 Channel 4"),
    ("@onlineincome_max", "📢 Channel 5"),
    ("@onlineincome_max", "📢 Channel 6"),
    ("@onlineincome_max", "📢 Channel 7"),
    ("@onlineincome_max", "📢 Channel 8")
]

# Reward system
JOIN_REWARD = 20
REFERRAL_REWARD = 10
WITHDRAWAL_THRESHOLD = 30

# Network options
NETWORKS = [
    "TRC20",
    "ERC20",
    "BEP20",
    "ARB"
]

def load_user_data() -> Dict[str, Any]:
    try:
        with open(USER_DB_FILE, 'rb') as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError):
        return {'users': {}, 'referral_map': {}, 'stats': {
            'total_coins_distributed': 0,
            'direct_joins': 0,
            'referral_joins': 0,
            'total_withdrawals': 0,
            'pending_withdrawals': 0
        }}

def save_user_data(data: Dict[str, Any]) -> None:
    with open(USER_DB_FILE, 'wb') as f:
        pickle.dump(data, f)

async def check_channels_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        for channel in CHANNELS:
            member = await context.bot.get_chat_member(chat_id=channel[0], user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                logger.info(f"User {user_id} not member of {channel[0]} (status: {member.status})")
                return False
        return True
    except Exception as e:
        logger.error(f"Channel check error for {channel[0]}: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    data = load_user_data()
    
    # Referral processing
    ref_id = None
    if context.args and context.args[0].isdigit():
        ref_id = int(context.args[0])
        if ref_id == user_id:
            ref_id = None
    
    new_user = False
    if user_id not in data['users']:
        data['users'][user_id] = {
            'name': user.full_name,
            'username': user.username,
            'coins': 0,
            'referrals': [],
            'joined': False,
            'join_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_active': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'join_type': 'direct',
            'pending_withdrawal': 0
        }
        new_user = True
        
        if ref_id and ref_id in data['users']:
            data['users'][user_id]['join_type'] = 'referral'
            data['referral_map'][user_id] = ref_id
            data['stats']['referral_joins'] += 1
            save_user_data(data)
            logger.info(f"New referral: {user_id} referred by {ref_id}")
        else:
            data['stats']['direct_joins'] += 1
    
    # Update last active time
    data['users'][user_id]['last_active'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_user_data(data)
    
    # Create channel buttons
    buttons = []
    for i in range(0, len(CHANNELS), 2):
        row = [
            InlineKeyboardButton(CHANNELS[i][1], url=f"https://t.me/{CHANNELS[i][0][1:]}"),
            InlineKeyboardButton(CHANNELS[i+1][1], url=f"https://t.me/{CHANNELS[i+1][0][1:]}")
        ] if i+1 < len(CHANNELS) else [
            InlineKeyboardButton(CHANNELS[i][1], url=f"https://t.me/{CHANNELS[i][0][1:]}")
        ]
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton("✅ Verify Join", callback_data="verify_join")])
    
    try:
        if os.path.exists(WELCOME_PHOTO):
            with open(WELCOME_PHOTO, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=f"👋 Hello {user.full_name}, Welcome to the {COIN_NAME} Bot!\n\n"
                            "📌 Join all channels below\n"
                            f"💰 Join Bonus: {JOIN_REWARD} {COIN_NAME}\n"
                            f"👥 Referral Bonus: {REFERRAL_REWARD} {COIN_NAME}",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
        else:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"👋 Hello {user.full_name}, Welcome to the {COIN_NAME} Bot!\n\n"
                     "📌 Join all channels below\n"
                     f"💰 Join Bonus: {JOIN_REWARD} {COIN_NAME}\n"
                     f"👥 Referral Bonus: {REFERRAL_REWARD} {COIN_NAME}",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        
        if new_user:
            logger.info(f"New user: {user.full_name} (ID: {user_id})")
    except Exception as e:
        logger.error(f"Welcome error: {e}")

async def verify_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    data = load_user_data()
    if user_id not in data['users']:
        await context.bot.send_message(user_id, "⚠️ Please use /start command first!")
        return
    
    if data['users'][user_id]['joined']:
        await show_main_menu(user_id, context, "⚠️ You've already joined!\n\n")
        return
    
    # Show checking message
    checking_msg = await context.bot.send_message(user_id, "🔍 Checking your channel memberships...")
    
    if await check_channels_membership(user_id, context):
        data['users'][user_id]['coins'] += JOIN_REWARD
        data['users'][user_id]['joined'] = True
        data['users'][user_id]['last_active'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data['stats']['total_coins_distributed'] += JOIN_REWARD
        
        # Referral reward
        if user_id in data['referral_map']:
            referrer_id = data['referral_map'][user_id]
            if referrer_id in data['users']:
                data['users'][referrer_id]['coins'] += REFERRAL_REWARD
                data['users'][referrer_id]['referrals'].append(user_id)
                data['stats']['total_coins_distributed'] += REFERRAL_REWARD
                try:
                    await context.bot.send_message(
                        chat_id=referrer_id,
                        text=f"🎉 New referral! {query.from_user.full_name} joined!\n"
                             f"➕ You got {REFERRAL_REWARD} {COIN_NAME}!"
                    )
                    logger.info(f"Referral reward: {referrer_id} got {REFERRAL_REWARD} {COIN_NAME}")
                except Exception as e:
                    logger.error(f"Referral message failed to {referrer_id}: {e}")
        
        save_user_data(data)
        await checking_msg.delete()
        logger.info(f"Join verified: {user_id} got {JOIN_REWARD} {COIN_NAME}")
        await show_main_menu(user_id, context, f"✅ Verification complete! You got {JOIN_REWARD} {COIN_NAME}!\n\n")
    else:
        await checking_msg.delete()
        # Create channel buttons again
        buttons = []
        for i in range(0, len(CHANNELS), 2):
            row = [
                InlineKeyboardButton(CHANNELS[i][1], url=f"https://t.me/{CHANNELS[i][0][1:]}"),
                InlineKeyboardButton(CHANNELS[i+1][1], url=f"https://t.me/{CHANNELS[i+1][0][1:]}")
            ] if i+1 < len(CHANNELS) else [
                InlineKeyboardButton(CHANNELS[i][1], url=f"https://t.me/{CHANNELS[i][0][1:]}")
            ]
            buttons.append(row)
        
        buttons.append([InlineKeyboardButton("✅ Verify Join", callback_data="verify_join")])
        
        await context.bot.send_message(
            user_id,
            "❌ You haven't joined all channels! Please join all these channels and click Verify Join again:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

async def show_main_menu(user_id: int, context: ContextTypes.DEFAULT_TYPE, prefix_text: str = ""):
    data = load_user_data()
    if user_id not in data['users']:
        await context.bot.send_message(user_id, "⚠️ Please use /start command first!")
        return
    
    user = data['users'][user_id]
    
    text = (
        f"{prefix_text}"
        f"👤 User: {user['name']}\n"
        f"🆔 Username: @{user.get('username', 'N/A')}\n"
        f"💰 {COIN_NAME}: {user['coins']}\n"
        f"👥 Referrals: {len(user['referrals'])} people\n\n"
        f"💡 Minimum withdrawal: {WITHDRAWAL_THRESHOLD} {COIN_NAME}"
    )
    
    buttons = [
        [InlineKeyboardButton("🔢 Check Balance", callback_data="check_balance")],
        [InlineKeyboardButton("🔗 Referral Link", callback_data="referral_link")],
        [InlineKeyboardButton("💵 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
    ]
    
    if user_id == ADMIN_ID:
        buttons.append([InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")])
        buttons.append([InlineKeyboardButton("📊 Stats", callback_data="admin_stats")])
    
    await context.bot.send_message(
        chat_id=user_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def check_balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    data = load_user_data()
    
    if user_id not in data['users']:
        await update.message.reply_text("⚠️ Please use /start command first!")
        return
    
    user = data['users'][user_id]
    await update.message.reply_text(
        f"💰 Your current balance:\n"
        f"• {COIN_NAME}: {user['coins']}\n"
        f"• Referrals: {len(user['referrals'])} people\n"
        f"• Can withdraw: {'Yes' if user['coins'] >= WITHDRAWAL_THRESHOLD else 'No'}\n"
        f"• Pending withdrawal: {user['pending_withdrawal']} {COIN_NAME}"
    )

async def referral_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    data = load_user_data()
    
    if user_id not in data['users']:
        await update.message.reply_text("⚠️ Please use /start command first!")
        return
    
    bot_username = (await context.bot.getMe()).username
    referral_url = f"https://t.me/{bot_username}?start={user_id}"
    
    await update.message.reply_text(
        f"📢 Your referral link:\n{referral_url}\n\n"
        f"Get {REFERRAL_REWARD} {COIN_NAME} for each referral!\n"
        f"Total referrals: {len(data['users'][user_id]['referrals'])} people"
    )

async def withdraw_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    data = load_user_data()
    
    if user_id not in data['users']:
        await update.message.reply_text("⚠️ Please use /start command first!")
        return
    
    if data['users'][user_id]['coins'] < WITHDRAWAL_THRESHOLD:
        await update.message.reply_text(
            f"❌ Minimum {WITHDRAWAL_THRESHOLD} {COIN_NAME} required for withdrawal!\n"
            f"Your current balance: {data['users'][user_id]['coins']} {COIN_NAME}"
        )
    else:
        # Create network selection buttons
        buttons = []
        for network in NETWORKS:
            buttons.append([InlineKeyboardButton(network, callback_data=f"network_{network}")])
        
        buttons.append([InlineKeyboardButton("🔙 Cancel", callback_data="cancel_withdrawal")])
        
        await update.message.reply_text(
            "🌐 Please select your network:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        context.user_data['withdrawal_stage'] = 'network'

async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ This feature is for admin only!")
        return
    
    data = load_user_data()
    total_users = len(data['users'])
    active_users = sum(1 for u in data['users'].values() if u['joined'])
    total_coins = sum(u['coins'] for u in data['users'].values())
    
    stats_text = (
        f"📊 Bot Statistics:\n\n"
        f"👥 Total users: {total_users}\n"
        f"🟢 Active users: {active_users}\n"
        f"💰 Total {COIN_NAME}: {total_coins}\n"
        f"🔄 Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"⏳ Pending withdrawals: {data['stats']['pending_withdrawals']}"
    )
    
    await update.message.reply_text(stats_text)

async def admin_broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ This feature is for admin only!")
        return
    
    context.user_data['waiting_for_broadcast'] = True
    await update.message.reply_text(
        "📢 Send broadcast message (text, photo, video or document):\n"
        "or type /cancel to abort"
    )

async def check_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    data = load_user_data()
    if user_id not in data['users']:
        await context.bot.send_message(user_id, "⚠️ Please use /start command first!")
        return
    
    user = data['users'][user_id]
    await context.bot.send_message(
        user_id,
        f"💰 Your current balance:\n"
        f"• {COIN_NAME}: {user['coins']}\n"
        f"• Referrals: {len(user['referrals'])} people\n"
        f"• Can withdraw: {'Yes' if user['coins'] >= WITHDRAWAL_THRESHOLD else 'No'}\n"
        f"• Pending withdrawal: {user['pending_withdrawal']} {COIN_NAME}\n\n"
        f"🔄 Last active: {user.get('last_active', 'N/A')}"
    )

async def referral_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    data = load_user_data()
    if user_id not in data['users']:
        await context.bot.send_message(user_id, "⚠️ Please use /start command first!")
        return
    
    bot_username = (await context.bot.getMe()).username
    referral_url = f"https://t.me/{bot_username}?start={user_id}"
    
    await context.bot.send_message(
        chat_id=user_id,
        text=f"📢 Your referral link:\n{referral_url}\n\n"
             f"Get {REFERRAL_REWARD} {COIN_NAME} for each referral!\n"
             f"Total referrals: {len(data['users'][user_id]['referrals'])} people\n\n"
             "👉 Share this link to earn more {COIN_NAME}!"
    )

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    data = load_user_data()
    if user_id not in data['users']:
        await context.bot.send_message(user_id, "⚠️ Please use /start command first!")
        return
    
    if data['users'][user_id]['coins'] < WITHDRAWAL_THRESHOLD:
        await context.bot.send_message(
            user_id,
            f"❌ Minimum {WITHDRAWAL_THRESHOLD} {COIN_NAME} required for withdrawal!\n"
            f"Your current balance: {data['users'][user_id]['coins']} {COIN_NAME}\n\n"
            f"👉 Share your referral link to earn more {COIN_NAME}!"
        )
    else:
        # Create network selection buttons
        buttons = []
        for network in NETWORKS:
            buttons.append([InlineKeyboardButton(network, callback_data=f"network_{network}")])
        
        buttons.append([InlineKeyboardButton("🔙 Cancel", callback_data="cancel_withdrawal")])
        
        await context.bot.send_message(
            user_id,
            "🌐 Please select your network:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        context.user_data['withdrawal_stage'] = 'network'

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📌 Help:\n\n"
        "1. Join all channels and click 'Verify Join'\n"
        f"2. Get {REFERRAL_REWARD} {COIN_NAME} for each referral\n"
        f"3. Minimum withdrawal: {WITHDRAWAL_THRESHOLD} {COIN_NAME}\n"
        "4. For withdrawal:\n"
        "   - Check your balance\n"
        "   - Select withdraw option\n"
        "   - Select network\n"
        "   - Send your wallet address\n"
        "5. Contact admin for any issues\n\n"
        "📌 Available commands:\n"
        "/start - Start the bot\n"
        "/balance - Check your balance\n"
        "/referral - Get your referral link\n"
        "/withdraw - Withdraw your coins\n"
        "/help - Show this help message"
    )
    
    if update.message:
        await update.message.reply_text(text)
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text)

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if user_id != ADMIN_ID:
        await context.bot.send_message(user_id, "❌ This feature is for admin only!")
        return
    
    context.user_data['waiting_for_broadcast'] = True
    await context.bot.send_message(
        user_id,
        "📢 Send broadcast message (text, photo, video or document):\n"
        "or type /cancel to abort"
    )

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if user_id != ADMIN_ID:
        await context.bot.send_message(user_id, "❌ This feature is for admin only!")
        return
    
    data = load_user_data()
    total_users = len(data['users'])
    active_users = sum(1 for u in data['users'].values() if u['joined'])
    total_coins = sum(u['coins'] for u in data['users'].values())
    today_joins = sum(1 for u in data['users'].values() if u.get('join_date', '').startswith(datetime.now().strftime('%Y-%m-%d')))
    active_today = sum(1 for u in data['users'].values() if u.get('last_active', '').startswith(datetime.now().strftime('%Y-%m-%d')))
    
    stats = data['stats']
    stats_text = (
        f"📊 Bot Statistics:\n\n"
        f"👥 Total users: {total_users}\n"
        f"🟢 Active users: {active_users}\n"
        f"💰 Total {COIN_NAME}: {total_coins}\n"
        f"📅 Today's joins: {today_joins}\n"
        f"🔄 Active today: {active_today}\n\n"
        f"📈 Detailed Stats:\n"
        f"• Direct joins: {stats['direct_joins']}\n"
        f"• Referral joins: {stats['referral_joins']}\n"
        f"• Total {COIN_NAME} distributed: {stats['total_coins_distributed']}\n"
        f"• Total withdrawals: {stats['total_withdrawals']}\n"
        f"• Pending withdrawals: {stats['pending_withdrawals']}"
    )
    
    await context.bot.send_message(user_id, stats_text)

async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)

async def handle_network_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not query.data.startswith("network_"):
        return
    
    user_id = query.from_user.id
    data = load_user_data()
    
    if user_id not in data['users']:
        await query.edit_message_text("⚠️ Please use /start command first!")
        return
    
    network = query.data[8:]  # Remove "network_" prefix
    context.user_data['selected_network'] = network
    
    await query.edit_message_text(
        f"🌐 Selected network: {network}\n\n"
        "📝 Please send your wallet address (no other text):"
    )
    context.user_data['withdrawal_stage'] = 'wallet_address'

async def handle_withdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    data = load_user_data()
    
    if user_id not in data['users']:
        return
    
    if 'withdrawal_stage' not in context.user_data:
        return
    
    if context.user_data['withdrawal_stage'] == 'wallet_address':
        # Store wallet address and process withdrawal
        wallet_address = update.message.text.strip()
        network = context.user_data['selected_network']
        amount = data['users'][user_id]['coins']
        
        # Deduct coins immediately
        data['users'][user_id]['coins'] = 0
        data['users'][user_id]['pending_withdrawal'] += amount
        data['stats']['pending_withdrawals'] += amount
        save_user_data(data)
        
        # Create click-to-copy wallet address text
        wallet_text = f'<code>{html.escape(wallet_address)}</code>'
        
        # Notify payment admin with click-to-copy functionality
        admin_text = (
            f"🚀 New withdrawal request:\n\n"
            f"👤 User: {data['users'][user_id]['name']}\n"
            f"🆔 Telegram ID: {user_id}\n"
            f"📛 Username: @{data['users'][user_id].get('username', 'N/A')}\n"
            f"💰 Amount: {amount} {COIN_NAME}\n"
            f"🌐 Network: {network}\n"
            f"📮 Wallet Address: {wallet_text}\n\n"
            f"🕒 Request time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        keyboard = [
            [InlineKeyboardButton("✅ Approve Payment", callback_data=f"approve_{user_id}_{amount}")],
            [InlineKeyboardButton("❌ Cancel Payment", callback_data=f"reject_{user_id}_{amount}")]
        ]
        
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        
        await update.message.reply_text(
            f"✅ Your withdrawal request has been received!\n"
            f"• Amount: {amount} {COIN_NAME}\n"
            f"• Network: {network}\n"
            f"• Wallet Address: {wallet_address}\n\n"
            "Admin will process your request soon. Your coins have been temporarily deducted."
        )
        logger.info(f"Withdrawal request: {user_id} - {amount} {COIN_NAME}")
        
        # Clean up
        context.user_data.pop('withdrawal_stage', None)
        context.user_data.pop('selected_network', None)

async def cancel_withdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data.pop('withdrawal_stage', None)
    context.user_data.pop('selected_network', None)
    
    await query.edit_message_text("❌ Withdrawal cancelled.")
    await show_main_menu(query.from_user.id, context)

async def handle_payment_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Check if the user is in the payment admin group
    if query.message.chat.id != ADMIN_CHAT_ID:
        await query.edit_message_text("❌ Only payment admins can process payments!")
        return
    
    action, user_id_str, amount_str = query.data.split('_')
    user_id = int(user_id_str)
    amount = int(amount_str)
    
    data = load_user_data()
    
    if user_id not in data['users']:
        await query.edit_message_text("❌ User not found in database!")
        return
    
    if action == 'approve':
        # Remove from pending and mark as completed
        data['users'][user_id]['pending_withdrawal'] -= amount
        data['stats']['pending_withdrawals'] -= amount
        data['stats']['total_withdrawals'] += amount
        save_user_data(data)
        
        # Notify user
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"🎉 Your withdrawal of {amount} {COIN_NAME} has been approved!\n\n"
                     "✅ The payment has been successfully sent to your wallet.\n\n"
                     "Please check your wallet and confirm receipt.\n"
                     "Thank you for using our service!"
            )
        except Exception as e:
            logger.error(f"Failed to notify user {user_id}: {e}")
        
        await query.edit_message_text(
            f"✅ Payment approved and processed!\n"
            f"User: {data['users'][user_id]['name']}\n"
            f"Amount: {amount} {COIN_NAME}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        logger.info(f"Payment approved for {user_id} - {amount} {COIN_NAME}")
    
    elif action == 'reject':
        # Return coins to user's main balance (not pending)
        data['users'][user_id]['coins'] += amount
        data['users'][user_id]['pending_withdrawal'] -= amount
        data['stats']['pending_withdrawals'] -= amount
        save_user_data(data)
        
        # Notify user
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"⚠️ Your withdrawal of {amount} {COIN_NAME} could not be processed.\n\n"
                     "Due to technical issues, we couldn't complete your payment at this time.\n"
                     "Your coins have been returned to your main balance.\n\n"
                     "Please verify your wallet address and network information and try again.\n"
                     "If the problem persists, contact support."
            )
        except Exception as e:
            logger.error(f"Failed to notify user {user_id}: {e}")
        
        await query.edit_message_text(
            f"❌ Payment rejected!\n"
            f"User: {data['users'][user_id]['name']}\n"
            f"Amount: {amount} {COIN_NAME} returned to user\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        logger.info(f"Payment rejected for {user_id} - {amount} {COIN_NAME} returned")

async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID or not context.user_data.get('waiting_for_broadcast'):
        return
    
    if update.message.text == '/cancel':
        context.user_data.pop('waiting_for_broadcast', None)
        await update.message.reply_text("❌ Broadcast cancelled")
        return
    
    data = load_user_data()
    users = list(data['users'].keys())
    total = len(users)
    success = 0
    failed = 0
    
    progress_msg = await context.bot.send_message(
        ADMIN_ID,
        f"📤 Broadcasting started...\n"
        f"Total recipients: {total}\n"
        f"✅ Success: 0\n"
        f"❌ Failed: 0"
    )
    
    start_time = time.time()
    
    for idx, uid in enumerate(users):
        try:
            if update.message.text:
                await context.bot.send_message(chat_id=uid, text=update.message.text)
            elif update.message.photo:
                await context.bot.send_photo(
                    chat_id=uid,
                    photo=update.message.photo[-1].file_id,
                    caption=update.message.caption
                )
            elif update.message.video:
                await context.bot.send_video(
                    chat_id=uid,
                    video=update.message.video.file_id,
                    caption=update.message.caption
                )
            elif update.message.document:
                await context.bot.send_document(
                    chat_id=uid,
                    document=update.message.document.file_id,
                    caption=update.message.caption
                )
            success += 1
        except Exception as e:
            failed += 1
            logger.error(f"Broadcast failed to {uid}: {e}")
        
        # Update every 10 sends
        if idx % 10 == 0 or idx == total - 1:
            try:
                await progress_msg.edit_text(
                    f"📤 Broadcast progress...\n"
                    f"Total recipients: {total}\n"
                    f"✅ Success: {success}\n"
                    f"❌ Failed: {failed}\n"
                    f"⏳ Time: {int(time.time() - start_time)}s"
                )
            except:
                pass
    
    context.user_data.pop('waiting_for_broadcast', None)
    await progress_msg.edit_text(
        f"✅ Broadcast completed!\n"
        f"• Total sent: {total}\n"
        f"• Success: {success}\n"
        f"• Failed: {failed}\n"
        f"⏳ Time taken: {int(time.time() - start_time)}s"
    )
    logger.info(f"Broadcast completed: {success}/{total} successful")

def main():
    # Initialize database
    data = load_user_data()
    save_user_data(data)
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Register handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('balance', check_balance_command))
    app.add_handler(CommandHandler('referral', referral_command))
    app.add_handler(CommandHandler('withdraw', withdraw_command))
    app.add_handler(CommandHandler('stats', admin_stats_command))
    app.add_handler(CommandHandler('broadcast', admin_broadcast_command))
    
    # Callback handlers
    app.add_handler(CallbackQueryHandler(verify_join, pattern="^verify_join$"))
    app.add_handler(CallbackQueryHandler(check_balance, pattern="^check_balance$"))
    app.add_handler(CallbackQueryHandler(referral_link, pattern="^referral_link$"))
    app.add_handler(CallbackQueryHandler(withdraw, pattern="^withdraw$"))
    app.add_handler(CallbackQueryHandler(help_command, pattern="^help$"))
    app.add_handler(CallbackQueryHandler(admin_broadcast, pattern="^admin_broadcast$"))
    app.add_handler(CallbackQueryHandler(admin_stats, pattern="^admin_stats$"))
    app.add_handler(CallbackQueryHandler(handle_payment_decision, pattern="^(approve|reject)_"))
    app.add_handler(CallbackQueryHandler(back_to_start, pattern="^back_to_start$"))
    app.add_handler(CallbackQueryHandler(handle_network_selection, pattern="^network_"))
    app.add_handler(CallbackQueryHandler(cancel_withdrawal, pattern="^cancel_withdrawal$"))
    
    # Message handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_withdrawal))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_broadcast))
    
    # Error handler
    app.add_error_handler(lambda u, c: logger.error(f"Error: {c.error}", exc_info=True))
    
    # Simplified start message
    print(f"\n🤖 Bot is running - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"👑 Admin ID: {ADMIN_ID} (broadcast/stats only)")
    print(f"💳 Payment Admin Chat: {ADMIN_CHAT_ID}")
    print(f"👥 Total users: {len(data['users'])}")
    print(f"💰 Coin Name: {COIN_NAME}")
    print(f"🔤 Coin Symbol: {COIN_SYMBOL}")
    
    # Start polling
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()

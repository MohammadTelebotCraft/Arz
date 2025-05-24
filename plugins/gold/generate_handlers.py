import os
import json
import re

# Gold configurations with their symbols and triggers
GOLD_TYPES = [
    {
        'name': 'انس طلا',
        'symbol': '🏆',
        'triggers': ['انس طلا', 'gold ounce', 'xau']
    },
    {
        'name': 'انس نقره',
        'symbol': '🥈',
        'triggers': ['انس نقره', 'silver ounce', 'xag']
    },
    {
        'name': 'انس پلاتین',
        'symbol': '⚪',
        'triggers': ['انس پلاتین', 'platinum ounce', 'xpt']
    },
    {
        'name': 'انس پالادیوم',
        'symbol': '⭐',
        'triggers': ['انس پالادیوم', 'palladium ounce', 'xpd']
    },
    {
        'name': 'طلای 18 عیار',
        'symbol': '💍',
        'triggers': ['طلای 18 عیار', '18k gold', 'طلا 18']
    },
    {
        'name': 'طلای 24 عیار',
        'symbol': '💎',
        'triggers': ['طلای 24 عیار', '24k gold', 'طلا 24']
    },
    {
        'name': 'طلای دست دوم',
        'symbol': '🔄',
        'triggers': ['طلای دست دوم', 'used gold']
    },
    {
        'name': 'گرم نقره ۹۹۹',
        'symbol': '✨',
        'triggers': ['گرم نقره', 'silver gram']
    },
    {
        'name': 'مثقال طلا',
        'symbol': '⚖️',
        'triggers': ['مثقال طلا', 'gold mithqal']
    },
    {
        'name': 'آبشده نقدی',
        'symbol': '💧',
        'triggers': ['آبشده نقدی', 'melted gold']
    },
    {
        'name': 'سکه امامی',
        'symbol': '🏅',
        'triggers': ['سکه امامی', 'emami coin']
    },
    {
        'name': 'سکه بهار آزادی',
        'symbol': '🪙',
        'triggers': ['سکه بهار آزادی', 'azadi coin']
    },
    {
        'name': 'نیم سکه',
        'symbol': '🥇',
        'triggers': ['نیم سکه', 'half coin']
    },
    {
        'name': 'ربع سکه',
        'symbol': '🥉',
        'triggers': ['ربع سکه', 'quarter coin']
    },
    {
        'name': 'سکه گرمی',
        'symbol': '💰',
        'triggers': ['سکه گرمی', 'gram coin']
    },
    {
        'name': 'حباب سکه گرمی',
        'symbol': '🫧',
        'triggers': ['حباب سکه گرمی', 'حباب سکه گرمی', 'gram coin bubble']
    }
]

# New symbol mapping for gold items provided by user
NEW_GOLD_SYMBOLS_DATA = [
  { "currency": "انس طلا", "symbol": "🥇" },
  { "currency": "انس نقره", "symbol": "🥈" },
  { "currency": "انس پلاتین", "symbol": "⚪" },
  { "currency": "انس پالادیوم", "symbol": "⚫" },
  { "currency": "طلای 18 عیار", "symbol": "💛" },
  { "currency": "طلای 24 عیار", "symbol": "'''" },
  { "currency": "طلای دست دوم", "symbol": "♻️" },
  { "currency": "گرم نقره ۹۹۹", "symbol": "📏" },
  { "currency": "مثقال طلا", "symbol": "⚖️" },
  { "currency": "آبشده نقدی", "symbol": "💰" },
  { "currency": "حباب آبشده", "symbol": "🫧" },
  { "currency": "مثقال / بدون حباب", "symbol": "🧮" },
  { "currency": "صندوق طلای مفید", "symbol": "📦" },
  { "currency": "صندوق طلای لوتوس", "symbol": "🌸" },
  { "currency": "صندوق طلای مثقال", "symbol": "📊" },
  { "currency": "صندوق طلای گوهر", "symbol": "💎" },
  { "currency": "سکه امامی", "symbol": "🪙" },
  { "currency": "سکه بهار آزادی", "symbol": "🌞" },
  { "currency": "نیم سکه", "symbol": "🌓" },
  { "currency": "ربع سکه", "symbol": "🌓" }, # Note: User provided same symbol for نیم and ربع, this will be used.
  { "currency": "سکه گرمی", "symbol": "🌕" },
  { "currency": "حباب سکه امامی", "symbol": "🫧" },
  { "currency": "حباب سکه بهار آزادی", "symbol": "🫧" },
  { "currency": "حباب نیم سکه", "symbol": "🫧" },
  { "currency": "حباب ربع سکه", "symbol": "🫧" },
  { "currency": "حباب سکه گرمی", "symbol": "🫧" }
]

# Convert the list of new gold symbol data to a dictionary for easier lookup
# Renaming "currency" to "name" in the map key to match how gold_name is used later.
NEW_GOLD_SYMBOLS_MAP = {item["currency"]: item["symbol"] for item in NEW_GOLD_SYMBOLS_DATA}

# Template for gold handler files
TEMPLATE = '''from telethon import events
from telethon.tl.custom import Button
from ..utils import format_number, format_change

# Keywords that trigger this handler
TRIGGERS = {triggers}

async def handle_gold(event, client):
    """Handle {name} gold type requests"""
    data = event.client.gold_data
    if not data:
        await event.respond('متاسفانه در حال حاضر امکان دریافت اطلاعات طلا وجود ندارد. ❌')
        return

    gold_types = data.get('data', [])
    gold_info = next((g for g in gold_types if g['currencyName'] == '{name}'), None)
    
    if not gold_info:
        await event.respond('اطلاعات {name} در حال حاضر در دسترس نیست. ❌')
        return

    price = format_number(gold_info['livePrice'])
    change = format_change(gold_info['change'])
    lowest = format_number(gold_info['lowest'])
    highest = format_number(gold_info['highest'])
    time = gold_info['time']

    # Create buttons for displaying information
    buttons = [
        [Button.inline("💰 قیمت فعلی", b'noop'), Button.inline(f"{{price}} تومان", b'noop')],
        [Button.inline("📊 تغییرات", b'noop'), Button.inline(f"{{change}}", b'noop')],
        [Button.inline("⬇️ کمترین", b'noop'), Button.inline(f"{{lowest}}", b'noop')],
        [Button.inline("⬆️ بیشترین", b'noop'), Button.inline(f"{{highest}}", b'noop')],
        [Button.inline("🕒 بروزرسانی", b'noop'), Button.inline(f"{{time}}", b'noop')],
        [Button.url("📢 کانال ما", "https://t.me/TelebotCraft")],
        [Button.url("➕ افزودن ربات به گروه", f"https://t.me/{{(await client.get_me()).username}}?startgroup=true")]
    ]

    message = f"{symbol} نرخ لحظه‌ای {name}:"
    await event.respond(message, buttons=buttons)
'''

def make_filename(name):
    """Convert gold type name to a valid filename"""
    # Replace spaces with underscores and ensure a safe filename
    filename = name.replace(' ', '_')
    # Replace any characters that might cause issues in filenames
    filename = re.sub(r'[\\/:*?"<>|]', '', filename)
    return f"{filename}.py"

def get_existing_config(name, old_configs):
    """Find an existing config for a gold type by name"""
    for config in old_configs:
        if config['name'] == name:
            return config
    return None

def generate_gold_handlers():
    """Generate handler files for all gold types from generation_data.json"""
    # Load the JSON data
    try:
        # Path relative to plugins/gold/ where this script is located
        with open('../../generation_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading generation_data.json: {e}")
        return

    if 'GoldType' in data and 'data' in data['GoldType']:
        for item in data['GoldType']['data']:
            gold_name = item['name'] # Assuming 'name' is the key in generation_data.json for gold items
            
            symbol = '🥇'  # Default symbol

            # 1. Try the new user-provided symbol map first
            if gold_name in NEW_GOLD_SYMBOLS_MAP:
                symbol = NEW_GOLD_SYMBOLS_MAP[gold_name]
            else:
                # 2. Try the old hardcoded GOLD_TYPES list
                existing_config_old = get_existing_config(gold_name, GOLD_TYPES) # Uses GOLD_TYPES
                if existing_config_old and 'symbol' in existing_config_old:
                    symbol = existing_config_old['symbol']
            
            # Determine triggers (uses GOLD_TYPES for additional triggers)
            existing_config_for_triggers = get_existing_config(gold_name, GOLD_TYPES) # Uses GOLD_TYPES
            triggers = [gold_name] # Start with the gold name itself as a trigger
            if existing_config_for_triggers and 'triggers' in existing_config_for_triggers:
                for trigger in existing_config_for_triggers['triggers']:
                    if trigger not in triggers:
                        triggers.append(trigger)
            
            # Generate filename
            filename = make_filename(gold_name) # Ensure this is in the current dir (plugins/gold/)
            
            # Create the handler file
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    handler_code = TEMPLATE.format(
                        name=gold_name,
                        symbol=symbol,
                        triggers=repr(triggers)
                    )
                    f.write(handler_code)
                print(f"Generated gold handler for {gold_name}")
            except Exception as e:
                print(f"Error generating gold handler for {gold_name}: {e}")
    else:
        print("No 'GoldType' data found in generation_data.json")
        
    print("Gold handlers generation complete!")

if __name__ == '__main__':
    generate_gold_handlers() 
from telethon import events
from telethon.tl.custom import Button
from .utils import format_number, format_change

# Keywords that trigger this handler
TRIGGERS = ['NGN', 'Ngn', 'Nigerian Naira', 'naira', 'ngn', 'nigerian naira', 'نایرای نیجریه', 'نیرا نیجریه']

async def handle_currency(event, client):
    """Handle نیرا نیجریه currency requests"""
    data = event.client.currency_data
    if not data:
        await event.respond('متاسفانه در حال حاضر امکان دریافت اطلاعات نرخ ارز وجود ندارد. ❌')
        return

    # Try main currencies first
    currencies = data.get('mainCurrencies', {}).get('data', [])
    currency_info = next((c for c in currencies if c['currencyName'] == 'نیرا نیجریه'), None)
    
    # If not found in main currencies, try minor currencies
    if not currency_info:
        currencies = data.get('minorCurrencies', {}).get('data', [])
        currency_info = next((c for c in currencies if c['currencyName'] == 'نیرا نیجریه'), None)
    
    if not currency_info:
        await event.respond('اطلاعات نیرا نیجریه در حال حاضر در دسترس نیست. ❌')
        return

    price = format_number(currency_info['livePrice'])
    change = format_change(currency_info['change'])
    lowest = format_number(currency_info['lowest'])
    highest = format_number(currency_info['highest'])
    time = currency_info['time']

    # Create buttons for displaying information
    buttons = [
        [Button.inline("💰 قیمت فعلی", b'noop'), Button.inline(f"{price} تومان", b'noop')],
        [Button.inline("📊 تغییرات", b'noop'), Button.inline(f"{change}", b'noop')],
        [Button.inline("⬇️ کمترین", b'noop'), Button.inline(f"{lowest}", b'noop')],
        [Button.inline("⬆️ بیشترین", b'noop'), Button.inline(f"{highest}", b'noop')],
        [Button.inline("🕒 بروزرسانی", b'noop'), Button.inline(f"{time}", b'noop')],
        [Button.url("📢 کانال ما", "https://t.me/TelebotCraft")],
        [Button.url("➕ افزودن ربات به گروه", f"https://t.me/{(await client.get_me()).username}?startgroup=true")]
    ]

    message = f"🇳🇬 نرخ لحظه‌ای نیرا نیجریه:"
    await event.respond(message, buttons=buttons)

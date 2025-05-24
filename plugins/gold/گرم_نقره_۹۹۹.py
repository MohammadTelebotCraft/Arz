from telethon import events
from telethon.tl.custom import Button
from ..utils import format_number, format_change

# Keywords that trigger this handler
TRIGGERS = ['گرم نقره ۹۹۹', 'گرم نقره', 'silver gram']

async def handle_gold(event, client):
    """Handle گرم نقره ۹۹۹ gold type requests"""
    data = event.client.gold_data
    if not data:
        await event.respond('متاسفانه در حال حاضر امکان دریافت اطلاعات طلا وجود ندارد. ❌')
        return

    gold_types = data.get('data', [])
    gold_info = next((g for g in gold_types if g['currencyName'] == 'گرم نقره ۹۹۹'), None)
    
    if not gold_info:
        await event.respond('اطلاعات گرم نقره ۹۹۹ در حال حاضر در دسترس نیست. ❌')
        return

    price = format_number(gold_info['livePrice'])
    change = format_change(gold_info['change'])
    lowest = format_number(gold_info['lowest'])
    highest = format_number(gold_info['highest'])
    time = gold_info['time']

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

    message = f"✨ نرخ لحظه‌ای گرم نقره ۹۹۹:"
    await event.respond(message, buttons=buttons)

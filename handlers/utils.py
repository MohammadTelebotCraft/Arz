from telethon import Button
from typing import List, Dict, Any
from .constants import CURRENCY_FLAGS
COUNTRY_FLAGS_MAP = {item['name']: item['flag'] for item in CURRENCY_FLAGS}
def get_data_from_cache(client) -> Dict[str, Any]:
    """Get fresh data from cache"""
    return client.currency_cache.get_data()
def create_footer_buttons(bot_username: str) -> List[List[Button]]:
    """Create standard footer buttons"""
    return [
        [Button.url("📢 عضویت در کانال ما", "https://t.me/TelebotCraft")],
        [Button.url("➕ افزودن ربات به گروه", f"tg://resolve?domain={bot_username}&startgroup=true")]
    ]
def create_home_button() -> List[Button]:
    """Create home button"""
    return [Button.inline("🏠 صفحه اصلی", "home")]
def create_header_row() -> List[Button]:
    """Create standard header row for rates"""
    return [
        Button.inline("💱 نوع", b'noop_header'),
        Button.inline("💰 قیمت", b'noop_header'),
        Button.inline("📊 تغییر", b'noop_header')
    ]
def format_number(number: str) -> str:
    """Format number with commas"""
    try:
        num_str = str(number).replace(',', '')
        if len(num_str) > 3:
            parts = []
            while num_str:
                parts.append(num_str[-3:])
                num_str = num_str[:-3]
            return ','.join(reversed(parts))
        return num_str
    except:
        return str(number)
def format_change(change: str) -> str:
    """Format price change with arrows"""
    try:
        change_str = str(change).strip('()')
        if '(' in str(change):
            parts_for_percentage = str(change).split('(')
            if len(parts_for_percentage) > 1:
                percentage_part = parts_for_percentage[1].split(')')[0]
            value_part = change_str.split(')')[-1].strip() if ')' in change_str else change_str
        else:
            value_part = change_str
        change_value_numeric = value_part.split()[-1].replace(',', '')
        formatted_change = format_number(change_value_numeric)
        is_negative = False
        try:
            if float(change_value_numeric) < 0:
                is_negative = True
        except ValueError:
            if str(change).startswith('-'):
                 is_negative = True
        if is_negative:
            return f"📉 {format_number(change_value_numeric.lstrip('-'))}-"
        else:
            return f"📈 {formatted_change}+"
    except Exception as e:
        return str(change)
def create_currency_buttons(currency: Dict[str, Any], base_url: str) -> List[List[Button]]:
    """Create buttons for a single currency item with name, price, change, and chart link."""
    raw_name = currency.get('currencyName', 'N/A')
    flag = COUNTRY_FLAGS_MAP.get(raw_name, '')
    display_name = f"{flag} {raw_name}".strip()
    price = format_number(currency.get('livePrice', 'N/A'))
    change_value = currency.get('change', 'N/A')
    formatted_change_display = format_change(change_value)
    buttons = [
        [Button.inline(f"{display_name}", data=f"noop_{raw_name.replace(' ', '_')}"),
         Button.inline(f"{price} ت", data=f"noop_price_{raw_name.replace(' ', '_')}"),
         Button.inline(f"{formatted_change_display}", data=f"noop_change_{raw_name.replace(' ', '_')}")]
    ]
    return buttons

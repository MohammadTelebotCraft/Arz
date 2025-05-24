from telethon import events, Button
import math
from typing import List, Tuple
from .constants import BASE_CHART_URL
from .utils import create_currency_buttons, COUNTRY_FLAGS_MAP

# Constants
ITEMS_PER_PAGE = 10

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
        change = change.strip('()')
        if '(' in change:
            change = change.split('(')[1].split(')')[0]
        
        parts = change.split()
        if len(parts) > 1:
            change_value = parts[-1].replace(',', '')
        else:
            change_value = change.replace(',', '')
        
        formatted_change = format_number(change_value)
        if change.startswith('-'):
            return f"📉 {formatted_change}-"
        else:
            return f"📈 {formatted_change}+"
    except:
        return change

def get_main_currency_items(data: dict) -> List[Tuple[str, str, str]]:
    """Get main currency items from data"""
    if not data:
        return []
    
    currencies = data.get('mainCurrencies', {}).get('data', [])
    result = []
    for c in currencies:
        name = c['currencyName']
        # Add flag if available, otherwise just use the name
        flag = COUNTRY_FLAGS_MAP.get(name, '') 
        display_name = f"{flag} {name}".strip()
        result.append((display_name, c['livePrice'], c['change']))
    return result

def get_navigation_buttons(current_page: int, total_pages: int) -> List[List[Button]]:
    """Generate navigation buttons for main currencies"""
    buttons = []
    
    # Add page navigation
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(Button.inline("⬅️ قبلی", f"main_curr_{current_page-1}"))
    nav_buttons.append(Button.inline(f"📄 {current_page}/{total_pages}", "noop_page"))
    if current_page < total_pages:
        nav_buttons.append(Button.inline("بعدی ➡️", f"main_curr_{current_page+1}"))
    buttons.append(nav_buttons)
    
    # Add home button
    buttons.append([Button.inline("🏠 صفحه اصلی", "home")])
    
    # Add channel and group buttons
    buttons.extend([
        [Button.url("📢 عضویت در کانال ما", "https://t.me/TelebotCraft")],
        [Button.url("➕ افزودن ربات به گروه", "tg://resolve?domain={bot_username}&startgroup=true")]
    ])
    
    return buttons

async def show_main_currencies_page(event, page: int, client):
    """Show a specific page of main currencies"""
    # Get fresh data
    data = client.currency_data
    
    # Get items
    items = get_main_currency_items(data)
    
    # Calculate pagination
    total_pages = max(1, math.ceil(len(items) / ITEMS_PER_PAGE))
    page = min(max(1, page), total_pages)
    start_idx = (page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    # Instead of page_items, we need to get the full currency dict for create_currency_buttons
    raw_currencies = data.get('mainCurrencies', {}).get('data', [])
    current_page_raw_currencies = raw_currencies[start_idx:end_idx]

    all_buttons = [] # Initialize all_buttons
    # Create header row - this seems to be a different style than minor_currencies
    # For consistency, we might want to adapt, but for now, let's keep main_currencies' original header
    all_buttons.append([
        Button.inline("💱 نوع", b'noop_header'),
        Button.inline("💰 قیمت", b'noop_header'),
        Button.inline("📊 تغییر", b'noop_header')
    ])

    # Add items using create_currency_buttons for consistency
    for currency_data in current_page_raw_currencies:
        # We need to add the flag to the name before passing it or handle it inside create_currency_buttons
        # For now, let's adjust currency_data or expect create_currency_buttons to handle it.
        # The current create_currency_buttons uses 'currencyName'. 
        # get_main_currency_items was adding flags. Let's replicate that or pass it.
        
        # Option 1: Re-create a dictionary similar to what create_currency_buttons expects
        # or modify create_currency_buttons to accept the flag separately or look for it.
        
        # For simplicity, let's assume create_currency_buttons will just use currencyName
        # and we rely on the chart URL and noop callbacks not needing the flag in the name.
        # Or, even better, let create_currency_buttons handle the flag if present.
        
        # The `create_currency_buttons` expects `currencyName`, `livePrice`, `change`, `slug`.
        # The `get_main_currency_items` was creating a tuple. We need the raw dict items.
        
        # Let's ensure the name passed to create_currency_buttons includes the flag if CURRENCY_FLAGS is used.
        # The create_currency_buttons in utils.py currently does: name = currency.get('currencyName', 'N/A')
        # It does not add flags. The main_currencies.py was doing it manually.
        # For consistency, the button creation logic should be centralized.
        
        # Let's adjust the main_currencies.py to use the create_currency_buttons directly
        # and ensure create_currency_buttons in utils.py handles flag prepending.
        
        # MODIFICATION will be needed in utils.py for create_currency_buttons to handle flags.
        # For now, this edit will just call it, and we'll address flag in utils.py next.
        all_buttons.extend(create_currency_buttons(currency_data, BASE_CHART_URL))

    # Add navigation buttons
    nav_buttons = get_navigation_buttons(page, total_pages)
    all_buttons.extend(nav_buttons)
    
    # Get last update time
    last_update = "نامشخص"
    if items:
        currencies = data.get('mainCurrencies', {}).get('data', [])
        if currencies:
            last_update = currencies[0].get('time', "نامشخص")
    
    message = f"💱 نرخ ارزهای اصلی (آخرین بروزرسانی: {last_update})"
    
    try:
        if isinstance(event, events.CallbackQuery.Event):
            await event.edit(message, buttons=all_buttons)
        else:
            await event.respond(message, buttons=all_buttons)
    except Exception as e:
        # If edit fails for a callback, maybe try responding or just log and answer with error
        if isinstance(event, events.CallbackQuery.Event):
            await event.answer("خطا در نمایش صفحه ارزهای اصلی.", alert=True)

def register_handlers(client):
    """Register all handlers related to main currencies"""
    
    @client.on(events.CallbackQuery(pattern=r"main_curr_(\d+)"))
    async def handle_main_currency_pagination(event):
        """Handle main currency pagination"""
        try:
            page = int(event.pattern_match.group(1))
            await show_main_currencies_page(event, page, event.client)
            await event.answer()
        except Exception as e:
            await event.answer(f"خطا در تغییر صفحه: {str(e)}", alert=True)
        raise events.StopPropagation 
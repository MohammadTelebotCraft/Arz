from telethon import Button
from typing import List, Dict, Any
from .constants import CURRENCY_FLAGS

# Convert CURRENCY_FLAGS list to a dictionary for easier lookup
# This will be done once when the module is imported.
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
        # Ensure change_value is a string before stripping and splitting
        change_str = str(change).strip('()') 
        
        # Check if original change string contains '(' to avoid error on direct values
        if '(' in str(change): # Use original change for this check
            # Safely extract percentage part if present
            parts_for_percentage = str(change).split('(')
            if len(parts_for_percentage) > 1:
                percentage_part = parts_for_percentage[1].split(')')[0]
            # The actual value for formatting is usually after the percentage
            # This part needs to correctly identify the numeric value associated with the change.
            # The current logic splits by space after stripping parentheses.
            # If change is e.g. "(0.58%) 4,800", change_str becomes "0.58%) 4,800"
            # We need the "4,800" part.
            value_part = change_str.split(')')[-1].strip() if ')' in change_str else change_str
        else:
            value_part = change_str # It's already the value part

        change_value_numeric = value_part.split()[-1].replace(',', '') # Get the last part, assuming it's the number
        
        formatted_change = format_number(change_value_numeric)
        
        # Determine trend based on the original input or the numeric part if it contains a sign
        # The provided `change` string might not always start with '-' for negative, 
        # e.g. it could be from an API that gives it as a signed number in the value part.
        # For now, let's assume the initial logic of checking original `change` for '-' is intended.
        # If change_value_numeric itself can be negative, that should be used.
        
        # Simplified trend check: if the numeric part (after parsing) is negative.
        # We need to parse it to a float/int for this. Robustly.
        is_negative = False
        try:
            if float(change_value_numeric) < 0:
                is_negative = True
        except ValueError:
            # If it's not a simple number (e.g. contains % or other text not stripped)
            # fallback to original check on the string
            if str(change).startswith('-'): # Check original input for negative sign
                 is_negative = True

        if is_negative:
            # Ensure the minus sign isn't duplicated if format_number already includes it (it shouldn't)
            return f"📉 {format_number(change_value_numeric.lstrip('-'))}-" 
        else:
            return f"📈 {formatted_change}+"
    except Exception as e:
        # print(f"Error formatting change '{change}': {e}") # Optional: for debugging
        return str(change) # Fallback to original change string if any error

def create_currency_buttons(currency: Dict[str, Any], base_url: str) -> List[List[Button]]:
    """Create buttons for a single currency item with name, price, change, and chart link."""
    raw_name = currency.get('currencyName', 'N/A')
    # Prepend flag if available in COUNTRY_FLAGS_MAP
    flag = COUNTRY_FLAGS_MAP.get(raw_name, '') 
    display_name = f"{flag} {raw_name}".strip()
    
    price = format_number(currency.get('livePrice', 'N/A'))
    change_value = currency.get('change', 'N/A')
    
    formatted_change_display = format_change(change_value)

    # Chart URL is no longer needed
    # chart_url = f"{base_url}{currency.get('slug', 'default')}" 

    buttons = [
        # Single row: [Name, Price, Change]
        [Button.inline(f"{display_name}", data=f"noop_{raw_name.replace(' ', '_')}"),
         Button.inline(f"{price} ت", data=f"noop_price_{raw_name.replace(' ', '_')}"), # Added "ت" for Toman
         Button.inline(f"{formatted_change_display}", data=f"noop_change_{raw_name.replace(' ', '_')}")]
        # Removed chart button and separator
    ]
    return buttons 
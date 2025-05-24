"""
Inline query handler for the currency bot.
This module handles inline queries for currency prices.
"""

import logging
import re
from telethon import events
from ..utils import format_number, format_change

logger = logging.getLogger(__name__)

# Create a mapping of search terms to currency names
CURRENCY_MAPPING = {}

def initialize_currency_mapping(comprehensive_config):
    """Initialize the currency mapping from the comprehensive config"""
    global CURRENCY_MAPPING
    for config in comprehensive_config:
        name = config['name']
        for trigger in config['triggers']:
            CURRENCY_MAPPING[trigger.lower()] = {
                'name': name,
                'flag': config['flag']
            }
    logger.info(f"Initialized currency mapping with {len(CURRENCY_MAPPING)} entries")

async def handle_inline_query(event):
    """Handle inline queries for currency prices"""
    builder = event.builder
    query = event.text.lower().strip()
    
    # Get the currency data from cache
    client = event.client
    data = client.currency_cache.get_data()
    
    results = []
    
    if not data:
        # Return an error message if no data is available
        results.append(
            builder.article(
                title="خطا در دریافت اطلاعات",
                description="متاسفانه در حال حاضر امکان دریافت اطلاعات نرخ ارز وجود ندارد.",
                text="متاسفانه در حال حاضر امکان دریافت اطلاعات نرخ ارز وجود ندارد. ❌"
            )
        )
        await event.answer(results)
        return
    
    # Combine main and minor currencies
    all_currencies = []
    if 'mainCurrencies' in data and 'data' in data['mainCurrencies']:
        all_currencies.extend(data['mainCurrencies']['data'])
    if 'minorCurrencies' in data and 'data' in data['minorCurrencies']:
        all_currencies.extend(data['minorCurrencies']['data'])
    
    # Create a mapping of currency names to their data
    currency_data_map = {c['currencyName']: c for c in all_currencies}
    
    # If query is empty, show popular currencies first, then the rest
    if not query:
        # Define popular currencies to show first
        popular_currencies = ['دلار', 'یورو', 'پوند انگلیس', 'درهم امارات', 'لیر ترکیه', 
                             'دلار کانادا', 'دلار استرالیا', 'یوان چین', 'ین ژاپن', 'فرانک سوئیس']
        
        # Add popular currencies first
        for currency_name in popular_currencies:
            if currency_name in currency_data_map:
                flag = CURRENCY_MAPPING.get(currency_name.lower(), {'flag': '🌐'}).get('flag', '🌐')
                results.append(create_currency_result(builder, currency_name, currency_data_map[currency_name], flag))
        
        # Get all remaining currencies
        remaining_currencies = [name for name in currency_data_map.keys() if name not in popular_currencies]
        # Sort alphabetically
        remaining_currencies.sort()
        
        # Add remaining currencies (up to Telegram's limit of 50 total results)
        remaining_slots = 50 - len(results)
        for currency_name in remaining_currencies[:remaining_slots]:
            flag = CURRENCY_MAPPING.get(currency_name.lower(), {'flag': '🌐'}).get('flag', '🌐')
            results.append(create_currency_result(builder, currency_name, currency_data_map[currency_name], flag))
    else:
        # Search for matching currencies
        matched_currencies = set()
        
        # First check for exact matches in our mapping
        for search_term, currency_info in CURRENCY_MAPPING.items():
            if query in search_term or search_term in query:
                currency_name = currency_info['name']
                if currency_name in currency_data_map and currency_name not in matched_currencies:
                    results.append(create_currency_result(builder, currency_name, currency_data_map[currency_name], currency_info['flag']))
                    matched_currencies.add(currency_name)
        
        # Then check for partial matches in currency names
        for currency_name, currency_data in currency_data_map.items():
            if currency_name not in matched_currencies and query in currency_name.lower():
                flag = CURRENCY_MAPPING.get(currency_name.lower(), {'flag': '🌐'}).get('flag', '🌐')
                results.append(create_currency_result(builder, currency_name, currency_data, flag))
                matched_currencies.add(currency_name)
    
    # If no results were found, show a message
    if not results:
        results.append(
            builder.article(
                title="ارز مورد نظر یافت نشد",
                description="لطفا با کلمه کلیدی دیگری جستجو کنید",
                text="ارز مورد نظر یافت نشد. لطفا با کلمه کلیدی دیگری جستجو کنید. ❌"
            )
        )
    
    # Return the results (limit to 50 as per Telegram's limit)
    await event.answer(results[:50])

def create_currency_result(builder, currency_name, currency_data, flag):
    """Create an inline result for a currency"""
    price = format_number(currency_data['livePrice'])
    change = format_change(currency_data['change'])
    lowest = format_number(currency_data['lowest'])
    highest = format_number(currency_data['highest'])
    time = currency_data['time']
    
    title = f"{flag} {currency_name}"
    description = f"قیمت: {price} تومان | تغییرات: {change}"
    
    content = f"{flag} نرخ لحظه‌ای {currency_name}:\n\n"
    content += f"💰 قیمت فعلی: {price} تومان\n"
    content += f"📊 تغییرات: {change}\n"
    content += f"⬇️ کمترین: {lowest}\n"
    content += f"⬆️ بیشترین: {highest}\n"
    content += f"🕒 بروزرسانی: {time}\n\n"
    content += "📢 @TelebotCraft"
    
    return builder.article(
        title=title,
        description=description,
        text=content
    )

def register_inline_handlers(client):
    """Register inline query handlers"""
    # Import the comprehensive config here to avoid circular imports
    from ..generate_handlers import COMPREHENSIVE_CURRENCY_CONFIGS
    
    # Initialize the currency mapping
    initialize_currency_mapping(COMPREHENSIVE_CURRENCY_CONFIGS)
    
    # Register the inline query handler
    client.add_event_handler(handle_inline_query, events.InlineQuery())
    
    logger.info("Registered inline query handler")

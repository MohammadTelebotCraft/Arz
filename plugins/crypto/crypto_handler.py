"""
Crypto handler module for the currency bot.
This module handles displaying cryptocurrency data and registering handlers.
"""

import logging
import time
import re
import aiohttp
import json
from typing import Dict, Any, List, Optional, Tuple
from telethon import events
from telethon.tl.custom import Button
from .crypto_cache import crypto_cache, POPULAR_CRYPTO_SYMBOLS, CRYPTO_INFO
from .currency_converter import format_number

# Dictionary to convert Persian digits to English digits
PERSIAN_DIGITS = {
    '۰': '0',
    '۱': '1',
    '۲': '2',
    '۳': '3',
    '۴': '4',
    '۵': '5',
    '۶': '6',
    '۷': '7',
    '۸': '8',
    '۹': '9',
}

# Cache for USDT price to avoid too many API calls
USDT_PRICE_CACHE = {
    'price': None,
    'timestamp': 0,
    'ttl': 300  # 5 minutes cache TTL
}

logger = logging.getLogger(__name__)

class CryptoHandler:
    """Handler for cryptocurrency commands and queries"""
    
    def __init__(self, symbol: str, name: str, icon: str, triggers: List[str]):
        """Initialize the crypto handler
        
        Args:
            symbol: The crypto symbol (e.g., 'BTCIRT')
            name: The Persian name of the cryptocurrency
            icon: The icon/emoji for the cryptocurrency
            triggers: List of trigger words to activate this handler
        """
        self.symbol = symbol
        self.name = name
        self.icon = icon
        self.triggers = triggers
        self.base_symbol = symbol.split('IRT')[0].split('USDT')[0]
        self.quote_symbol = 'IRT' if 'IRT' in symbol else 'USDT'
        self.quote_name = 'تومان' if self.quote_symbol == 'IRT' else 'دلار'
        
    def _parse_amount(self, amount_str: str) -> Optional[float]:
        """Parse an amount string, handling Persian digits and commas
        
        Args:
            amount_str: The amount string to parse
            
        Returns:
            The parsed amount as a float, or None if parsing failed
        """
        if not amount_str:
            return None
            
        # Convert Persian digits to English digits
        for persian_digit, english_digit in PERSIAN_DIGITS.items():
            amount_str = amount_str.replace(persian_digit, english_digit)
            
        # Remove commas and spaces
        amount_str = amount_str.replace(',', '').replace(' ', '')
        
        try:
            amount = float(amount_str)
            
            # Add a limit to prevent extremely large numbers
            MAX_AMOUNT = 1000000000  # 1 billion
            if amount > MAX_AMOUNT:
                logger.warning(f"Amount {amount} exceeds maximum limit of {MAX_AMOUNT}")
                return None
                
            return amount if amount > 0 else None  # Only return positive amounts
        except ValueError:
            logger.error(f"Could not parse amount: {amount_str}")
            return None
        
    async def handle_crypto(self, event, client, amount_str: Optional[str] = None):
        """Handle cryptocurrency requests
        
        Args:
            event: The Telegram event
            client: The Telegram client
            amount_str: Optional string representing the amount from the message
        """
        # Parse the amount if provided
        parsed_amount = None
        if amount_str:
            parsed_amount = self._parse_amount(amount_str)
            if parsed_amount is None:
                # Check if it's because of the limit
                try:
                    test_amount = float(amount_str.replace(',', '').replace(' ', ''))
                    if test_amount > 1000000000:
                        await event.respond(f"❌ مقدار وارد شده بسیار بزرگ است. لطفاً عددی کمتر از 1,000,000,000 وارد کنید.")
                    else:
                        return
                except:
                    print("Invalid amount")
                return
        else:
            # Default to 1 unit if no amount provided
            parsed_amount = 1.0
            
        # Try to update the cache first if data is not available
        data = crypto_cache.get_data(self.symbol)
        
        # Special handling for USDT
        if 'USDT' in self.symbol and not data:
            # Try to get live USDT price
            usdt_price_data = await get_live_usdt_price()
            
            if usdt_price_data and usdt_price_data.get('price'):
                usdt_rate = usdt_price_data['price']
                is_live = True
                logger.info(f"Using live USDT data with rate {usdt_rate}")
            else:
                # Fallback to fixed rate if live data isn't available
                usdt_rate = 42000  # 1 USDT = 42,000 تومان
                is_live = False
                logger.info(f"Using fallback USDT rate of {usdt_rate}")
            
            # Create a synthetic data object
            data = {
                'lastTradePrice': str(usdt_rate),
                'asks': [[str(usdt_rate), '1']],
                'bids': [[str(usdt_rate), '1']],
                'timestamp': usdt_price_data.get('timestamp', time.time()) if is_live else time.time(),
                'priceChange': usdt_price_data.get('change', '0'),
                'priceChangePercent': usdt_price_data.get('change_percent', '0'),
                'synthetic': not is_live,  # Mark as synthetic only if using fallback
                'live': is_live
            }
            logger.info(f"Created {'live' if is_live else 'synthetic'} USDT data for {self.symbol} with rate {usdt_rate}")
        elif not data:
            # For non-USDT pairs, try to force an update
            crypto_cache._update_cache_for_symbol(self.symbol)
            # Try to get the data again
            data = crypto_cache.get_data(self.symbol)
        
        if not data:
            await event.respond(f'اطلاعات {self.name} در حال حاضر در دسترس نیست. ❌')
            return
        
        # Format the data
        price = self._format_price(data.get('lastTradePrice', '0'))
        
        # Get best ask and bid prices
        best_ask = self._get_best_price(data.get('asks', []), 'ask')
        best_bid = self._get_best_price(data.get('bids', []), 'bid')
        
        # Calculate the time since last update
        update_time = self._format_update_time(data.get('timestamp', time.time()))
        
        # Add a note if this is synthetic data
        is_synthetic = data.get('synthetic', False)
        
        # Get USD price if this is an IRT pair
        usd_price = ""
        if 'IRT' in self.symbol:
            # Try to get the USD price from USDT pair
            usdt_symbol = f"{self.base_symbol}USDT"
            usdt_data = crypto_cache.get_data(usdt_symbol)
            if usdt_data and 'lastTradePrice' in usdt_data:
                usd_price = self._format_price(usdt_data.get('lastTradePrice', '0'))
        
        # Get raw price values for caption
        try:
            # Convert from Rials to Tomans if this is an IRT pair (1 Toman = 10 Rials)
            rial_to_toman_conversion = 10 if 'IRT' in self.symbol else 1
            
            # Get the unit price and convert if needed
            unit_price_value = float(data.get('lastTradePrice', '0'))
            if 'IRT' in self.symbol and not data.get('already_converted', False):
                unit_price_value = unit_price_value / rial_to_toman_conversion
                logger.info(f"Converted price from {unit_price_value * rial_to_toman_conversion} Rials to {unit_price_value} Tomans for {self.symbol}")
            
            # Calculate total value
            total_value = unit_price_value * parsed_amount
            
            # Format prices for display - handle empty or zero values
            if unit_price_value == 0:
                raw_unit_price = "N/A"
            else:
                raw_unit_price = f"{int(unit_price_value):,}" if unit_price_value >= 1 else f"{unit_price_value:.8f}"
                
            if total_value == 0:
                raw_total_price = "N/A"
            else:
                raw_total_price = f"{int(total_value):,}" if total_value >= 1 else f"{total_value:.8f}"
            
            # Get and convert ask/bid prices
            ask_price = float(data.get('asks', [[0, 0]])[0][0]) if data.get('asks') else 0
            bid_price = float(data.get('bids', [[0, 0]])[0][0]) if data.get('bids') else 0
            
            if 'IRT' in self.symbol and not data.get('already_converted', False):
                ask_price = ask_price / rial_to_toman_conversion
                bid_price = bid_price / rial_to_toman_conversion
            
            raw_ask = f"{int(ask_price):,}" if ask_price >= 1 else ("N/A" if ask_price == 0 else f"{ask_price:.8f}")
            raw_bid = f"{int(bid_price):,}" if bid_price >= 1 else ("N/A" if bid_price == 0 else f"{bid_price:.8f}")
            
            # Mark data as already converted to avoid double conversion
            data['already_converted'] = True
        except (ValueError, IndexError):
            unit_price_value = 0
            total_value = 0
            raw_unit_price = "N/A"
            raw_total_price = "N/A"
            raw_ask = "N/A"
            raw_bid = "N/A"
            
        # Get price change data directly from the API data
        # Don't use hardcoded values
        
        # For debugging, also try to get the real change data
        price_change = data.get('priceChange')
        # Calculate price change and percentage
        change_emoji = ""
        change_text = ""
        
        # Special handling for USDT - don't use hardcoded changes for amount queries
        if 'USDT' in self.symbol and parsed_amount != 1.0:
            # Skip showing price changes for amount queries on USDT
            change_emoji = ""
            change_text = ""
        elif data.get('priceChange') is not None and data.get('priceChangePercent') is not None:
            try:
                price_change = float(data.get('priceChange', 0))
                price_change_percent = float(data.get('priceChangePercent', 0))
                
                # Only show changes if they're meaningful
                if abs(price_change) < 0.000001:
                    change_emoji = ""
                    change_text = ""
                elif price_change > 0:
                    change_emoji = "🟢 ↗️"
                    change_text = f"+{int(price_change):,} ({price_change_percent:.2f}%)"
                elif price_change < 0:
                    change_emoji = "🔴 ↘️"
                    change_text = f"{int(price_change):,} ({price_change_percent:.2f}%)"
                else:
                    change_emoji = "⚪️ ↔️"
                    change_text = "بدون تغییر (0%)"
            except (ValueError, TypeError) as e:
                logger.error(f"Error formatting change: {e}")
                change_emoji = ""
                change_text = ""
        
        # Create a formatted text message with all information
        if parsed_amount == 1.0 and amount_str is None:
            # Standard price display for single unit
            caption = f"{self.icon} **نرخ لحظه‌ای {self.name}:**\n\n"
            caption += f"💰 **قیمت:** {raw_unit_price} {self.quote_name}\n"
        else:
            # Show ONLY the total value for specified amount
            formatted_amount = format_number(parsed_amount)
            
            # Don't include the crypto name in the value line if it's USDT
            if 'USDT' in self.symbol:
                caption = f"{self.icon} **ارزش {formatted_amount} {self.name}:**\n\n"
                caption += f"💰 **{formatted_amount} = {raw_total_price} {self.quote_name}**\n"
            else:
                caption = f"{self.icon} **ارزش {formatted_amount} {self.name}:**\n\n"
                caption += f"💰 **{formatted_amount} {self.name} = {raw_total_price} {self.quote_name}**\n"
            
        # Add note about data source for USDT - only for single unit queries
        if 'USDT' in self.symbol and parsed_amount == 1.0 and amount_str is None:
            if is_synthetic:
                caption += "\n💡 **(نرخ تقریبی)**\n"
            elif data.get('live', False):
                caption += "\n💹 **(نرخ زنده)**\n"
        
        # Add change information if available and not an amount query for USDT
        if change_text and not ('USDT' in self.symbol and parsed_amount != 1.0):
            caption += f"{change_emoji} **تغییرات:** {change_text}\n"
            
        caption += f"📈 **قیمت فروش:** {raw_ask} {self.quote_name}\n"
        caption += f"📉 **قیمت خرید:** {raw_bid} {self.quote_name}\n\n"
        caption += f"🕒 **بروزرسانی:** {update_time}\n\n"
        
        # Add USD price if available and this is a standard query (not an amount query)
        if usd_price and 'IRT' in self.symbol and parsed_amount == 1.0 and amount_str is None:
            # Get raw USD price
            try:
                # Convert from Rials to Tomans if this is an IRT pair (1 Toman = 10 Rials)
                raw_usd_price = f"{int(usdt_data.get('lastTradePrice', '0')):,}"
            except (ValueError, TypeError):
                raw_usd_price = usdt_data.get('lastTradePrice', '0') if usdt_data else "N/A"
                
            caption += f"💵 **قیمت دلاری:** {raw_usd_price} دلار\n\n"
        
        caption += "📢 @TelebotCraft"
        
        # Get the user ID who requested this price
        user_id = event.sender_id
        
        # Log the request
        if parsed_amount == 1.0 and amount_str is None:
            logger.info(f"User {user_id} requested price for {self.symbol}")
        else:
            logger.info(f"User {user_id} requested price for {parsed_amount} {self.symbol}")
        
        # Create simplified buttons - only show channel button for amount queries
        if parsed_amount == 1.0 and amount_str is None:
            # Standard buttons for regular price query
            buttons = [
                [Button.inline(f"💰 قیمت معامله", b'noop'), Button.inline(f"{price} {self.quote_name}", b'noop')],
                [Button.inline(f"📈 قیمت فروش", b'noop'), Button.inline(f"{best_ask} {self.quote_name}", b'noop')],
                [Button.inline(f"📉 قیمت خرید", b'noop'), Button.inline(f"{best_bid} {self.quote_name}", b'noop')],
                [Button.url("📢 کانال ما", "https://t.me/TelebotCraft")]
            ]
        else:
            # Simplified buttons for amount query - just the channel button
            buttons = [
                [Button.url("📢 @TelebotCraft", "https://t.me/TelebotCraft")]
            ]
        
        # Check if this is a refresh (edit) or new message
        if hasattr(event, 'message_id') and hasattr(event, 'edit'):
            # This is a button press, edit the message
            await event.edit(caption, buttons=buttons)
        else:
            # This is a new request, send a new message
            await event.respond(caption, buttons=buttons)
    
    def _format_price(self, price_str: str) -> str:
        """Format the price string with commas and convert large numbers to text
        
        Args:
            price_str: The price string from the API
            
        Returns:
            Formatted price string with text for large numbers
        """
        try:
            # Convert to float first to handle decimal values
            price_float = float(price_str)
            
            # Convert from Rials to Tomans if this is an IRT pair (1 Toman = 10 Rials)
            if 'IRT' in self.symbol:
                price_float = price_float / 10
            
            # Convert to integer for formatting if it's a whole number
            price = int(price_float) if price_float == int(price_float) else price_float
            
            # Convert to text for large numbers
            if price >= 1_000_000_000_000:  # Trillion
                return f"{price / 1_000_000_000_000:.2f} تریلیون"
            elif price >= 1_000_000_000:  # Billion
                return f"{price / 1_000_000_000:.2f} میلیارد"
            elif price >= 1_000_000:  # Million
                return f"{price / 1_000_000:.2f} میلیون"
            elif price >= 1_000:  # Thousand
                return f"{price / 1_000:.2f} هزار"
            else:
                return f"{price:,}"
        except (ValueError, TypeError):
            return price_str
    
    def _get_best_price(self, orders: List[List[str]], order_type: str) -> str:
        """Get the best ask or bid price from the orders
        
        Args:
            orders: List of orders from the API
            order_type: Either 'ask' or 'bid'
            
        Returns:
            The best price formatted with commas
        """
        if not orders:
            return "N/A"
        
        # For asks, the best price is the lowest (first in the list)
        # For bids, the best price is the highest (first in the list)
        best_price = orders[0][0]
        
        # Convert from Rials to Tomans if needed before formatting
        if 'IRT' in self.symbol:
            try:
                best_price_float = float(best_price) / 10
                best_price = str(best_price_float)
            except (ValueError, TypeError):
                pass
                
        return self._format_price(best_price)
    
    def _format_update_time(self, timestamp: float) -> str:
        """Format the update time as a human-readable string
        
        Args:
            timestamp: Unix timestamp of the last update
            
        Returns:
            Human-readable time string
        """
        now = time.time()
        diff = now - timestamp
        
        if diff < 60:
            return "چند ثانیه پیش"
        elif diff < 3600:
            minutes = int(diff / 60)
            return f"{minutes} دقیقه پیش"
        else:
            hours = int(diff / 3600)
            return f"{hours} ساعت پیش"
    
    def _format_symbol(self) -> str:
        """Format the symbol for display
        
        Returns:
            Formatted symbol string
        """
        if 'IRT' in self.symbol:
            return f"{self.base_symbol}/IRT"
        elif 'USDT' in self.symbol:
            return f"{self.base_symbol}/USDT"
        return self.symbol


async def show_crypto_list(event, client):
    """Show the list of available cryptocurrencies
    
    Args:
        event: The Telegram event
        client: The Telegram client
    """
    try:
        logger.info("Showing crypto list")
        # Get all available symbols from the cache
        all_symbols = crypto_cache.get_all_symbols()
        logger.info(f"Got {len(all_symbols)} symbols from cache")
        
        # Split into IRT and USDT symbols
        irt_symbols = [s for s in all_symbols if 'IRT' in s]
        usdt_symbols = [s for s in all_symbols if 'USDT' in s]
        logger.info(f"Split into {len(irt_symbols)} IRT symbols and {len(usdt_symbols)} USDT symbols")
        
        # Use custom emojis for popular cryptocurrencies
        custom_emojis = {
            'BTC': '₿',  # Bitcoin
            'ETH': 'Ξ',  # Ethereum
            'LTC': 'Ł',  # Litecoin
            'USDT': '₮',  # Tether
            'BNB': '🔶',  # Binance Coin
            'SOL': '☀️',  # Solana
            'ADA': '🦊',  # Cardano
            'XRP': '💧',  # Ripple
            'DOGE': 'Ð',  # Dogecoin
            'DOT': '◉',  # Polkadot
            'SHIB': '🐕',  # Shiba Inu
            'MATIC': '🔷',  # Polygon
            'AVAX': '🔺',  # Avalanche
            'TRX': '♦️',  # Tron
        }
        
        # Create buttons for IRT pairs
        irt_buttons = []
        for symbol in irt_symbols:
            base_symbol = symbol.split('IRT')[0]
            info = crypto_cache.get_crypto_info(base_symbol)
            # Use custom emoji if available, otherwise use the default icon
            emoji = custom_emojis.get(base_symbol, info.get('icon', '🔸'))
            name = info.get('name', base_symbol)
            irt_buttons.append(
                Button.inline(f"{emoji} {name}", f"crypto_{symbol}")
            )
        
        # Create buttons for USDT pairs
        usdt_buttons = []
        for symbol in usdt_symbols:
            base_symbol = symbol.split('USDT')[0]
            info = crypto_cache.get_crypto_info(base_symbol)
            # Use custom emoji if available, otherwise use the default icon
            emoji = custom_emojis.get(base_symbol, info.get('icon', '🔹'))
            name = info.get('name', base_symbol)
            usdt_buttons.append(
                Button.inline(f"{emoji} {name}", f"crypto_{symbol}")
            )
        
        # Arrange buttons in rows of 2
        irt_rows = [irt_buttons[i:i+2] for i in range(0, len(irt_buttons), 2)]
        usdt_rows = [usdt_buttons[i:i+2] for i in range(0, len(usdt_buttons), 2)]
        
        # Add navigation buttons without the headers
        buttons = []
        buttons.extend(irt_rows)
        buttons.extend(usdt_rows)
        buttons.append([Button.inline("🏠 بازگشت به منوی اصلی", b"home")])
        buttons.append([Button.url("📢 کانال ما", "https://t.me/TelebotCraft")])
        
        message = "🪙 <b>لیست ارزهای دیجیتال:</b>\n\nلطفا یکی از ارزهای دیجیتال را انتخاب کنید:"
        logger.info("Sending crypto list message with buttons")
        await event.respond(message, buttons=buttons, parse_mode='html')
        logger.info("Crypto list message sent successfully")
    except Exception as e:
        logger.error(f"Error in show_crypto_list: {str(e)}", exc_info=True)
        await event.answer(f"خطا در نمایش لیست ارزهای دیجیتال: {str(e)}", alert=True)


async def handle_usdt_price(event, client):
    """Handle USDT price requests
    
    Args:
        event: The Telegram event
        client: The Telegram client
    """
    # Create a handler for USDT
    handler = CryptoHandler(
        symbol="USDTIRT",
        name="تتر",
        icon="💵",
        triggers=["usdt", "تتر"]
    )
    
    # Process the request
    await handler.handle_crypto(event, client)
    return True


async def handle_crypto_button(event, client):
    """Handle crypto button presses
    
    Args:
        event: The Telegram event
        client: The Telegram client
    """
    # Get the data from the button
    data = event.data.decode('utf-8')
    
    # Check if this is a crypto button
    if not data.startswith('crypto_'):
        return
    
    # Extract the symbol
    symbol = data.replace('crypto_', '')
    
    # Get the current user ID
    current_user_id = event.sender_id
    
    # Parse the button data which might include user ID
    parts = data.split('crypto_')[1].split('_')
    
    if len(parts) >= 2:
        # New format with user ID
        symbol = parts[0]
        try:
            original_user_id = int(parts[1])
            
            # Check if the current user is the original requester
            if current_user_id != original_user_id:
                # This button is for another user
                await event.answer("این دکمه برای شما نیست! لطفاً خودتان قیمت را درخواست کنید.", alert=True)
                return
        except (ValueError, IndexError):
            # Error parsing user ID
            symbol = data.replace('crypto_', '')
    else:
        # Old format without user ID (for backward compatibility)
        symbol = data.split('crypto_')[1]
    
    # Extract the base symbol
    base_symbol = symbol.split('IRT')[0].split('USDT')[0]
    
    # Get crypto info
    info = crypto_cache.get_crypto_info(base_symbol)
    
    # Create a handler and process the request
    handler = CryptoHandler(
        symbol=symbol,
        name=info.get('name', base_symbol),
        icon=info.get('icon', ''),
        triggers=[base_symbol]
    )
    
    await handler.handle_crypto(event, client)


async def get_live_usdt_price() -> Dict[str, Any]:
    """Get the live USDT price from external APIs
    
{{ ... }}
    Returns:
        Dictionary with price, timestamp, and other data in Tomans
    """
    global USDT_PRICE_CACHE
    
    # Check if we have a valid cached price
    current_time = time.time()
    if USDT_PRICE_CACHE['price'] and (current_time - USDT_PRICE_CACHE['timestamp']) < USDT_PRICE_CACHE['ttl']:
        logger.info(f"Using cached USDT price: {USDT_PRICE_CACHE['price']} Tomans")
        return USDT_PRICE_CACHE
    
    # List of APIs to try (in order of preference)
    apis = [
        {
            'url': 'https://api.nobitex.ir/v2/trades/USDTIRT',
            'parser': parse_nobitex_usdt
        },
        {
            'url': 'https://api.tetherland.com/currencies',
            'parser': parse_tetherland_usdt
        },
        {
            'url': 'https://api.exir.io/v1/ticker/usdt-irt',
            'parser': parse_exir_usdt
        }
    ]
    
    result = None
    
    # Try each API until we get a valid result
    for api in apis:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api['url'], timeout=5) as response:
                    if response.status == 200:
                        data = await response.text()
                        result = api['parser'](data)
                        if result and result.get('price'):
                            # Update cache
                            USDT_PRICE_CACHE = result
                            USDT_PRICE_CACHE['timestamp'] = current_time
                            logger.info(f"Updated USDT price cache: {result['price']} from {api['url']}")
                            return result
        except Exception as e:
            logger.error(f"Error fetching USDT price from {api['url']}: {str(e)}")
    
    # Return None if all APIs failed
    return None

def parse_nobitex_usdt(data: str) -> Dict[str, Any]:
    """Parse USDT price data from Nobitex API"""
    try:
        json_data = json.loads(data)
        trades = json_data.get('trades', [])
        if trades:
            # Get the latest trade
            latest_trade = trades[0]
            price = float(latest_trade.get('price', 0))
            
            # Nobitex returns price in Rials, convert to Tomans (1 Toman = 10 Rials)
            price = price / 10
            
            return {
                'price': price,
                'change': '0',  # Nobitex doesn't provide change in this endpoint
                'change_percent': '0',
                'source': 'nobitex'
            }
    except Exception as e:
        logger.error(f"Error parsing Nobitex data: {str(e)}")
    return None

def parse_tetherland_usdt(data: str) -> Dict[str, Any]:
    """Parse USDT price data from Tetherland API"""
    try:
        json_data = json.loads(data)
        usdt_data = next((c for c in json_data if c.get('symbol') == 'USDT'), None)
        if usdt_data:
            price = float(usdt_data.get('price', 0))
            
            # Tetherland returns price in Rials, convert to Tomans (1 Toman = 10 Rials)
            price = price / 10
            
            # Change is also in Rials
            change = float(usdt_data.get('change', '0')) / 10 if usdt_data.get('change') else '0'
            
            return {
                'price': price,
                'change': str(change),
                'change_percent': usdt_data.get('changePercent', '0'),
                'source': 'tetherland'
            }
    except Exception as e:
        logger.error(f"Error parsing Tetherland data: {str(e)}")
    return None

def parse_exir_usdt(data: str) -> Dict[str, Any]:
    """Parse USDT price data from Exir API"""
    try:
        json_data = json.loads(data)
        price = float(json_data.get('last', 0))
        
        # Exir returns price in Rials, convert to Tomans (1 Toman = 10 Rials)
        price = price / 10
        
        # Calculate change in Tomans
        last_price = float(json_data.get('last', 0)) / 10
        open_price = float(json_data.get('open', 0)) / 10
        change = last_price - open_price
        
        return {
            'price': price,
            'change': str(change),
            'change_percent': json_data.get('percentChange', '0'),
            'source': 'exir'
        }
    except Exception as e:
        logger.error(f"Error parsing Exir data: {str(e)}")
    return None

def register_crypto_handlers(client):
    logger.info("Registering crypto handlers...")
    try:
        for symbol_pair in POPULAR_CRYPTO_SYMBOLS:
            base_symbol = None
            quote_currency = None

            if symbol_pair.endswith("IRT"):
                base_symbol = symbol_pair[:-3]
                quote_currency = "IRT"
            elif symbol_pair.endswith("USDT") and symbol_pair != "USDT":
                base_symbol = symbol_pair[:-4]
                quote_currency = "USDT"
            else:
                continue # Skip if not ending with IRT or USDT (and not USDT itself)

            if not base_symbol:
                continue # Should not happen if logic above is correct, but as a safeguard
            
            info = crypto_cache.get_crypto_info(base_symbol)

            # TARGETED LOGGING FOR USDTIRT
            if symbol_pair == "USDTIRT":
                logger.info(f"[USDTIRT_DEBUG] Processing symbol_pair: {symbol_pair}")
                logger.info(f"[USDTIRT_DEBUG]   Base symbol: {base_symbol}, Quote: {quote_currency}")
                logger.info(f"[USDTIRT_DEBUG]   Info for {base_symbol}: {info}")

            # Generate appropriate triggers for this symbol
            triggers = []
            # Add base symbol and name
            triggers.append(base_symbol)
            if info.get('name'):
                triggers.append(info.get('name'))
                triggers.append(f"قیمت {info.get('name')}")  # قیمت NAME
                triggers.append(f"نرخ {info.get('name')}")   # نرخ NAME
            
            # Add pair-specific triggers
            if quote_currency == "IRT":
                triggers.append(f"{base_symbol}IRT")
                triggers.append(f"{base_symbol}/IRT")
                triggers.append(f"{base_symbol} IRT")
                if info.get('name'):
                    triggers.append(f"{info.get('name')} تومان")  # NAME تومان
                    triggers.append(f"{info.get('name')} به تومان")  # NAME به تومان
            elif quote_currency == "USDT":
                triggers.append(f"{base_symbol}USDT")
                triggers.append(f"{base_symbol}/USDT")
                triggers.append(f"{base_symbol} USDT")
                if info.get('name'):
                    triggers.append(f"{info.get('name')} دلار")  # NAME دلار
                    triggers.append(f"{info.get('name')} به دلار")  # NAME به دلار

            # Create the handler with the correct number of parameters
            handler_instance = CryptoHandler(
                symbol=symbol_pair,
                name=info.get('name', base_symbol),
                icon=info.get('icon', ''),
                triggers=triggers
            )
            
            if symbol_pair == "USDTIRT":
                logger.info(f"[USDTIRT_DEBUG]   Generated triggers for {symbol_pair}: {triggers}")

            # Now register handlers for each trigger
            for trigger_word in triggers:
                if not trigger_word: # Skip empty trigger words
                    continue

                # Regex to capture optional amount before or after the trigger word
                # Allows for Persian and English numbers, dots, commas, and spaces for the amount
                pattern_regex = rf"^(?:([۰-۹\d\.,\s]+)\s*)?{re.escape(trigger_word)}(?:\s*([۰-۹\d\.,\s]+))?$"
                
                if symbol_pair == "USDTIRT":
                    logger.info(f"[USDTIRT_DEBUG]     Registering trigger: '{trigger_word}' with pattern: {pattern_regex}")

                # Define a specific handler for this trigger to capture the correct handler_instance and trigger_word
                async def specific_handler(event, current_handler=handler_instance, current_trigger=trigger_word):
                    match = event.pattern_match
                    amount_str_before = match.group(1)
                    amount_str_after = match.group(2)
                    
                    amount_str = None
                    if amount_str_before and amount_str_before.strip():
                        amount_str = amount_str_before.strip()
                    elif amount_str_after and amount_str_after.strip():
                        amount_str = amount_str_after.strip()

                    await current_handler.handle_crypto(event, client, amount_str=amount_str)
                    raise events.StopPropagation # Prevent other handlers from processing this event

                client.add_event_handler(specific_handler, events.NewMessage(pattern=re.compile(pattern_regex, re.IGNORECASE)))
        
        logger.info(f"Successfully registered crypto handlers.")
    except Exception as e:
        logger.error(f"Error during crypto handler registration: {e}", exc_info=True)
        pass # Non-functional change to potentially satisfy linter

def initialize_crypto_plugin(client):
    """Initializes the crypto plugin by registering handlers and starting cache."""
    # Start the crypto cache
    crypto_cache.start()
    
    # Register all crypto handlers
    register_crypto_handlers(client)
    
    # Register the crypto list command
    client.add_event_handler(
        lambda e: show_crypto_list(e, client),
        events.NewMessage(pattern=r'^/crypto$')
    )
    
    # Register button handler for crypto selections
    client.add_event_handler(
        lambda e: handle_crypto_button(e, client),
        events.CallbackQuery(pattern=r'^crypto_')
    )
    
    # Note: The cmd_crypto button is already registered in main.py
    
    # Register handler for USDT price
    client.add_event_handler(
        lambda e: handle_usdt_price(e, client),
        events.NewMessage(pattern=r'(?i)^(usdt|تتر|تتر به تومان|قیمت تتر|نرخ تتر)$')
    )
    
    logger.info("Crypto plugin initialized successfully")

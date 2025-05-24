"""
پنل مدیریت
مدیریت دستورات ادمین، ارسال پیام همگانی و آمار ربات
"""

import asyncio
import logging
import time
from typing import List, Optional
from telethon import events, Button

# Set up logging
logger = logging.getLogger(__name__)

class AdminPanel:
    def __init__(self, client, user_db, admin_ids: List[int]):
        """Initialize the admin panel
        
        Args:
            client: The Telegram client instance
            user_db: The user database instance
            admin_ids: List of admin user IDs
        """
        self.client = client
        self.user_db = user_db
        self.admin_ids = admin_ids
        self.broadcast_in_progress = False
        self.register_handlers()
        logger.info("Admin panel initialized")
    
    def is_admin(self, user_id: int) -> bool:
        """Check if a user is an admin"""
        return user_id in self.admin_ids
    
    def register_handlers(self):
        """Register admin command handlers"""
        
        @self.client.on(events.NewMessage(pattern=r'^/admin$'))
        async def admin_command(event):
            """Handle /admin command"""
            if not self.is_admin(event.sender_id):
                await event.respond("❌ شما مجوز دسترسی به پنل مدیریت را ندارید.")
                return
            
            buttons = [
                [Button.inline("📊 آمار", b"admin:stats")],
                [Button.inline("📢 ارسال همگانی", b"admin:broadcast")],
                [Button.inline("👥 اطلاعات کاربر", b"admin:user_info")]
            ]
            await event.respond("👨‍💼 **پنل مدیریت**\n\nیک گزینه را انتخاب کنید:", buttons=buttons)
        
        @self.client.on(events.CallbackQuery(data=b"admin:stats"))
        async def show_stats(event):
            """Show bot statistics"""
            if not self.is_admin(event.sender_id):
                await event.answer("❌ Access denied", alert=True)
                return
                
            try:
                # Get user stats from database
                cursor = self.user_db.conn.cursor()
                
                # Total users
                cursor.execute("SELECT COUNT(*) FROM users")
                total_users = cursor.fetchone()[0]
                
                # Active users (last 30 days)
                cursor.execute("""
                    SELECT COUNT(DISTINCT user_id) 
                    FROM user_stats 
                    WHERE timestamp > ?
                """, (int(time.time()) - 30 * 24 * 60 * 60,))
                active_users = cursor.fetchone()[0]
                
                # Messages per day (last 7 days)
                cursor.execute("""
                    SELECT 
                        date(datetime(timestamp, 'unixepoch')) as day,
                        COUNT(*) as count
                    FROM user_stats
                    WHERE timestamp > ?
                    GROUP BY day
                    ORDER BY day DESC
                    LIMIT 7
                """, (int(time.time()) - 7 * 24 * 60 * 60,))
                messages_data = cursor.fetchall()
                
                # Format stats message
                stats_message = (
                    "📊 **آمار ربات**\n\n"
                    f"👥 تعداد کل کاربران: `{total_users:,}`\n"
                    f"🟢 کاربران فعال (30 روز اخیر): `{active_users:,}`\n\n"
                    "📈 پیام‌های ارسالی (7 روز اخیر):\n"
                )
                
                for day, count in messages_data:
                    stats_message += f"• {day}: `{count:,}` پیام\n"
                
                # Add back button
                buttons = [
                    [Button.inline("🔙 بازگشت", b"admin:back")]
                ]
                
                await event.edit(stats_message, buttons=buttons)
                
            except Exception as e:
                logger.error(f"Error getting stats: {str(e)}")
                await event.answer("❌ خطا در دریافت آمار", alert=True)
        
        @self.client.on(events.CallbackQuery(data=b"admin:broadcast"))
        async def start_broadcast(event):
            """Start broadcast flow"""
            if not self.is_admin(event.sender_id):
                await event.answer("❌ Access denied", alert=True)
                return
                
            if self.broadcast_in_progress:
                await event.answer("⚠️ در حال حاضر یک ارسال همگانی در حال انجام است", alert=True)
                return
                
            await event.edit(
                "📢 **پیامی که می‌خواهید به صورت همگانی ارسال کنید را ارسال کنید**\n\n"
                "می‌توانید از قالب‌بندی مارک‌داون استفاده کنید. برای انصراف /cancel ارسال کنید.",
                buttons=[[Button.inline("🔙 انصراف", b"admin:back")]]
            )
            
            # Store that we're waiting for a broadcast message
            self.broadcast_in_progress = True
            self.broadcast_sender = event.sender_id
            
            @self.client.on(events.NewMessage(from_users=self.admin_ids))
            async def handle_broadcast_message(broadcast_event):
                if broadcast_event.raw_text == '/cancel':
                    self.broadcast_in_progress = False
                    await broadcast_event.respond("❌ ارسال همگانی لغو شد")
                    return
                    
                # Remove this handler to prevent multiple triggers
                self.client.remove_event_handler(handle_broadcast_message)
                self.broadcast_in_progress = False
                
                # Get all user IDs
                cursor = self.user_db.conn.cursor()
                cursor.execute("SELECT user_id FROM users")
                user_ids = [row[0] for row in cursor.fetchall()]
                
                total_users = len(user_ids)
                success = 0
                failed = 0
                
                # Send the broadcast
                await event.edit(f"📢 در حال ارسال به {total_users} کاربر...")
                
                for user_id in user_ids:
                    try:
                        await self.client.send_message(user_id, broadcast_event.message)
                        success += 1
                        # Small delay to avoid hitting rate limits
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        logger.error(f"Failed to send to {user_id}: {str(e)}")
                        failed += 1
                
                # Send summary
                summary = (
                    f"✅ **ارسال همگانی تکمیل شد**\n\n"
                    f"📤 ارسال موفق: `{success:,}`\n"
                    f"❌ ناموفق: `{failed:,}`\n"
                    f"📊 درصد موفقیت: `{(success/max(1, total_users)*100):.1f}%`"
                )
                await event.respond(summary)
        
        @self.client.on(events.CallbackQuery(data=b"admin:user_info"))
        async def user_info_prompt(event):
            """Prompt for user ID to get info"""
            if not self.is_admin(event.sender_id):
                await event.answer("❌ Access denied", alert=True)
                return
                
            await event.edit(
                "👤 **اطلاعات کاربر**\n\n"
                "لطفاً آیدی عددی یا یوزرنیم کاربر را ارسال کنید.",
                buttons=[[Button.inline("🔙 بازگشت", b"admin:back")]]
            )
            
            @self.client.on(events.NewMessage(from_users=event.sender_id))
            async def handle_user_info_query(user_event):
                if user_event.raw_text == '/cancel':
                    await user_event.respond("❌ عملیات لغو شد")
                    self.client.remove_event_handler(handle_user_info_query)
                    return
                    
                user_input = user_event.raw_text.strip()
                
                # Remove @ if present
                if user_input.startswith('@'):
                    user_input = user_input[1:]
                
                try:
                    # Try to get user by ID
                    user_id = int(user_input)
                    cursor = self.user_db.conn.cursor()
                    cursor.execute("""
                        SELECT * FROM users 
                        WHERE user_id = ?
                    """, (user_id,))
                    user_data = cursor.fetchone()
                except ValueError:
                    # Try to get user by username
                    cursor = self.user_db.conn.cursor()
                    cursor.execute("""
                        SELECT * FROM users 
                        WHERE username = ?
                    """, (user_input.lower(),))
                    user_data = cursor.fetchone()
                
                if not user_data:
                    await user_event.respond("❌ کاربر یافت نشد")
                    self.client.remove_event_handler(handle_user_info_query)
                    return
                
                # Get user stats
                cursor.execute("""
                    SELECT action, COUNT(*) as count, MAX(timestamp) as last_seen
                    FROM user_stats
                    WHERE user_id = ?
                    GROUP BY action
                """, (user_data[0],))
                stats = cursor.fetchall()
                
                # Format user info
                user_info = (
                    f"👤 **اطلاعات کاربر**\n\n"
                    f"🆔 شناسه: `{user_data[0]}`\n"
                    f"👤 نام: {user_data[2] or 'ندارد'}"
                    f"{(' ' + user_data[3]) if user_data[3] else ''}\n"
                    f"🔗 نام کاربری: @{user_data[1] or 'ندارد'}\n"
                    f"🤖 ربات: {'✅' if user_data[4] else '❌'}\n"
                    f"🌐 زبان: {user_data[5] or 'ندارد'}\n"
                    f"📅 اولین بازدید: <code>{self._format_timestamp(user_data[6])}</code>\n"
                    f"🕒 آخرین بازدید: <code>{self._format_timestamp(user_data[7])}</code>\n"
                    f"🔢 تعداد تعاملات: `{user_data[8]:,}`\n\n"
                    "📊 **آمار فعالیت**\n"
                )
                
                for action, count, last_seen in stats:
                    action_fa = {
                        'start': 'شروع',
                        'message': 'پیام',
                        'callback': 'کلیک دکمه',
                        'inline_query': 'جستجوی اینلاین'
                    }.get(action, action)
                    user_info += f"• {action_fa}: `{count:,}` (آخرین: {self._format_timestamp(last_seen)})\n"
                
                await user_event.respond(user_info, parse_mode='html')
                self.client.remove_event_handler(handle_user_info_query)
        
        @self.client.on(events.CallbackQuery(data=b"admin:back"))
        async def back_to_admin(event):
            """Return to admin main menu"""
            if not self.is_admin(event.sender_id):
                await event.answer("❌ Access denied", alert=True)
                return
                
            buttons = [
                [Button.inline("📊 آمار", b"admin:stats")],
                [Button.inline("📢 ارسال همگانی", b"admin:broadcast")],
                [Button.inline("👥 اطلاعات کاربر", b"admin:user_info")]
            ]
            await event.edit("👨‍💼 **پنل مدیریت**\n\nیک گزینه را انتخاب کنید:", buttons=buttons)
    
    @staticmethod
    def _format_timestamp(timestamp: int) -> str:
        """Format a Unix timestamp to a readable date"""
        from datetime import datetime, timezone, timedelta
        if not timestamp:
            return "هرگز"
        
        # Convert to Tehran timezone (UTC+3:30)
        tehran_tz = timezone(timedelta(hours=3, minutes=30))
        dt = datetime.utcfromtimestamp(timestamp).replace(tzinfo=timezone.utc).astimezone(tehran_tz)
        
        # Format with Persian numbers
        persian_digits = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
        return dt.strftime('%Y-%m-%d %H:%M:%S').translate(persian_digits) + ' IRST'

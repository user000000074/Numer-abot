import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import asyncio

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

class MediaServiceBot:
    def __init__(self):
        # التوكن مباشرة بدلاً من os.getenv
        self.token = "8485376998:AAFKQifErEDv4-g-IdRY3hoptD-jcCj3n2M"
        self.lion_api_key = "8w963myi1eCDm5jHxl"
        
        self.required_channels = ['@nhkfjj']
        
        self.services = {
            '1': {'name': 'متابعين تيك توك', 'id': '121', 'price': '5$ لكل 1000'},
            '2': {'name': 'مشاهدات يوتيوب', 'id': '132', 'price': '3$ لكل 1000'},
            '3': {'name': 'متابعين انستجرام', 'id': '145', 'price': '7$ لكل 1000'},
        }

    async def check_subscription(self, user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
        try:
            for channel in self.required_channels:
                member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
                if member.status in ['left', 'kicked']:
                    return False
            return True
        except Exception as e:
            logging.error(f"Error checking subscription: {e}")
            return False

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        if not await self.check_subscription(user_id, context):
            await update.message.reply_text(
                "📢 **مرحباً! للاستفادة من خدماتنا، يرجى الاشتراك في قناتنا أولاً:**\n\n"
                "• @nhkfjj\n\n"
                "✅ بعد الاشتراك في القناة، أرسل /start مرة أخرى\n\n"
                "🔗 رابط القناة: https://t.me/nhkfjj",
                parse_mode='Markdown'
            )
            return
        
        services_text = "\n".join([f"{key}. {value['name']} - {value['price']}" for key, value in self.services.items()])
        
        await update.message.reply_text(
            f"🎉 **مرحباً! تم التحقق من اشتراكك**\n\n"
            f"📋 **الخدمات المتاحة:**\n{services_text}\n\n"
            f"📝 **كيفية الطلب:**\n"
            f"أرسل رقم الخدمة + الرابط\n"
            f"مثال: `1 https://tiktok.com/@username`",
            parse_mode='Markdown'
        )

    async def handle_service_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user_message = update.message.text
        
        if not await self.check_subscription(user_id, context):
            await update.message.reply_text("❌ **يرجى الاشتراك في قناتنا أولاً**")
            return
        
        try:
            parts = user_message.split()
            if len(parts) < 2:
                await update.message.reply_text("❌ **صيغة خاطئة**\nمثال: `1 https://tiktok.com/@username`")
                return
            
            service_key = parts[0]
            target_link = parts[1]
            
            if service_key not in self.services:
                await update.message.reply_text("❌ **رقم خدمة غير صحيح**")
                return
            
            service = self.services[service_key]
            await update.message.reply_text("⏳ **جاري معالجة طلبك...**")
            
            await asyncio.sleep(2)
            await update.message.reply_text(
                f"✅ **تم استلام طلبك بنجاح!**\n\n"
                f"📦 الخدمة: {service['name']}\n"
                f"🔗 الرابط: {target_link}\n"
                f"🧮 الكمية: 1000\n\n"
                f"شكراً لثقتك! 🌟"
            )
                
        except Exception as e:
            logging.error(f"Error: {e}")
            await update.message.reply_text("❌ **حدث خطأ**")

    def run(self):
        application = Application.builder().token(self.token).build()
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_service_request))
        
        logging.info("Bot is starting...")
        application.run_polling()

if __name__ == '__main__':
    bot = MediaServiceBot()
    bot.run()

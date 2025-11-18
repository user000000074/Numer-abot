import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

# إعداد التسجيل
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

class MediaServiceBot:
    def __init__(self):
        self.token = os.getenv('BOT_TOKEN')
        self.lion_api_key = os.getenv('LION_API_KEY')
        
        # القناة المطلوبة للاشتراك (قناتك الجديدة)
        self.required_channels = ['@nhkfjj']
        
        # خدمات tg-lion
        self.services = {
            '1': {'name': 'متابعين تيك توك', 'id': '121', 'price': '5$ لكل 1000'},
            '2': {'name': 'مشاهدات يوتيوب', 'id': '132', 'price': '3$ لكل 1000'},
            '3': {'name': 'متابعين انستجرام', 'id': '145', 'price': '7$ لكل 1000'},
            '4': {'name': 'مشاهدات تيك توك', 'id': '125', 'price': '2$ لكل 1000'},
            '5': {'name': 'لايكات انستجرام', 'id': '148', 'price': '4$ لكل 1000'}
        }

    async def check_subscription(self, user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """التحقق من اشتراك المستخدم في القناة"""
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
        """رسالة الترحيب والتحقق من الاشتراك"""
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
        
        # إذا كان مشتركاً، عرض القائمة
        services_text = "\n".join([f"{key}. {value['name']} - {value['price']}" for key, value in self.services.items()])
        
        await update.message.reply_text(
            f"🎉 **مرحباً! تم التحقق من اشتراكك**\n\n"
            f"📋 **الخدمات المتاحة:**\n{services_text}\n\n"
            f"📝 **كيفية الطلب:**\n"
            f"أرسل رقم الخدمة + الرابط\n"
            f"مثال: `1 https://tiktok.com/@username`\n\n"
            f"⚡ **خدمة سريعة ومضمونة**",
            parse_mode='Markdown'
        )

    async def handle_service_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة طلبات الخدمات"""
        user_id = update.effective_user.id
        user_message = update.message.text
        
        # التحقق من الاشتراك أولاً
        if not await self.check_subscription(user_id, context):
            await update.message.reply_text(
                "❌ **يرجى الاشتراك في قناتنا أولاً**\n"
                "🔗 https://t.me/nhkfjj\n\n"
                "بعد الاشتراك أرسل /start"
            )
            return
        
        try:
            # تحليل الرسالة (رقم الخدمة + الرابط)
            parts = user_message.split()
            if len(parts) < 2:
                await update.message.reply_text(
                    "❌ **صيغة خاطئة**\n\n"
                    "📋 الطريقة الصحيحة:\n"
                    "`رقم الخدمة + الرابط`\n\n"
                    "مثال: `1 https://tiktok.com/@username`\n"
                    "مثال: `2 https://youtube.com/c/ChannelName`"
                )
                return
            
            service_key = parts[0]
            target_link = parts[1]
            
            if service_key not in self.services:
                await update.message.reply_text(
                    "❌ **رقم خدمة غير صحيح**\n\n"
                    "📋 الخدمات المتاحة:\n"
                    + "\n".join([f"{key}. {value['name']}" for key, value in self.services.items()])
                )
                return
            
            service = self.services[service_key]
            
            # إرسال طلب لـ tg-lion
            await update.message.reply_text("⏳ **جاري معالجة طلبك...**")
            order_result = self.send_to_lion_api(service['id'], target_link, 1000)
            
            if order_result and order_result.get('status') == 'success':
                await update.message.reply_text(
                    f"✅ **تم استلام طلبك بنجاح!**\n\n"
                    f"📦 الخدمة: {service['name']}\n"
                    f"🔗 الرابط: {target_link}\n"
                    f"🧮 الكمية: 1000\n"
                    f"⏳ جاري التجهيز...\n\n"
                    f"شكراً لثقتك! 🌟\n"
                    f"تابع جديدنا في: @nhkfjj"
                )
            else:
                await update.message.reply_text(
                    "❌ **حدث خطأ في النظام**\n"
                    "يرجى المحاولة لاحقاً أو التواصل مع الدعم"
                )
                
        except Exception as e:
            logging.error(f"Error processing order: {e}")
            await update.message.reply_text("❌ **حدث خطأ، يرجى المحاولة مرة أخرى**")

    def send_to_lion_api(self, service_id: str, target_link: str, quantity: int):
        """إرسال الطلب لـ tg-lion API"""
        try:
            # محاكاة API - سنعدلها عندما نجرب API الحقيقي
            logging.info(f"Sending order to Lion: Service {service_id}, Link {target_link}")
            
            # هنا نضع كود API الحقيقي عندما نختبره
            return {'status': 'success', 'order_id': '12345'}
            
        except Exception as e:
            logging.error(f"API Error: {e}")
            return {'status': 'error'}

    def run(self):
        """تشغيل البوت"""
        application = Application.builder().token(self.token).build()
        
        # إضافة handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_service_request))
        
        # بدء البوت
        logging.info("Bot is starting...")
        application.run_polling()

if __name__ == '__main__':
    bot = MediaServiceBot()
    bot.run()

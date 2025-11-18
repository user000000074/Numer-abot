import logging
import requests
from flask import Flask
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# إعداد التسجيل
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

app = Flask(__name__)

class TGLionBot:
    def __init__(self):
        self.token = "8485376998:AAFKQifErEDv4-g-IdRY3hoptD-jcCj3n2M"
        self.lion_api_key = "8w963myi1eCDm5jHxl"
        self.api_url = "https://tg-lion.net/api/v1"
        
        self.required_channels = ['@nhkfjj']
        
        # خدمات TG-Lion الحقيقية
        self.services = {
            '1': {'name': 'حسابات تليجرام', 'category': 'accounts'},
            '2': {'name': 'أرقام هاتف', 'category': 'phones'}, 
            '3': {'name': 'خدمات سوشيال ميديا', 'category': 'social'},
            '4': {'name': 'بوتات تليجرام', 'category': 'bots'},
            '5': {'name': 'قنوات تليجرام', 'category': 'channels'}
        }

    def get_services_list(self):
        """جلب قائمة الخدمات من TG-Lion API"""
        try:
            response = requests.get(f"{self.api_url}/services", headers={
                "Authorization": f"Bearer {self.lion_api_key}"
            })
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logging.error(f"API Error: {e}")
            return None

    def create_order(self, service_id, quantity=1):
        """إنشاء طلب جديد"""
        try:
            data = {
                "service": service_id,
                "quantity": quantity
            }
            response = requests.post(f"{self.api_url}/order", 
                                   json=data,
                                   headers={"Authorization": f"Bearer {self.lion_api_key}"})
            return response.json()
        except Exception as e:
            logging.error(f"Order Error: {e}")
            return None

    def check_subscription(self, user_id: int, context: CallbackContext) -> bool:
        """التحقق من الاشتراك في القناة"""
        try:
            for channel in self.required_channels:
                try:
                    member = context.bot.get_chat_member(chat_id=channel, user_id=user_id)
                    if member.status in ['left', 'kicked']:
                        return False
                except Exception as e:
                    logging.error(f"Channel check error: {e}")
                    return False
            return True
        except Exception as e:
            logging.error(f"Subscription error: {e}")
            return False

    def start(self, update: Update, context: CallbackContext):
        """رسالة البدء"""
        user_id = update.effective_user.id
        
        if not self.check_subscription(user_id, context):
            update.message.reply_text(
                "🦁 **مرحباً في TG-Lion Bot**\n\n"
                "📢 للاستفادة من خدماتنا، يرجى الاشتراك في قناتنا أولاً:\n"
                "• @nhkfjj\n\n"
                "✅ بعد الاشتراك أرسل /start مرة أخرى\n"
                "🔗 https://t.me/nhkfjj"
            )
            return

        services_text = "\n".join([f"{key}. {value['name']}" for key, value in self.services.items()])
        
        update.message.reply_text(
            f"🎉 **مرحباً في TG-Lion!**\n\n"
            f"🛍️ **الخدمات المتاحة:**\n{services_text}\n\n"
            f"📝 **كيفية الطلب:**\n"
            f"أرسل رقم الخدمة\n"
            f"مثال: `1`\n\n"
            f"💼 **خدمات حصرية:**\n"
            f"• حسابات تليجرام\n"
            f"• أرقام هاتف\n" 
            f"• بوتات وقنوات\n"
            f"• خدمات سوشيال ميديا"
        )

    def handle_service_selection(self, update: Update, context: CallbackContext):
        """معالجة اختيار الخدمة"""
        user_id = update.effective_user.id
        user_message = update.message.text
        
        if not self.check_subscription(user_id, context):
            update.message.reply_text("❌ **يرجى الاشتراك في القناة أولاً**")
            return
        
        if user_message in self.services:
            service = self.services[user_message]
            
            # جلب الخدمات الحقيقية من API
            available_services = self.get_services_list()
            
            if available_services:
                services_list = "\n".join([f"• {s['name']} - ${s['price']}" for s in available_services[:5]])
                update.message.reply_text(
                    f"📦 **{service['name']} - الخدمات المتاحة:**\n\n"
                    f"{services_list}\n\n"
                    f"🔢 أرسل رقم الخدمة المطلوبة"
                )
            else:
                update.message.reply_text(
                    f"🛒 **{service['name']}**\n\n"
                    f"⏳ جاري جلب الخدمات المتاحة...\n"
                    f"📞 للطلبات السريعة تواصل مع الدعم"
                )
        else:
            update.message.reply_text("❌ **رقم خدمة غير صحيح**")

    def run_bot(self):
        """تشغيل البوت"""
        updater = Updater(self.token, use_context=True)
        dispatcher = updater.dispatcher
        
        dispatcher.add_handler(CommandHandler("start", self.start))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_service_selection))
        
        logging.info("🦁 TG-Lion Bot is starting...")
        updater.start_polling()
        return updater

# تشغيل البوت
if __name__ == '__main__':
    bot = TGLionBot()
    bot.run_bot()

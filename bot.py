import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

class SimpleBot:
    def __init__(self):
        self.token = "8485376998:AAFKQifErEDv4-g-IdRY3hoptD-jcCj3n2M"
        self.required_channels = ['@nhkfjj']

    def start(self, update: Update, context: CallbackContext):
        update.message.reply_text(
            "🎉 **مرحباً! البوت يعمل الآن**\n\n"
            "📢 قناتنا: @nhkfjj\n\n"
            "✅ البوت جاهز للاستخدام!"
        )

    def run(self):
        updater = Updater(self.token, use_context=True)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", self.start))
        
        logging.info("✅ البوت يعمل بنجاح!")
        updater.start_polling()
        updater.idle()

if __name__ == '__main__':
    bot = SimpleBot()
    bot.run()

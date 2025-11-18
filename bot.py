import telebot
import logging

logging.basicConfig(level=logging.INFO)

# التوكن مباشرة
TOKEN = "8485376998:AAFKQifErEDv4-g-IdRY3hoptD-jcCj3n2M"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎉 **البوت يعمل بنجاح!**\n\n📢 قناتنا: @nhkfjj")

if __name__ == '__main__':
    logging.info("✅ البوت يعمل!")
    bot.polling()

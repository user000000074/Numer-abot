from flask import Flask
from bot import TGLionBot
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "🦁 TG-Lion Bot is Running!"

def run_bot():
    bot = TGLionBot()
    bot.run_bot()

if __name__ == '__main__':
    # تشغيل البوت في thread منفصل
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # تشغيل Flask
    app.run(host='0.0.0.0', port=5000)

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import re
from bs4 import BeautifulSoup
from Crypto.Cipher import AES

BOT_TOKEN = "8727109230:AAETzwkJNqKQbNRf3xihJocWrXNqyVLb_kI"
bot = telebot.TeleBot(BOT_TOKEN)

API_URL = "https://asmodeus.free.nf/index.php"

session = requests.Session()
session.headers.update({
    'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36"
})


def solve_cookie_challenge():
    try:
        r = session.get(API_URL, timeout=30)
        matches = re.findall(r'toNumbers\("([a-f0-9]+)"\)', r.text)
        if len(matches) >= 3:
            a = bytes.fromhex(matches[0])
            b = bytes.fromhex(matches[1])
            c = bytes.fromhex(matches[2])
            cipher = AES.new(a, AES.MODE_CBC, b)
            cookie_val = cipher.decrypt(c).hex()
            session.cookies.set('__test', cookie_val, domain='asmodeus.free.nf', path='/')
            session.get(API_URL + "?i=1", timeout=30)
            return True
    except:
        pass
    return False


solve_cookie_challenge()


def get_developer_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("👨‍💻 المطور", url="https://t.me/priknm"))
    return markup


def get_ai_response(message_text):
    payload = {
        'model': "V3.2",
        'msg': message_text
    }
    try:
        response = session.post(API_URL, data=payload, timeout=60)
        soup = BeautifulSoup(response.text, 'html.parser')
        pre = soup.find('pre')
        if pre:
            return pre.get_text()

        if 'slowAES' in response.text:
            if solve_cookie_challenge():
                response = session.post(API_URL, data=payload, timeout=60)
                soup = BeautifulSoup(response.text, 'html.parser')
                pre = soup.find('pre')
                if pre:
                    return pre.get_text()

        return "⚠️ لم يتم الحصول على رد من الذكاء الاصطناعي."
    except requests.exceptions.Timeout:
        return "⏳ انتهت مهلة الاتصال، حاول مرة أخرى."
    except Exception as e:
        return f"❌ حدث خطأ: {str(e)}"


@bot.message_handler(commands=['start'])
def start_command(message):
    welcome_text = (
        "🤖 *مرحباً بك في بوت DeepSeek AI!*\n\n"
        "أنا بوت ذكاء اصطناعي يعمل بنموذج *DeepSeek V3.2*\n\n"
        "📝 أرسل لي أي رسالة وسأرد عليك!\n"
        "━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_developer_button()
    )


@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "📖 *كيفية الاستخدام:*\n\n"
        "• أرسل أي رسالة نصية وسيرد عليك الذكاء الاصطناعي\n"
        "• /start - بدء البوت\n"
        "• /help - عرض المساعدة\n"
        "━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.send_message(
        message.chat.id,
        help_text,
        parse_mode="Markdown",
        reply_markup=get_developer_button()
    )


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    waiting_msg = bot.send_message(
        message.chat.id,
        "⏳ *جاري التفكير...*",
        parse_mode="Markdown"
    )

    ai_response = get_ai_response(message.text)

    bot.delete_message(message.chat.id, waiting_msg.message_id)

    bot.send_message(
        message.chat.id,
        f"🤖 *DeepSeek AI:*\n\n{ai_response}",
        parse_mode="Markdown",
        reply_markup=get_developer_button()
    )


print("✅ Run")
bot.infinity_polling()

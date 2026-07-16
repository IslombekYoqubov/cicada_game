import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

API_TOKEN = '8603411482:AAEbrMH1Tjeykbsn_F2UAsb4mt5qMHeckNy'
CHANNEL_ID = '@cicada_vibe'

logging.basicConfig(level=logging.INFO)

# Serverlarda proxy talab qilinmaydi, to'g'ridan-to'g'ri ulanadi
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Kanaldagi a'zolik holatini tekshirish
async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'creator', 'administrator']
    except Exception as e:
        logging.error(f"A'zolikni tekshirishda xato: {e}")
        return False

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    is_sub = await check_subscription(user_id)
    
    if is_sub:
        await send_puzzle(message.chat.id)
    else:
        keyboard = InlineKeyboardMarkup(row_width=1)
        btn_channel = InlineKeyboardButton(text="📢 Kanalga ulanish", url=f"https://t.me/{CHANNEL_ID[1:]}")
        btn_check = InlineKeyboardButton(text="🔄 A'zolikni tekshirish", callback_data="check_sub")
        keyboard.add(btn_channel, btn_check)
        
        await message.answer(
            "Xush kelibsiz! Tizimga kirish tasdiqlandi. 🔓\n\n"
            "Biroq, keyingi bosqich signalini qabul qilish uchun avval rasmiy kanalimizga a'zo bo'lishingiz kerak:",
            reply_markup=keyboard
        )

@dp.callback_query_handler(text="check_sub")
async def process_callback_check(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    is_sub = await check_subscription(user_id)
    
    if is_sub:
        await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
        await send_puzzle(user_id)
    else:
        await bot.answer_callback_query(callback_query.id, "Siz hali kanalga a'zo bo'lmadingiz! ❌", show_alert=True)

async def send_puzzle(chat_id):
    puzzle_text = (
        "📟 **2-BOSQICH SIGNALI QABUL QILINDI**\n\n"
        "Quyidagi shifrlangan kosmik signalni tarjima qiling va kalit so'zni botga yuboring:\n\n"
        "`...   ---   .--.   ....   ..   .-`\n\n"
        "💡 *Yordam:* Har bir harf orasida bo'sh joy qoldirilgan. Kalit so'zni katta harflarda kiriting."
    )
    await bot.send_message(chat_id, puzzle_text, parse_mode="Markdown")

@dp.message_handler()
async def check_answer(message: types.Message):
    user_answer = message.text.strip().upper()
    
    if user_answer == "SOPHIA":
        await message.reply(
            "🎉 **MUVOFAQQIYATLI YECHILDI!**\n\n"
            "Siz signalni to'g'ri dekodladingiz. Tizim sizga 3-bosqich kalitini taqdim etadi:\n"
            "Keyingi bosqich tez orada boshlanadi. Kanallarni kuzatib boring!"
        )
    else:
        await message.reply("❌ Signal noto'g'ri dekodlandi. Qayta urinib ko'ring.")

# Platformalar (Zeabur/Render) uxlab qolmasligi uchun port eshituvchi qism
async def handle(request):
    return web.Response(text="Cicada Bot is online and active!")

app = web.Application()
app.router.add_get('/', handle)

async def main():
    # Platforma beradigan portni oladi yoki standart 8000 dan foydalanadi
    port = int(os.environ.get("PORT", 8000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Dummy server started on port {port}")
    
    try:
        await dp.start_polling()
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

API_TOKEN = '8603411482:AAEbRMH1TjeykbSn_F2UAsb4mt5qMHeCknY'
CHANNEL_ID = '@cicada_vibe'

# 🌐 Tashqi saytingiz havolasi
WEBSITE_URL = 'https://youtube.com/miyagi' 

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Foydalanuvchilar qaysi bosqichdaligini eslab qolish uchun kesh
user_stages = {}

async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'creator', 'administrator']
    except Exception as e:
        logging.error(f"A'zolikni tekshirishda xato: {e}")
        return False

# /start buyrug'i kelganda foydalanuvchini har doim 0 dan boshlatamiz
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    
    # 🚨 MUHIM: Har doim start bosilganda bosqichni nollaymiz!
    user_stages[user_id] = "STAGE_1"
    
    is_sub = await check_subscription(user_id)
    
    if is_sub:
        await send_first_puzzle(message.chat.id)
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
        # 🚨 A'zolik tekshirilganda ham bosqich boshidan boshlanadi
        user_stages[user_id] = "STAGE_1"
        await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
        await send_first_puzzle(user_id)
    else:
        await bot.answer_callback_query(callback_query.id, "Siz hali kanalga a'zo bo'lmadingiz! ❌", show_alert=True)

# 1-Bosqich boshlanishi
async def send_first_puzzle(chat_id):
    puzzle_text = (
        "📟 1-BOSQICH: TOVUSH SHIFRI\n\n"
        "Kanaldagi (`@cicada_vibe`) ovozli xabar (audio) ortiga yashiringan maxfiy kodni toping va botga yuboring!\n\n"
        "💡 Yordam: Kalit so'zni katta harflarda kiriting."
    )
    await bot.send_message(chat_id, puzzle_text, parse_mode="Markdown")

# Xabarlarni qabul qilish va bosqichlarni tekshirish
@dp.message_handler()
async def game_router(message: types.Message):
    user_id = message.from_user.id
    user_answer = message.text.strip().upper()
    
    # Agar foydalanuvchi bazada hali yo'q bo'lsa, avtomatik 1-bosqichga o'rnatiladi
    if user_id not in user_stages:
        user_stages[user_id] = "STAGE_1"
        
    current_stage = user_stages[user_id]
    
    # --- 1-BOSQICH: OVOZLI XABAR TEKSHIRUVI ---
    if current_stage == "STAGE_1":
        if user_answer == "NULL":
            user_stages[user_id] = "STAGE_2" # 2-bosqichga o'tkazamiz
            
            # Telegram postidagi video havolasi
            puzzle_video_url = "https://t.me/demo11212/3" 
            
            await message.reply("🎉 Tabriklaymiz, keyingi bosqichga o'tdingiz! 🔓")
            
            # send_photo emas, send_video qildik, chunki bu video kvest!
            try:
                await bot.send_video(
                    chat_id=user_id,
                    video=puzzle_video_url,
                    caption=(
                        "📟 2-BOSQICH: VIDEO ORTIDAGI JUMBOQ\n\n"
                        "Ushbu video qaysi filmdan parcha ekanligini toping va kino nomini botga yuboring!\n\n"
                        "💡 Yordam: Diqqat bilan elementlarga qarang."
                    )
                )
            except Exception as e:
                # Agar video yuborishda havola xato bo'lsa, ogohlantirish va oddiy xabar yuborish
                logging.error(f"Video yuborishda xato: {e}")
                await message.answer(
                    f"{'https://www.youtube.com/shorts/Aj51buU3j-k'}"
                )
        else:
            await message.reply("❌ Xato! Video xabardagi kod noto'g'ri. Diqqat bilan eshitib ko'ring.")

    # --- 2-BOSQICH: RASMDAGI KOD TEKSHIRUVI ---
    elif current_stage == "STAGE_2":
        # Video ichidagi film nomi (Masalan: INCEPTION)
        if user_answer == "INCEPTION":
            user_stages[user_id] = "COMPLETED"
            
            # Saytga o'tish uchun chiroyli tugma
            keyboard = InlineKeyboardMarkup()
            btn_website = InlineKeyboardButton(text="🌐 Yakuniy topshiriqqa o'tish", url=WEBSITE_URL)
            keyboard.add(btn_website)
            
            await message.reply(
                "🎉 AJOYIB! Siz videodagi kodni ham to'g'ri topdingiz.\n\n"
                "Siz kvestning so'nggi va hal qiluvchi bosqichiga yetib keldingiz. "
                "Quyidagi tugma orqali maxfiy saytga o'ting va topshiriqni yakunlang:",
                reply_markup=keyboard
            )
        else:
            await message.reply("❌ Videodagi kod noto'g'ri. Yaxshilab tekshirib, qayta urinib ko'ring.")

# Dummy veb-server (Render uchun)
async def handle(request):
    return web.Response(text="Cicada Vibe Bot is live!")

app = web.Application()
app.router.add_get('/', handle)

async def main():
    port = int(os.environ.get("PORT", 8000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    try:
        await dp.start_polling()
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
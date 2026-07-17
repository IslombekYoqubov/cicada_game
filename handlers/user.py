import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import database as db_mod
from utils.logger import log_event

CHANNEL_ID = '@cicada_vibe'
WEBSITE_URL = 'https://final-level.netlify.app'

def register_user_handlers(dp: Dispatcher, bot: Bot):

    async def check_subscription(user_id):
        try:
            member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
            return member.status in ['member', 'creator', 'administrator']
        except Exception as e:
            logging.error(f"A'zolikni tekshirishda xato: {e}")
            return False

    async def send_first_puzzle(chat_id):
        puzzle_text = (
            "📟 **1-BOSQICH: TOVUSH SHIFRI**\n\n"
            "Kanaldagi (`@cicada_vibe`) ovozli xabar (audio) ortiga yashiringan maxfiy kodni toping va botga yuboring!\n\n"
            "💡 **Yordam:** Kalit so'zni KATTA harflarda kiriting."
        )
        await bot.send_message(chat_id, puzzle_text, parse_mode="Markdown")

    @dp.message_handler(commands=['start'])
    async def start_cmd(message: types.Message):
        user_id = message.from_user.id
        username = message.from_user.username
        
        await db_mod.register_or_update_user(user_id, username, "STAGE_1")
        await log_event(user_id, "START_BOT", "STAGE_1")
        await log_event(user_id, "ENTER_STAGE_1", "STAGE_1")
        
        is_sub = await check_subscription(user_id)
        if is_sub:
            await log_event(user_id, "JOIN_CHANNEL", "STAGE_1")
            await send_first_puzzle(message.chat.id)
        else:
            keyboard = InlineKeyboardMarkup(row_width=1)
            btn_channel = InlineKeyboardButton(text="📢 Kanalga ulanish", url=f"https://t.me/{CHANNEL_ID[1:]}")
            btn_check = InlineKeyboardButton(text="🔄 A'zolikni tekshirish", callback_data="check_sub")
            keyboard.add(btn_channel, btn_check)

            await message.answer(
                "Xush kelibsiz! Tizimga kirish tasdiqlandi. 🔓\n\n"
                "Keyingi bosqich signalini qabul qilish uchun avval rasmiy kanalimizga a'zo bo'lishingiz kerak:",
                reply_markup=keyboard
            )

    @dp.callback_query_handler(text="check_sub")
    async def process_callback_check(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        username = callback_query.from_user.username
        is_sub = await check_subscription(user_id)

        if is_sub:
            await db_mod.update_last_activity(user_id, username)
            await log_event(user_id, "JOIN_CHANNEL", "STAGE_1")
            await db_mod.set_user_stage(user_id, "STAGE_1")
            try:
                await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
            except Exception:
                pass
            await send_first_puzzle(user_id)
        else:
            await bot.answer_callback_query(callback_query.id, "Siz hali kanalga a'zo bo'lmadingiz! ❌", show_alert=True)

    @dp.message_handler()
    async def game_router(message: types.Message):
        user_id = message.from_user.id
        username = message.from_user.username
        user_answer = message.text.strip().upper()
        
        current_stage = await db_mod.get_user_stage(user_id)
        await db_mod.update_last_activity(user_id, username)

        if current_stage == "STAGE_1":
            if user_answer == "NULL":
                await db_mod.set_user_stage(user_id, "STAGE_2")
                await log_event(user_id, "PASS_STAGE_1", "STAGE_1")
                
                puzzle_video_url = "https://t.me/demo11212/4"
                await message.reply("🎉 Tabriklaymiz, keyingi bosqichga o'tdingiz! 🔓")
                try:
                    await bot.send_video(
                        chat_id=user_id, video=puzzle_video_url,
                        caption="📟 **2-BOSQICH: VIDEO ORTIDAGI JUMBOQ**\n\nUshbu video qaysi filmdan parcha ekanligini toping va kino nomini botga yuboring!\n\n💡 **Yordam:** Diqqat bilan kadrdagi va ovozdagi elementlarga qarang.",
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    logging.error(f"Video yuborishda xato: {e}")
                    await message.answer(f"📟 **2-BOSQICH: VIDEO ORTIDAGI JUMBOQ**\n\nVideo yuklanmadi, uni ushbu havola orqali ko'ring:\n{puzzle_video_url}\n\nKino nomini botga yuboring.")
            else:
                await message.reply("❌ Xato! Ovozli xabardagi kod noto'g'ri. Diqqat bilan eshitib ko'ring.")

        elif current_stage == "STAGE_2":
            valid_answers = ["INCEPTION", "MUQADDIMA", "НАЧАЛО"]
            if user_answer in valid_answers:
                await db_mod.set_user_stage(user_id, "COMPLETED")
                await log_event(user_id, "PASS_STAGE_2", "STAGE_2")
                await log_event(user_id, "COMPLETED", "COMPLETED")
                
                keyboard = InlineKeyboardMarkup()
                btn_website = InlineKeyboardButton(text="🌐 Yakuniy topshiriqqa o'tish", url=WEBSITE_URL)
                keyboard.add(btn_website)
                await message.reply(
                    "🎉 **AJOYIB!** Siz videodagi javobni to'g'ri topdingiz.\n\nSiz kvestning so'nggi va hal qiluvchi bosqichiga yetib keldingiz. Quyidagi tugma orqali maxfiy saytga o'ting va topshiriqni yakunlang:",
                    reply_markup=keyboard, parse_mode="Markdown"
                )
                await log_event(user_id, "OPEN_FINAL_SITE", "COMPLETED")
            else:
                await message.reply("❌ Film nomi noto'g'ri. Yaxshilab tekshirib, qayta urinib ko'ring.")
                
        elif current_stage == "COMPLETED":
            keyboard = InlineKeyboardMarkup()
            btn_website = InlineKeyboardButton(text="🌐 Saytga o'tish", url=WEBSITE_URL)
            keyboard.add(btn_website)
            await message.reply("Siz kvestni muvaffaqiyatli yakunlagansiz! 🏆\nYakuniy topshiriq saytda joylashgan:", reply_markup=keyboard)
            await log_event(user_id, "OPEN_FINAL_SITE", "COMPLETED")
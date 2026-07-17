from aiogram import Bot, Dispatcher, types
import analytics

ADMIN_ID = 5363456345  # 👈 BU YERGA O'ZINGNI TELEGRAM ID'NGNI YOZ !!!

def register_admin_handlers(dp: Dispatcher, bot: Bot):

    def is_admin(user_id: int):
        return user_id == ADMIN_ID

    @dp.message_handler(commands=['stats'])
    async def admin_stats(message: types.Message):
        if not is_admin(message.from_user.id):
            return

        gen_stats = await analytics.get_general_stats()
        today_events = await analytics.get_today_events_analytics()

        st_count = gen_stats["stages_count"]
        
        response = (
            "📊 **Quest Analytics**\n\n"
            f"👥 **Total Users:** {gen_stats['total_users']}\n"
            f"🟢 **Today Joined:** {gen_stats['today_joined']}\n"
            f"🔥 **Active Today:** {gen_stats['active_today']}\n"
            f"🏁 **Completed:** {gen_stats['completed']}\n\n"
            "📈 **Stage Analytics:**\n"
            f" ├ Stage 1 : {st_count.get('STAGE_1', 0)} user\n"
            f" ├ Stage 2 : {st_count.get('STAGE_2', 0)} user\n"
            f" └ Completed : {st_count.get('COMPLETED', 0)} user\n\n"
            f"🎯 **Completion Rate:** {gen_stats['completion_rate']}%\n\n"
            "📅 **Today Activity Logs:**\n"
            f" ├ Start pressed: {today_events.get('START_BOT', 0)}\n"
            f" ├ Passed Stage 1: {today_events.get('PASS_STAGE_1', 0)}\n"
            f" ├ Passed Stage 2: {today_events.get('PASS_STAGE_2', 0)}\n"
            f" └ Total Finished Today: {today_events.get('COMPLETED', 0)}"
        )
        await message.reply(response, parse_mode="Markdown")

    @dp.message_handler(commands=['recent'])
    async def admin_recent(message: types.Message):
        if not is_admin(message.from_user.id):
            return

        logs = await analytics.get_recent_logs(15)
        if not logs:
            await message.reply("Hozircha hech qanday log mavjud emas.")
            return

        lines = []
        for time_str, username, event, user_id in logs:
            user_repr = f"@{username}" if username else f"ID: {user_id}"
            lines.append(f"⏱ {time_str} | {user_repr} | `{event}`")

        response = "⏳ **Last 15 Activity Events:**\n\n" + "\n".join(lines)
        await message.reply(response, parse_mode="Markdown")

    @dp.message_handler(commands=['user'])
    async def admin_user_search(message: types.Message):
        if not is_admin(message.from_user.id):
            return

        args = message.get_args()
        if not args:
            await message.reply("Format xato. Masalan:\n`/user 1234567` yoki `/user @username`", parse_mode="Markdown")
            return

        user_data = await analytics.get_detailed_user_info(args.strip())
        if not user_data:
            await message.reply("❌ Bunday foydalanuvchi ma'lumotlar bazasidan topilmadi.")
            return

        user_id, username, stage, first_join, last_act = user_data
        uname = f"@{username}" if username else "Mavjud emas"
        is_done = "Ha ✅" if stage == "COMPLETED" else "Yo'q ❌"

        response = (
            "👤 **User Progress Card**\n\n"
            f"🆔 **ID:** `{user_id}`\n"
            f"🌐 **Username:** {uname}\n"
            f"⚡ **Current Stage:** `{stage}`\n"
            f"📥 **First Join:** {first_join}\n"
            f"🔄 **Last Activity:** {last_act}\n"
            f"🏁 **Finished:** {is_done}"
        )
        await message.reply(response, parse_mode="Markdown")
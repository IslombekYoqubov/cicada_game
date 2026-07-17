import os
import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiohttp import web

import database as db_mod
from handlers.user import register_user_handlers
from handlers.admin import register_admin_handlers

API_TOKEN = '8603411482:AAGGH9GL-OlZ2awx7aN-A7hPBTiIwwNx9Bs'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Handlerlarni ro'yxatdan o'tkazish
register_admin_handlers(dp, bot)
register_user_handlers(dp, bot)

async def handle_ping(request):
    return web.Response(text="Miya yoniq, tizim va analitika onlayn!")

async def main():
    # 1. Bazani va xavfsiz migratsiyalarni ishga tushirish
    await db_mod.init_db()
    
    # 2. Render uxlab qolmasligi uchun HTTP Serverni yoqish
    app = web.Application()
    app.router.add_get('/', handle_ping)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Web server {port}-portda muvaffaqiyatli ishga tushdi.")

    # 3. Bot Pollingni fonda boshlash
    try:
        await dp.start_polling()
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
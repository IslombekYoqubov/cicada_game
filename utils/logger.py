import aiosqlite
from database import DB_FILE

async def log_event(user_id: int, event: str, stage: str):
    """
    Tizimdagi har qanday foydalanuvchi harakatini bazaga muhrlaydi.
    Events: START_BOT, ENTER_STAGE_1, PASS_STAGE_1, JOIN_CHANNEL, PASS_STAGE_2, COMPLETED, va h.k.
    """
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('''
            INSERT INTO event_logs (user_id, event, stage, created_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, event, stage))
        await db.commit()
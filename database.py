import aiosqlite
import logging

DB_FILE = 'quest_bot.db'

async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        # Asosiy foydalanuvchilar jadvali
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                stage TEXT DEFAULT 'STAGE_1'
            )
        ''')
        await db.commit()

        # Xavfsiz Migratsiya: Yangi ustunlarni tekshirib qo'shish
        columns_to_add = [
            ("first_join_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ("last_activity_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ("current_stage", "TEXT DEFAULT 'STAGE_1'"),
            ("completed_at", "TIMESTAMP")
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                await db.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                await db.commit()
                logging.info(f"Database: '{col_name}' ustuni muvaffaqiyatli qo'shildi.")
            except aiosqlite.OperationalError:
                # Agar ustun allaqachon mavjud bo'lsa, SQLite xato beradi va biz uni o'tkazib yuboramiz
                pass

        # Event loglari uchun alohida yangi jadval
        await db.execute('''
            CREATE TABLE IF NOT EXISTS event_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                event TEXT,
                stage TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()

async def get_user_stage(user_id):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute('SELECT stage FROM users WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else "STAGE_1"

async def set_user_stage(user_id, stage):
    async with aiosqlite.connect(DB_FILE) as db:
        if stage == "COMPLETED":
            await db.execute('''
                UPDATE users 
                SET stage = ?, current_stage = ?, last_activity_at = CURRENT_TIMESTAMP, completed_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (stage, stage, user_id))
        else:
            await db.execute('''
                UPDATE users 
                SET stage = ?, current_stage = ?, last_activity_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (stage, stage, user_id))
        await db.commit()

async def register_or_update_user(user_id, username, stage="STAGE_1"):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('''
            INSERT INTO users (user_id, username, stage, current_stage, first_join_at, last_activity_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET 
                username = excluded.username,
                last_activity_at = CURRENT_TIMESTAMP
        ''', (user_id, username, stage, stage))
        await db.commit()

async def update_last_activity(user_id, username=None):
    async with aiosqlite.connect(DB_FILE) as db:
        if username:
            await db.execute('''
                UPDATE users SET last_activity_at = CURRENT_TIMESTAMP, username = ? WHERE user_id = ?
            ''', (username, user_id))
        else:
            await db.execute('''
                UPDATE users SET last_activity_at = CURRENT_TIMESTAMP WHERE user_id = ?
            ''', (user_id,新建))
        await db.commit()
import aiosqlite
from database import DB_FILE

async def get_general_stats():
    async with aiosqlite.connect(DB_FILE) as db:
        # Umumiy foydalanuvchilar
        async with db.execute("SELECT COUNT(*) FROM users") as c:
            total_users = (await c.fetchone())[0]
            
        # Bugun qo'shilganlar (Sana bo'yicha)
        async with db.execute("SELECT COUNT(*) FROM users WHERE date(first_join_at) = date('now')") as c:
            today_joined = (await c.fetchone())[0]

        # Bugun aktiv bo'lganlar
        async with db.execute("SELECT COUNT(*) FROM users WHERE date(last_activity_at) = date('now')") as c:
            active_today = (await c.fetchone())[0]

        # Tugatganlar soni
        async with db.execute("SELECT COUNT(*) FROM users WHERE stage = 'COMPLETED'") as c:
            completed_count = (await c.fetchone())[0]

        # Har bir Stage'da turgan amaldagi userlar soni
        stages_count = {"STAGE_1": 0, "STAGE_2": 0, "COMPLETED": 0}
        async with db.execute("SELECT stage, COUNT(*) FROM users GROUP BY stage") as cursor:
            async for row in cursor:
                stages_count[row[0]] = row[1]

        # Completion Rate hisoblash
        completion_rate = 0.0
        if total_users > 0:
            completion_rate = (completed_count / total_users) * 100

        return {
            "total_users": total_users,
            "today_joined": today_joined,
            "active_today": active_today,
            "completed": completed_count,
            "stages_count": stages_count,
            "completion_rate": round(completion_rate, 2)
        }

async def get_today_events_analytics():
    async with aiosqlite.connect(DB_FILE) as db:
        # Bugun sodir bo'lgan o'ziga xos eventlar soni
        events = ["START_BOT", "PASS_STAGE_1", "PASS_STAGE_2", "COMPLETED"]
        stats = {}
        for ev in events:
            async with db.execute(
                "SELECT COUNT(*) FROM event_logs WHERE event = ? AND date(created_at) = date('now')", (ev,)
            ) as c:
                stats[ev] = (await c.fetchone())[0]
        return stats

async def get_recent_logs(limit=15):
    async with aiosqlite.connect(DB_FILE) as db:
        # Oxirgi eventlarni username bilan birga yuklash
        query = '''
            SELECT strftime('%H:%M', e.created_at), u.username, e.event, e.user_id
            FROM event_logs e
            LEFT JOIN users u ON e.user_id = u.user_id
            ORDER BY e.id DESC LIMIT ?
        '''
        async with db.execute(query, (limit,)) as cursor:
            return await cursor.fetchall()

async def get_detailed_user_info(search_param):
    async with aiosqlite.connect(DB_FILE) as db:
        if str(search_param).isdigit():
            query = "SELECT user_id, username, stage, first_join_at, last_activity_at FROM users WHERE user_id = ?"
            params = (int(search_param),)
        else:
            username = str(search_param).replace("@", "")
            query = "SELECT user_id, username, stage, first_join_at, last_activity_at FROM users WHERE LOWER(username) = LOWER(?)"
            params = (username,)

        async with db.execute(query, params) as cursor:
            return await cursor.fetchone()
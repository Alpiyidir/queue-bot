import sqlite3


def connect_to_database():
    conn = sqlite3.connect("queuebot.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_text_id(guildId):
    # connects to database and initializes cursor
    conn = connect_to_database()
    c = conn.cursor()

    # fetches text and voice channel id
    c.execute("SELECT text_channel_id FROM preferences WHERE guild_id = ?", [guildId])
    row = c.fetchone()

    if not row:
        conn.close()
        return None

    conn.close()
    return row["text_channel_id"]


def get_voice_id(guildId):
    # connects to database and initializes cursor
    conn = connect_to_database()
    c = conn.cursor()

    # fetches text and voice channel id
    c.execute("SELECT voice_channel_id FROM preferences WHERE guild_id = ?", [guildId])
    row = c.fetchone()

    if not row:
        conn.close()
        return None

    conn.close()
    return row["voice_channel_id"]


def get_bot_prefix(guildId):
    conn = connect_to_database()
    c = conn.cursor()
    c.execute("SELECT bot_prefix FROM preferences WHERE guild_id = ?", [guildId])
    botPrefix = c.fetchone()["bot_prefix"]
    conn.close()
    return botPrefix


def get_queue_save_time(guildId):
    conn = connect_to_database()
    c = conn.cursor()
    c.execute("SELECT save_time FROM preferences WHERE guild_id = ?", [guildId])
    queueSaveTime = c.fetchone()["save_time"]
    conn.close
    return queueSaveTime


def set_voice_id(guildId, voiceId):
    conn = connect_to_database()
    c = conn.cursor()

    c.execute("UPDATE preferences SET voice_channel_id = ? WHERE guild_id = ?", [voiceId, guildId])
    conn.commit()
    conn.close()


def set_queue_save_time_id(guildId, queueSaveTime):
    conn = connect_to_database()
    c = conn.cursor()

    c.execute("UPDATE preferences SET save_time = ? WHERE guild_id = ?", [queueSaveTime, guildId])
    conn.commit()
    conn.close()


def set_text_id(guildId, textId):
    conn = connect_to_database()
    c = conn.cursor()

    c.execute("UPDATE preferences SET text_channel_id = ? WHERE guild_id = ?", [textId, guildId])
    conn.commit()
    conn.close()


def set_bot_prefix(guildId, botPrefix):
    conn = connect_to_database()
    c = conn.cursor()

    c.execute("UPDATE preferences SET bot_prefix = ? WHERE guild_id = ?", [botPrefix, guildId])
    conn.commit()
    conn.close()


def get_queue_times(guildId, memberId, queueCountToSelect):
    conn = connect_to_database()
    c = conn.cursor()
    c.execute(
        "SELECT timestamp, time_in_queue FROM queueinfo WHERE guild_id = ? AND member_id = ? ORDER BY timestamp DESC",
        [guildId, memberId])
    rowList = c.fetchmany(queueCountToSelect)
    conn.close()
    return rowList


def write_member_info(guildId, memberId, unixTime, timeSpentInQueue):
    conn = connect_to_database()
    c = conn.cursor()

    c.execute("INSERT INTO queueinfo (guild_id, member_id, timestamp, time_in_queue) VALUES (?, ?, ?, ?)",
              [guildId, memberId, unixTime, timeSpentInQueue])
    conn.commit()
    conn.close()


def create_default_preferences_if_not_in_db(guildId):
    conn = connect_to_database()
    c = conn.cursor()

    c.execute("SELECT guild_id FROM preferences")
    rowList = c.fetchall()

    # If the guild id already has a preferences entry then it won't create preferences, and so will return, if it does
    # not return then the function will create default prefs
    for row in rowList:
        if row["guild_id"] == guildId:
            return

    c.execute("INSERT INTO preferences (guild_id) VALUES (?)", [guildId])
    conn.commit()
    conn.close()

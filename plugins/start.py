import random
import humanize
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import URL, LOG_CHANNEL, SHORTLINK
from urllib.parse import quote_plus
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
from TechVJ.util.human_readable import humanbytes
from database.users_chats_db import db
from utils import temp, get_shortlink
from premium import is_premium
from datetime import datetime, timedelta  # ✅ for tracking usage time

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))

    rm = InlineKeyboardMarkup([
        [InlineKeyboardButton("✨ Update Channel", url="https://t.me/vj_botz")]
    ])

    await client.send_message(
        chat_id=message.from_user.id,
        text=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
        reply_markup=rm,
        parse_mode=enums.ParseMode.HTML
    )

    await message.reply_text(
        f"""👋 Welcome {message.from_user.first_name}!
⚠️ Only premium users can use this bot.
💳 To check your plan or buy access, click /plan."""
    )


@Client.on_message(filters.private & (filters.document | filters.video))
async def stream_start(client, message):
    user_id = message.from_user.id

    if not is_premium(user_id):
        # ✅ Check last usage time
        last_use = await db.get_last_use(user_id)
        now = datetime.utcnow()

        if last_use:
            last_used_date = datetime.strptime(last_use, "%Y-%m-%d")
            if last_used_date.date() == now.date():
                await message.reply_text("❌ You have already used your free access today.\nUse /plan to buy premium.")
                return

        # ✅ Update last use
        await db.set_last_use(user_id, now.strftime("%Y-%m-%d"))

    file = getattr(message, message.media.value)
    filename = file.file_name
    filesize = humanize.naturalsize(file.file_size)
    fileid = file.file_id
    username = message.from_user.mention

    log_msg = await client.send_cached_media(
        chat_id=LOG_CHANNEL,
        file_id=fileid,
    )

    fileName = get_name(log_msg)

    if not SHORTLINK:
        stream = f"{URL}watch/{str(log_msg.id)}/{quote_plus(fileName)}?hash={get_hash(log_msg)}"
        download = f"{URL}{str(log_msg.id)}/{quote_plus(fileName)}?hash={get_hash(log_msg)}"
    else:
        stream = await get_shortlink(f"{URL}watch/{str(log_msg.id)}/{quote_plus(fileName)}?hash={get_hash(log_msg)}")
        download = await get_shortlink(f"{URL}{str(log_msg.id)}/{quote_plus(fileName)}?hash={get_hash(log_msg)}")

    await log_msg.reply_text(
        text=f"•• ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ꜰᴏʀ ɪᴅ #{user_id} \n•• ᴜꜱᴇʀɴᴀᴍᴇ : {username} \n\n•• ᖴᎥᒪᗴ Nᗩᗰᗴ : {fileName}",
        quote=True,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🚀 Fast Download 🚀", url=download),
                InlineKeyboardButton('🖥️ Watch online 🖥️', url=stream)
            ]
        ])
    )

    rm = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("sᴛʀᴇᴀᴍ 🖥", url=stream),
            InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ 📥", url=download)
        ]
    ])

    msg_text = f"""<i><u>𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 !</u></i>\n\n<b>📂 Fɪʟᴇ ɴᴀᴍᴇ :</b> <i>{fileName}</i>\n\n<b>📦 Fɪʟᴇ ꜱɪᴢᴇ :</b> <i>{humanbytes(get_media_file_size(message))}</i>\n\n<b>📥 Dᴏᴡɴʟᴏᴀᴅ :</b> <i>{download}</i>\n\n<b> 🖥ᴡᴀᴛᴄʜ  :</b> <i>{stream}</i>\n\n<b>🚸 Nᴏᴛᴇ : ʟɪɴᴋ ᴡᴏɴ'ᴛ ᴇxᴘɪʀᴇ ᴛɪʟʟ ɪ ᴅᴇʟᴇᴛᴇ</b>"""

    await message.reply_text(
        text=msg_text,
        quote=True,
        disable_web_page_preview=True,
        reply_markup=rm
    )

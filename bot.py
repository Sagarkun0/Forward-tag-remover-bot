from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = ''


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
✨ *Forward Tag Remover Bot*

📩 Send me any forwarded message.
I will resend it back without forward tag.

✅ Supports:
• Text
• Mono Text
• Quotes
• Links
• Photos
• Videos
• Files
• Stickers
• Voice
• Audio

✅ Works in groups & channels too!
✅ In channels, deletes the original forwarded post and reposts clean.

👨‍💻 Developer : @sagarkun0
"""
    await update.message.reply_text(text, parse_mode="Markdown")


async def dev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
👨‍💻 *Developer Information*

Name : Sagar
Telegram : @sagarkun0

⚡ This bot removes forward tags
and re-sends messages in same format.
"""
    await update.message.reply_text(text, parse_mode="Markdown")


async def forward_remover(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message

    if not msg:
        return

    # Skip auto-forwarded posts (channel -> linked discussion group)
    if msg.is_automatic_forward:
        return

    chat_id = msg.chat_id
    message_id = msg.message_id

    # Check if this message was actually forwarded
    is_forwarded = bool(
        getattr(msg, "forward_origin", None)
        or getattr(msg, "forward_from", None)
        or getattr(msg, "forward_from_chat", None)
    )

    # IMPORTANT: ignore normal (non-forwarded) messages completely.
    # Without this check, every regular chat message also gets copied.
    if not is_forwarded:
        return

    sent = None

    if msg.text:
        sent = await context.bot.send_message(
            chat_id=chat_id,
            text=msg.text,
            entities=msg.entities or []
        )

    elif msg.photo:
        sent = await context.bot.send_photo(
            chat_id=chat_id,
            photo=msg.photo[-1].file_id,
            caption=msg.caption or "",
            caption_entities=msg.caption_entities
        )

    elif msg.video:
        sent = await context.bot.send_video(
            chat_id=chat_id,
            video=msg.video.file_id,
            caption=msg.caption or "",
            caption_entities=msg.caption_entities
        )

    elif msg.document:
        sent = await context.bot.send_document(
            chat_id=chat_id,
            document=msg.document.file_id,
            caption=msg.caption or "",
            caption_entities=msg.caption_entities
        )

    elif msg.audio:
        sent = await context.bot.send_audio(
            chat_id=chat_id,
            audio=msg.audio.file_id,
            caption=msg.caption or "",
            caption_entities=msg.caption_entities
        )

    elif msg.voice:
        sent = await context.bot.send_voice(
            chat_id=chat_id,
            voice=msg.voice.file_id
        )

    elif msg.sticker:
        sent = await context.bot.send_sticker(
            chat_id=chat_id,
            sticker=msg.sticker.file_id
        )

    # Delete the original forwarded message once the clean repost succeeds.
    # Works in groups and channels (bot needs delete rights in both).
    if sent:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            print(f"⚠️ Couldn't delete original message: {e}")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dev", dev))

    # Private chats + groups
    app.add_handler(
        MessageHandler(filters.ALL & ~filters.COMMAND, forward_remover)
    )

    # Channel posts
    app.add_handler(
        MessageHandler(filters.UpdateType.CHANNEL_POST, forward_remover)
    )

    print("✅ Bot Started Successfully...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

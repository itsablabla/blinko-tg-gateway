#!/usr/bin/env python3
"""Minimal Blinko Cloud Telegram bridge.
Listens for text messages from one authorized chat and saves each as a Blinko
note via the Blinko Agent API (POST {BLINKO_API_URL}/api/agent/note).
Env: TELEGRAM_BOT_TOKEN, AUTHORIZED_CHAT_ID, BLINKO_API_URL, BLINKO_API_KEY
"""
import logging
import os

import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO)
log = logging.getLogger("blinko-tg")

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
AUTHORIZED_CHAT_ID = int(os.environ["AUTHORIZED_CHAT_ID"])
BLINKO_API_URL = os.environ["BLINKO_API_URL"].rstrip("/")
BLINKO_API_KEY = os.environ["BLINKO_API_KEY"]


async def save_note(content: str):
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{BLINKO_API_URL}/api/agent/note",
            headers={"Authorization": f"Bearer {BLINKO_API_KEY}"},
            json={"content": content},
        )
    return resp.status_code, resp.text


async def start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! Send me a message and I will save it to Blinko.")


async def on_message(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if chat_id != AUTHORIZED_CHAT_ID:
        log.warning("ignoring message from unauthorized chat %s", chat_id)
        return
    text = update.message.text
    if not text or not text.strip():
        await update.message.reply_text("Only text messages are supported for now.")
        return
    try:
        status, body = await save_note(text.strip())
        if status == 200:
            await update.message.reply_text("Saved to Blinko ✔")
        else:
            log.error("blinko api %s: %s", status, body[:300])
            await update.message.reply_text(f"Blinko returned error {status}.")
    except Exception:
        log.exception("failed to save note")
        await update.message.reply_text("Save failed — check the bridge logs.")


def main() -> None:
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
    log.info("polling started for bot %s ...", TELEGRAM_BOT_TOKEN.split(":")[0])
    app.run_polling()


if __name__ == "__main__":
    main()

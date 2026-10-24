# Blinko Cloud Telegram bridge

Saves Telegram text messages to Blinko Cloud notes via the Blinko Agent API.

Long-polling only — no inbound port or public URL required.

## Environment

| Variable | Description |
| --- | --- |
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather |
| `AUTHORIZED_CHAT_ID` | Numeric Telegram chat id allowed to write |
| `BLINKO_API_URL` | Blinko API base, e.g. `https://api.blinko.space` |
| `BLINKO_API_KEY` | Blinko API key (`blk_...`) |

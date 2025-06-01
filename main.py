import asyncio
import re
from telethon import TelegramClient, events
from telethon.errors import MessageIdInvalidError

accounts = [
    {"api_id": 8447214, "api_hash": '9ec5782ddd935f7e2763e5e49a590c0d', "session_name": 'session1'},
    {"api_id": 22548387, "api_hash": '40cfecc9ba1ee8d5f60e1dc475884dce', "session_name": 'session2'}
]

GAME_BOT_ID = 5364964725
keywords = ["level", "identified", "engage", "dizzy", "blinded"]

async def resend_if_no_response(client, chat_id, message, delay=3):
    await asyncio.sleep(delay)
    last = (await client.get_messages(chat_id, limit=1))[0]
    if message in last.raw_text.lower():
        await client.send_message(chat_id, message)

def has_keywords(text, keys): 
    return any(k in re.sub(r"[^\w\s]", "", text).lower() for k in keys)

async def run_client(account):
    running = False
    client = TelegramClient(account['session_name'], account['api_id'], account['api_hash'])

    @client.on(events.NewMessage(pattern=r'!st'))
    async def start(event):
        nonlocal running
        running = True
        await event.reply("Bot started!")

    @client.on(events.NewMessage(pattern=r'!sp'))
    async def stop(event):
        nonlocal running
        running = False
        await event.reply("Bot stopped.")

    @client.on(events.NewMessage(from_users=GAME_BOT_ID))
    async def on_message(event):
        if not running:
            return
        if event.buttons:
            await asyncio.sleep(0.5)
            await event.click(0)
        elif has_keywords(event.raw_text, keywords):
            await asyncio.sleep(0.5)
            await client.send_message(GAME_BOT_ID, "/explore")
            await resend_if_no_response(client, GAME_BOT_ID, "/explore")

    @client.on(events.MessageEdited(from_users=GAME_BOT_ID))
    async def on_edit(event):
        if not running:
            return

        text = event.raw_text.lower()
        click_first = ["dizzy", "pearls", "tickets"]
        click_second = ["common", "rare"]
        explore_triggers = [
            "reward", "successfully", "walked", "defeated", "found", "🎫", "🔮",
            "tranquilizer", "net", "chains", "rope", "freeze ray", "miserably", "mournfully",
            "unfortunately", "angrily", "dissappeared", "cry", "sadly", "sad", "sorrowfully", "dejectedly"
        ]
        try:
            if "encounter" in text:
                await asyncio.sleep(0.88)
                await client.send_message(GAME_BOT_ID, "/fight")
                await resend_if_no_response(client, GAME_BOT_ID, "/fight")
            elif any(k in text for k in explore_triggers):
                await asyncio.sleep(0.88)
                await client.send_message(GAME_BOT_ID, "/explore")
                await resend_if_no_response(client, GAME_BOT_ID, "/explore")
            elif any(k in text for k in click_first):
                await asyncio.sleep(0.88)
                await event.click(0)
            elif any(k in text for k in click_second):
                await asyncio.sleep(0.88)
                await event.click(1, 0)
            elif any(k in text for k in ["enemy", "attacker", "avoided", "opponent", "select", "moves", "move"]):
                await asyncio.sleep(0.5)
                try:
                    await event.click(1, 0)
                except:
                    await event.click(0, 0)
            elif has_keywords(text, keywords):
                await asyncio.sleep(0.5)
                if event.buttons:
                    await event.click(0)
                else:
                    await client.send_message(GAME_BOT_ID, "/explore")
                    await resend_if_no_response(client, GAME_BOT_ID, "/explore")
        except (asyncio.TimeoutError, MessageIdInvalidError):
            pass

    print(f"{account['session_name']} ready. Use !st to start or !sp to pause.")
    await client.start()
    await client.run_until_disconnected()

async def main():
    num = int(input("Run how many accounts? (1 or 2): "))
    await asyncio.gather(*(run_client(acc) for acc in accounts[:num]))

asyncio.run(main())

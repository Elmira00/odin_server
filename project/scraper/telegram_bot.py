import asyncio
from telegram import Bot

TELEGRAM_BOT_TOKEN = '7878304917:AAGo9JdcDLmP-A76tDrprogBpqrscCq-7ZI'

async def main():

    #Create bot object
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    #Get updates
    await bot.delete_webhook()
    updates = await bot.get_updates()
    if not bot:
        print('bot not found')
    if not updates:
        print("No updates found")
    else:
        for update in updates:
            if update.message:

                #print(update.message)

                chat_id = update.message.chat.id
                chat_title = update.message.chat.title
                message_text = update.message.text
                print(f"Chat ID: {chat_id}  | Chat Title: {chat_title} | Message: {message_text}")

asyncio.run(main())

# scraper/management/commands/run_telegram_bot.py

import asyncio
from django.core.management.base import BaseCommand
from tasks.send_keyword_match_notify import start_bot_listener


class Command(BaseCommand):
    help = "Run Telegram bot listener"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting Telegram bot...")
        asyncio.run(start_bot_listener())

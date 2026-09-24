from telegram import Bot
import json
from django.utils import timezone
from datetime import timedelta
from management.models import Problem
import asyncio

TELEGRAM_BOT_TOKEN = '7878304917:AAGo9JdcDLmP-A76tDrprogBpqrscCq-7ZI'
TELEGRAM_CHAT_ID = '-1002794930818'


async def send_telegram_message(text: str):
    async with Bot(token=TELEGRAM_BOT_TOKEN) as bot:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=text,
        )


def notify_unsent_problems():

    five_minutes_ago = timezone.now() - timedelta(minutes=5)

    problems = list(
        Problem.objects.filter(
            created_at__gte=five_minutes_ago,
            is_deleted=False,
            is_sent=False
        ).select_related("source", "category")
    )

    if not problems:
        return

    lines = ["New Problems\n"]

    for problem in problems:

        data = problem.problem_description

        if isinstance(data, str):
            data = json.loads(data)

        source_name = data.get("source_name", "unknown")
        problem_type = data.get("problem_type", "unknown")
        total_count = data.get("total_count", 0)

        lines.append(
            f"Source: {source_name}\n"
            f"Type: {problem_type}\n"
            f"Total: {total_count}\n"
        )

    message = "\n".join(lines)
    asyncio.run(send_telegram_message(message))

    Problem.objects.filter(id__in=[p.id for p in problems]).update(is_sent=True)



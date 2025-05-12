import discord
import os
import sys
import asyncio
import signal
import sentry_sdk
import random
from dotenv import get_key
from discord.ext import commands, tasks

from view.close import CloseView
from view.start_ticket import StartTicketView
from view.inactive import InactiveView

sentry_sdk.init("http://ca1217fce7644447860bace472887020@192.168.2.99:8000/3")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

paths = [
    "ext/"
]

class Tickets(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=">>",
            help_command=None,
            intents=intents
        )

    @tasks.loop(hours=2)
    async def presence_tick(self):
        choices: discord.Activity or discord.CustomActivity = [
            discord.Activity(
                type=discord.ActivityType.watching, name="Tickets"
            ),
            discord.CustomActivity(name="Writing Transcripts"),
            discord.Activity(
                type=discord.ActivityType.watching, name="Boxes"
            )
        ]

        await self.change_presence(
            activity=random.choice(choices), status=discord.Status.online
        )

    async def setup_hook(self):
        self.add_view(CloseView(self))
        self.add_view(StartTicketView(self))
        self.add_view(InactiveView(self))
        
        if not os.path.exists("configuration/configuration.json"):
            with open("configuration/configuration.json", "w") as f:
                f.write("{}")
        
        if not os.path.exists("configuration/tickets.json"):
            with open("configuration/tickets.json", "w") as f:
                f.write("{}")
    
    async def on_connect(self):
        choices: discord.Activity or discord.CustomActivity = [
            discord.CustomActivity(name="¯\\_(ツ)_/¯")
        ]
        
        await self.change_presence(
            activity=random.choice(choices), status=discord.Status.dnd
        )
    
    async def on_ready(self):
        
        self.presence_tick.start()
        
        for path in paths:
            for file in os.listdir(path):
                if file.startswith("-"):
                    continue
                if file.endswith(".py"):
                    await self.load_extension(f"{path.replace("/", ".")}{file[:-3]}")
    
        sync = await self.tree.sync()
        print(f"> Synced {len(sync)} commands")
    
        print(
            f">> {self.user.name} Ready"
            )

# Shutdown Handler
def shutdown_handler(signum, frame):
    loop = asyncio.get_event_loop()
    
    # Cancel all tasks lingering
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    [task.cancel() for task in tasks]

    loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
    loop.close()

    sys.exit(0)


signal.signal(signal.SIGTERM, shutdown_handler)

bot = Tickets()

bot.run(os.environ.get("TOKEN", get_key("./.env", "TOKEN")))

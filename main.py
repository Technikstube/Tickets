import discord
import os
import sys
import asyncio
import signal
import sentry_sdk
import random
from dotenv import get_key
from datetime import datetime
from discord.ext import commands, tasks

from utility import Ticket, Config
from view.close import CloseView
from view.start_ticket import StartTicketView
from modal.start_ticket import StartTicketModal

sentry_sdk.init("http://ca1217fce7644447860bace472887020@192.168.2.99:8000/3")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

paths = [
    "ext/"
]

MAXIMUM_INACTIVE_SECONDS = 10800 # 3 hours in seconds

class Tickets(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=">>",
            help_command=None,
            intents=intents
        )
    
    @tasks.loop(hours=12.1)
    async def purge_inactive_tickets(self):
        TICKETS = Ticket().get() # One List that doesnt change, so that the for loop doesnt break lol.
        tickets = Ticket().get()
        conf = Config().get()
        
        for ticket in TICKETS:
            member = None
            channel = None
            channel = self.get_channel(Ticket().get_ticket_channel_id(int(ticket)))
            member = channel.guild.get_member(int(ticket))
            transcript = ""
            
            if tickets[str(ticket)]["stale"]:
                channel = self.get_channel(Ticket().get_ticket_channel_id(int(ticket)))
                transcript = tickets[str(ticket)]["transcript"]
                tickets.pop(str(ticket))
                
                if member is not None:
                    with open(f"configuration/{transcript}", "rb") as f:
                        embed = discord.Embed(title="", description=f"{channel.name} wurde von {self.user.mention} geschlossen.", color=discord.Color.blue())
                        await member.send(embed=embed, file=discord.File(f))
                Ticket().save(tickets)
                await channel.delete()
                if "transcript_channel" in conf:
                    tc = self.get_channel(int(conf["transcript_channel"]))
                    with open(f"configuration/{transcript}", "rb") as f:
                        embed = discord.Embed(title="", description=f"{channel.name} wurde von {self.user.mention} geschlossen.", color=discord.Color.blue())
                        await tc.send(embed=embed, file=discord.File(f))
                    os.remove(f"./configuration/{transcript}")
                continue
    
    @tasks.loop(minutes=1.1)
    async def inactive_marker(self):
        TICKETS = Ticket().get() # One List that doesnt change, so that the for loop doesnt break lol.
        tickets = Ticket().get()
        
        stale_embed = discord.Embed(title="",
                                    description="<:uncheck:1226665497701912728> Ticket als `Inaktiv` markiert.",
                                    color=discord.Color.red()
                                    )
        for ticket in TICKETS:
            channel = None
            channel = self.get_channel(Ticket().get_ticket_channel_id(int(ticket)))
            dist = round(datetime.now().timestamp()) - round(tickets[str(ticket)]["last_activity"])
            if dist >= MAXIMUM_INACTIVE_SECONDS:
                if tickets[str(ticket)]["stale"] is True:
                    continue
                tickets[str(ticket)]["stale"] = True
                Ticket().save(tickets)
                await channel.send(embed=stale_embed)

                await channel.edit(name=channel.name.replace("ticket", "inactive"))
                await channel.move(end=True)
                continue

    @tasks.loop(minutes=60.1)
    async def presence_tick(self):
        choices: discord.Activity or discord.CustomActivity = [
            discord.Activity(
                type=discord.ActivityType.watching, name="Tickets"
            ),
            discord.CustomActivity(name="Technikstube Support")
        ]

        await self.change_presence(
            activity=random.choice(choices), status=discord.Status.online
        )

    async def setup_hook(self):
        self.add_view(CloseView(self))
        self.add_view(StartTicketView(self))
    
    async def on_connect(self):
        choices: discord.Activity or discord.CustomActivity = [
            discord.CustomActivity(name="¯\\_(ツ)_/¯")
        ]

        await self.change_presence(
            activity=random.choice(choices), status=discord.Status.dnd
        )
    
    async def on_ready(self):
        
        self.presence_tick.start()
        self.purge_inactive_tickets.start()
        self.inactive_marker.start()
        
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

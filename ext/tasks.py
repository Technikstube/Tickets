import discord
from discord.ext import commands, tasks
from datetime import datetime

from utility import Ticket, Transcript
from ui.view import InactiveView

MAXIMUM_INACTIVE_SECONDS = 21600 # 6 hours in seconds

class Tasks(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.inactive_marker.start()

    @tasks.loop(hours=16)
    async def inactive_marker(self):
        TICKETS = Ticket().get()
        tickets = Ticket().get()
        
        stale_embed = discord.Embed(title="",
                                    description="",
                                    color=discord.Color.orange()
                                    )
        
        for ticket in TICKETS:
            channel = None
            submitter = self.bot.get_user(int(ticket))
            last_activity = round(tickets[str(ticket)]["last_activity"])
            channel = self.bot.get_channel(Ticket().get_ticket_channel_id(int(ticket)))
            dist = round(datetime.now().timestamp()) - last_activity
            
            timestamp = f"<t:{last_activity}:R>"
            stale_embed = discord.Embed(title="",
                                    description=f"**This Ticket is already inactive since {timestamp}. Is this Ticket resolved?**",
                                    color=discord.Color.orange()
                                    )
            
            if dist >= MAXIMUM_INACTIVE_SECONDS:
                tickets[str(ticket)]["stale"] = True
                Transcript(f"configuration/{tickets[str(ticket)]["transcript"]}").append_as_system("Ticket was marked as Inactive.")
                if tickets[str(ticket)]["stale_notified"] is False:
                    msg = await channel.send(content=f"{submitter.mention}", embed=stale_embed)
                    await msg.edit(view=InactiveView(self.bot, msg))
                    tickets[str(ticket)]["stale_notified"] = True
                else:
                    msg = await channel.send(content="", embed=stale_embed)
                    await msg.edit(view=InactiveView(self.bot, msg))
                    tickets[str(ticket)]["stale_notified"] = False
                Ticket().save(tickets)
                continue
    
async def setup(bot):
    await bot.add_cog(Tasks(bot))
    print(f"> {__name__} loaded")
    
async def teardown(bot):
    await bot.remove_cog(Tasks(bot))
    print(f"> {__name__} unloaded")
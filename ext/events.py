import discord
import os
from datetime import datetime
from discord.ext import commands

from utility import Ticket, Config

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
    
    @commands.Cog.listener(name="on_message")
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        tickets: dict = Ticket().get()
        ticket = None
        channel = None
        
        for _ticket in tickets:
            if int(tickets[str(_ticket)]["channel"]) != message.channel.id:
                return
            channel = self.bot.get_channel(int(tickets[str(_ticket)]["channel"]))
            ticket = _ticket
        if ticket is None:
            return
        if channel is None:
            return
        
        with open(f"configuration/{tickets[str(ticket)].get("transcript")}", "a") as f:
            date = datetime.now()
            f.write(
                f"{date.day}.{date.month}.{str(date.year)[2:]}, {date.hour}:{date.minute}:{date.second} | {message.author.name}: {message.content}\n"
            )
            
        tickets[str(ticket)]["last_activity"] = datetime.now().timestamp()
        if tickets[str(ticket)]["stale"] is True:
            tickets[str(ticket)]["stale"] = False
            await channel.edit(name=channel.name.replace("inactive", "ticket"))
            await channel.move(beginning=True)
        Ticket().save(tickets)
        
    @commands.Cog.listener(name="on_message_edit")
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot:
            return
        tickets: dict = Ticket().get()
        ticket = None
        channel = None
        
        for _ticket in tickets:
            if int(tickets[str(_ticket)]["channel"]) != before.channel.id:
                return
            channel = self.bot.get_channel(int(tickets[str(_ticket)]["channel"]))
            ticket = _ticket
        if ticket is None:
            return
        if channel is None:
            return
        
        with open(f"configuration/{tickets[str(ticket)].get("transcript")}", "a") as f:
            date = datetime.now()
            f.write(
                f"{date.day}.{date.month}.{str(date.year)[2:]}, {date.hour}:{date.minute}:{date.second} | [Editiert] {after.author.name}: {after.content}\n    vorher: {before.content}\n"
            )
                    
    @commands.Cog.listener(name="on_member_remove")
    async def on_member_remove(self, member: discord.Member):
        conf = Config().get()
        tickets = Ticket().get()
        transcript = ""
        
        for ticket in tickets:
            if ticket == str(member.id):
                channel = self.bot.get_channel(Ticket().get_ticket_channel_id(int(ticket)))
                transcript = tickets[str(ticket)]["transcript"]
                tickets.pop(str(ticket))
                Ticket().save(tickets)
                await channel.delete()
                if "transcript_channel" in conf:
                    tc = self.bot.get_channel(int(conf["transcript_channel"]))
                    with open(f"configuration/{transcript}", "rb") as f:
                        embed = discord.Embed(title="", description=f"{channel.name} wurde von {self.bot.user.mention} geschlossen. (Nutzer hat den Server verlassen)", color=discord.Color.blue())
                        await tc.send(embed=embed, file=discord.File(f))
                    os.remove(f"./configuration/{transcript}")
                break
        
async def setup(bot):
    await bot.add_cog(Events(bot))
    print(f"> {__name__} loaded")
    
async def teardown(bot):
    await bot.remove_cog(Events(bot))
    print(f"> {__name__} unloaded")
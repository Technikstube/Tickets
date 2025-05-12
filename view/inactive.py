import discord
from typing import Optional
from discord import ui
from datetime import datetime

from view.yousure import YouSureView
from utility import Ticket
from helper.transcript import Transcript

class InactiveView(ui.View):
    def __init__(self, bot, message: Optional[discord.Message]=None):
        super().__init__(
            timeout=None
        )
        self.bot = bot
        self.closebutton = ui.Button(
            style=discord.ButtonStyle.green,
            custom_id="close_ticket",
            row=1,
            label="Resolved",
        )
        self.keepbutton = ui.Button(
            style=discord.ButtonStyle.gray,
            custom_id="keep_ticket",
            row=1,
            label="Not Resolved",
        )
        
        self.original_message: discord.Message | None = None
        if message is not None:
            self.original_message = message
        
        self.add_item(self.closebutton)
        self.add_item(self.keepbutton)
        
        self.closebutton.callback = self.close_callback
        self.keepbutton.callback = self.keep_callback
        
    async def close_callback(self, interaction: discord.Interaction):
        if self.original_message:
            await self.original_message.delete()
        for ticket in Ticket().get():
            if Ticket().get_ticket_channel_id(ticket) == interaction.channel.id:
                embed = discord.Embed(title="Resolve & Delete Ticket?", description="Are you sure you want to resolve & delete this Ticket?", color=discord.Color.red())
                await interaction.response.send_message(content="", embed=embed, view=YouSureView(self.bot, interaction.user.id, interaction, None), ephemeral=True)
                self.stop()
                return
        await interaction.response.send_message(content="Something went wrong, contact an administrator to delete this Ticket.", ephemeral=True, delete_after=3)
        
    async def keep_callback(self, interaction: discord.Interaction):
        tickets = Ticket().get()
        
        for ticket in Ticket().get():
            if Ticket().get_ticket_channel_id(ticket) == interaction.channel.id:
                t = tickets
                t[str(ticket)]["stale"] = False
                t[str(ticket)]["last_activity"] = datetime.now().timestamp()
                Transcript(f"configuration/{tickets[str(ticket)]["transcript"]}").append_as_system(f"{interaction.user.name} marked this ticket as Unresolved (Active)")
                if self.original_message:
                    await self.original_message.delete()
                self.stop()
                Ticket().save(t)
                return
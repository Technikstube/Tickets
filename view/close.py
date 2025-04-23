import discord
from typing import Optional
from discord import ui

from view.yousure import YouSureView
from utility import Ticket

class CloseView(ui.View):
    def __init__(self, bot, message: Optional[discord.Message]=None):
        super().__init__(
            timeout=None
        )
        self.bot = bot
        self.closebutton = ui.Button(
            style=discord.ButtonStyle.gray,
            custom_id="close_ticket",
            row=1,
            label="Close Ticket",
        )
        
        if message is not None:
            self.original_message = message
        
        self.add_item(self.closebutton)
        
        self.closebutton.callback = self.close_callback
        
    async def close_callback(self, interaction: discord.Interaction):
        for ticket in Ticket().get():
            if Ticket().get_ticket_channel_id(ticket) == interaction.channel.id:
                embed = discord.Embed(title="Delete Ticket", description="Are you sure you want to delete this ticket?", color=discord.Color.red())
                await interaction.response.send_message(content="", embed=embed, view=YouSureView(self.bot, interaction.user.id, interaction, None), ephemeral=True)
                self.stop()
                return
        await interaction.response.send_message(content="Something went wrong, contact an administrator to delete this Ticket.", ephemeral=True, delete_after=3)
        
        
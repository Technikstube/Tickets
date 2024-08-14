import discord
from discord import ui

from modal.start_ticket import StartTicketModal

class StartTicketView(ui.View):
    def __init__(self, bot):
        super().__init__(
            timeout=None
        )
        self.bot = bot
        self.startbutton = ui.Button(
            style=discord.ButtonStyle.green,
            emoji="<:helioscheckcircle:1267515445582237797>",
            custom_id="open_ticket",
            row=0,
            label="Ticket öffnen",
        )
        
        self.add_item(self.startbutton)
        
        self.startbutton.callback = self.start_callback
        
    async def start_callback(self, interaction: discord.Interaction):        
        await interaction.response.send_modal(StartTicketModal(self.bot))